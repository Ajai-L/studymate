import os
from datetime import datetime
from io import BytesIO

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    send_file,
)
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from markupsafe import Markup, escape

from config import Config
from models import db, User, UploadedFile, ChatHistory, UserSettings
from utils import login_required, allowed_file, generate_unique_filename
from pdf_utils import extract_text_from_pdf
from ai import AIService


app = Flask(__name__)
app.config.from_object(Config)

# Register Jinja filter for nl2br

def jinja_nl2br(value: str) -> Markup:
    return Markup("<br>".join(escape(value).splitlines()))

app.jinja_env.filters["nl2br"] = jinja_nl2br

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Init extensions
csrf = CSRFProtect(app)
db.init_app(app)

# Lazy AI service
ai_service = AIService(model_path=app.config.get("GRANITE_MODEL_PATH"))


@app.before_first_request
def setup_database() -> None:
    with app.app_context():
        db.create_all()


@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").lower().strip()
    password = request.form.get("password", "")

    if not name or not email or not password:
        flash("All fields are required.", "danger")
        return redirect(url_for("signup"))

    existing = User.query.filter_by(email=email).first()
    if existing:
        flash("Email already registered.", "warning")
        return redirect(url_for("login"))

    password_hash = generate_password_hash(password)
    user = User(name=name, email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    # Create default settings row
    settings = UserSettings(user_id=user.id, preferred_exam=None, theme="light")
    db.session.add(settings)
    db.session.commit()

    flash("Account created. Please log in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").lower().strip()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    session["user_id"] = user.id
    flash("Logged in successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    files = UploadedFile.query.filter_by(user_id=user.id).order_by(UploadedFile.created_at.desc()).limit(10).all()
    return render_template("dashboard.html", user=user, recent_files=files)


@app.route("/update-profile", methods=["POST"])
@login_required
def update_profile():
    user = User.query.get(session["user_id"])
    name = request.form.get("name", "").strip()
    preferred_exam = request.form.get("preferred_exam", "").strip() or None
    password = request.form.get("password", "")

    if name:
        user.name = name
    if password:
        user.password_hash = generate_password_hash(password)

    # Ensure settings row exists
    settings = UserSettings.query.filter_by(user_id=user.id).first()
    if not settings:
        settings = UserSettings(user_id=user.id)
        db.session.add(settings)
    settings.preferred_exam = preferred_exam

    db.session.commit()

    flash("Profile updated.", "success")
    return redirect(url_for("dashboard"))


@app.route("/chat")
@login_required
def chat():
    user = User.query.get(session["user_id"])
    history = (
        ChatHistory.query.filter_by(user_id=user.id)
        .order_by(ChatHistory.created_at.asc())
        .limit(200)
        .all()
    )
    return render_template("chat.html", user=user, history=history)


@app.route("/upload-pdf", methods=["POST"])
@login_required
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    filename = secure_filename(file.filename)
    unique_name = generate_unique_filename(filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)

    file.save(save_path)
    size = os.path.getsize(save_path)

    text = extract_text_from_pdf(save_path)

    record = UploadedFile(
        user_id=session["user_id"],
        original_filename=filename,
        stored_filename=unique_name,
        path=save_path,
        size_bytes=size,
        extracted_text=text,
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "fileId": record.id,
        "originalFilename": record.original_filename,
        "storedFilename": record.stored_filename,
        "size": record.size_bytes,
        "hasExtractedText": bool(text),
    })


@app.route("/process-request", methods=["POST"])
@login_required
def process_request():
    data = request.get_json(silent=True) or {}

    action = data.get("action")  # summarize | flashcards | competitive | custom
    input_text = data.get("text", "").strip()
    file_id = data.get("fileId")
    exam_type = data.get("exam", "GATE").strip() or "GATE"

    # If file is provided, prefer its extracted text
    context_text = None
    related_file_id = None
    if file_id:
        file_rec = UploadedFile.query.filter_by(id=file_id, user_id=session["user_id"]).first()
        if file_rec and file_rec.extracted_text:
            context_text = file_rec.extracted_text
            related_file_id = file_rec.id

    try:
        # Record user message
        user_message_text = build_user_message_preview(action, input_text, exam_type, context_text)
        user_msg = ChatHistory(
            user_id=session["user_id"],
            role="user",
            content=user_message_text,
            related_file_id=related_file_id,
        )
        db.session.add(user_msg)
        db.session.commit()

        # Produce AI response
        if action == "summarize":
            if not (context_text or input_text):
                return jsonify({"error": "No input text or PDF content provided"}), 400
            output_text = ai_service.summarize_text(context_text or input_text)
        elif action == "flashcards":
            if not (context_text or input_text):
                return jsonify({"error": "No input text or PDF content provided"}), 400
            output_text = ai_service.generate_flashcards(context_text or input_text)
        elif action == "competitive":
            if not (context_text or input_text):
                return jsonify({"error": "No input text or PDF content provided"}), 400
            output_text = ai_service.generate_competitive_questions(context_text or input_text, exam_type=exam_type)
        else:  # custom
            if not (input_text or context_text):
                return jsonify({"error": "No prompt provided"}), 400
            output_text = ai_service.answer_custom_prompt(input_text, context_text=context_text)

        ai_msg = ChatHistory(
            user_id=session["user_id"],
            role="ai",
            content=output_text,
            related_file_id=related_file_id,
        )
        db.session.add(ai_msg)
        db.session.commit()

        return jsonify({
            "userMessageId": user_msg.id,
            "aiMessageId": ai_msg.id,
            "response": output_text,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<int:chat_id>")
@login_required
def download(chat_id: int):
    fmt = request.args.get("format", "txt").lower()
    message = ChatHistory.query.filter_by(id=chat_id, user_id=session["user_id"]).first()
    if not message:
        flash("Item not found.", "warning")
        return redirect(url_for("chat"))

    filename_base = f"studymate_output_{chat_id}"
    if fmt == "pdf":
        # Build a simple PDF via reportlab
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except Exception:
            flash("PDF generation dependency missing.", "danger")
            return redirect(url_for("chat"))

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        textobject = c.beginText(40, height - 40)
        lines = message.content.splitlines() or [message.content]
        for line in lines:
            # Wrap long lines manually (simple wrap)
            for chunk in wrap_text(line, max_chars=90):
                textobject.textLine(chunk)
        c.drawText(textobject)
        c.showPage()
        c.save()
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{filename_base}.pdf",
            mimetype="application/pdf",
        )
    else:
        return send_file(
            BytesIO(message.content.encode("utf-8")),
            as_attachment=True,
            download_name=f"{filename_base}.txt",
            mimetype="text/plain; charset=utf-8",
        )


def wrap_text(text: str, max_chars: int = 90):
    words = text.split()
    line = []
    count = 0
    for word in words:
        if count + len(word) + (1 if count > 0 else 0) > max_chars:
            yield " ".join(line)
            line = [word]
            count = len(word)
        else:
            line.append(word)
            count += len(word) + (1 if count > 0 else 0)
    if line:
        yield " ".join(line)


def build_user_message_preview(action: str, input_text: str, exam_type: str, context_text: str | None) -> str:
    prefix = {
        "summarize": "Summarize",
        "flashcards": "Generate flashcards",
        "competitive": f"Generate {exam_type} MCQs",
        "custom": "Custom prompt",
    }.get(action or "custom", "Custom prompt")

    snippet = (context_text or input_text or "").strip()
    if len(snippet) > 400:
        snippet = snippet[:400] + "..."
    if action == "custom":
        return f"{prefix}: {input_text.strip()[:400]}"
    return f"{prefix} from content: {snippet}"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)