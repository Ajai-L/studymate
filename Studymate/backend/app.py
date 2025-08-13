#!/usr/bin/env python3
"""
Studymate - Backend API Server (updated)
- Robust imports with fallbacks for missing modules
- File upload endpoint (pdf)
- Placeholder /api/ask endpoint (connect FAISS/LLM later)
- Serves frontend static files if present
- Uses env vars (.env) and improved logging
"""

import os
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, Blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import logging

# Load environment variables from .env (if present)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
FRONTEND_DIR = BASE_DIR.parent / "frontend"  # ../frontend by default

# Ensure upload dir exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("studymate")

# Initialize Flask app
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="/")
CORS(app, resources={r"/api/*": {"origins": "*"}})  # tighten origins in prod

# Configuration (via env or defaults)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///studymate.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))

# Init extensions
jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, cors_allowed_origins="*")

# --------------------------
# Attempt to import models/routes; fallback to dummy blueprints
# --------------------------
def make_dummy_blueprint(name):
    bp = Blueprint(name, __name__)

    @bp.route("/", methods=["GET"])
    def info():
        return jsonify({"message": f"{name} blueprint placeholder"}), 200

    return bp

# Import models (if exist)
try:
    from models import User, StudyGroup, Resource, Progress  # noqa: F401
    logger.info("Imported models module.")
except Exception as e:
    logger.warning(f"Could not import models: {e}. Using dummy placeholders.")
    User = StudyGroup = Resource = Progress = None

# Import route blueprints (if present)
import_types = {
    "auth": "routes.auth",
    "study": "routes.study",
    "resources": "routes.resources",
    "groups": "routes.groups",
    "analytics": "routes.analytics"
}

for key, module_path in import_types.items():
    try:
        module = __import__(module_path, fromlist=['bp'])
        bp = getattr(module, "bp", None)
        if bp is None:
            raise ImportError(f"No 'bp' in {module_path}")
        app.register_blueprint(bp, url_prefix=f"/api/{key}")
        logger.info(f"Registered blueprint /api/{key} from {module_path}")
    except Exception as ex:
        logger.warning(f"Could not register blueprint {module_path}: {ex}. Registering placeholder.")
        app.register_blueprint(make_dummy_blueprint(key), url_prefix=f"/api/{key}")

# --------------------------
# Basic endpoints
# --------------------------
@app.route("/")
def index():
    # If frontend index exists, serve it; otherwise, return JSON
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return send_from_directory(str(FRONTEND_DIR), "index.html")
    return jsonify({
        "message": "Welcome to Studymate API",
        "version": "1.0.0",
        "status": "running"
    })

@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/api/docs")
def api_docs():
    return jsonify({
        "endpoints": {
            "auth": "/api/auth",
            "study": "/api/study",
            "resources": "/api/resources",
            "groups": "/api/groups",
            "analytics": "/api/analytics",
            "upload": "/api/upload (POST multipart/form-data)",
            "ask": "/api/ask (POST JSON)"
        }
    })

# --------------------------
# File upload endpoint (PDFs)
# --------------------------
ALLOWED_EXTENSIONS = {"pdf"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/upload", methods=["POST"])
def upload_pdfs():
    """
    Expects multipart/form-data with key 'files' (multiple allowed).
    Saves PDFs to backend/uploads and returns saved filenames.
    """
    if "files" not in request.files:
        return jsonify({"error": "No files part in request"}), 400

    files = request.files.getlist("files")
    saved = []
    for f in files:
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            dest = UPLOAD_DIR / filename
            # avoid overwrite by appending timestamp if exists
            if dest.exists():
                stem = dest.stem
                suffix = dest.suffix
                filename = f"{stem}_{int(datetime.utcnow().timestamp())}{suffix}"
                dest = UPLOAD_DIR / filename
            f.save(str(dest))
            saved.append({"original_name": f.filename, "saved_name": filename, "path": str(dest)})
            logger.info(f"Saved upload: {dest}")
        else:
            logger.warning(f"Rejected upload (invalid file): {f.filename if f else 'unknown'}")
    return jsonify({"saved": saved}), 201

# --------------------------
# Placeholder /api/ask endpoint
# --------------------------
@app.route("/api/ask", methods=["POST"])
def ask_question():
    """
    Accepts JSON: {"question": "...", "context": optional}
    Returns a placeholder response. Replace with FAISS search + LLM call.
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    question = data.get("question")
    context = data.get("context", None)
    if not question:
        return jsonify({"error": "Please provide a 'question' field"}), 400

    # TODO: Integrate FAISS retrieval and IBM Watsonx here
    # For now return a dummy answer with echoed question and a sample source list
    answer = {
        "question": question,
        "answer": f"(placeholder) I received your question: '{question}'. Connect FAISS + LLM to generate real answers.",
        "context_used": context or [],
        "sources": []  # fill with {"file": "paper.pdf", "page": 12, "snippet": "..."} later
    }
    return jsonify(answer), 200

# --------------------------
# Serve static frontend files if present
# --------------------------
@app.route("/<path:filename>")
def serve_frontend(filename):
    # Allow serving of static frontend files from FRONTEND_DIR
    if (FRONTEND_DIR / filename).exists():
        return send_from_directory(str(FRONTEND_DIR), filename)
    # fallback to app static folder
    if (BASE_DIR / filename).exists():
        return send_from_directory(str(BASE_DIR), filename)
    return jsonify({"error": "Not found"}), 404

# --------------------------
# Socket.IO events
# --------------------------
@socketio.on("connect")
def handle_connect():
    logger.info("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    logger.info("Client disconnected")

@socketio.on("join_room")
def handle_join_room(data):
    room = data.get("room")
    if room:
        socketio.enter_room(request.sid, room)
        emit("joined_room", {"room": room}, room=room)

@socketio.on("leave_room")
def handle_leave_room(data):
    room = data.get("room")
    if room:
        socketio.leave_room(request.sid, room)
        emit("left_room", {"room": room}, room=room)

@socketio.on("send_message")
def handle_send_message(data):
    room = data.get("room")
    message = data.get("message")
    if room and message:
        payload = {
            "room": room,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        emit("receive_message", payload, room=room)

# --------------------------
# Error handlers
# --------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.exception("Server error")
    return jsonify({"error": "Internal server error"}), 500

# --------------------------
# Entry point
# --------------------------
if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("1", "true", "yes")

    logger.info(f"Starting Studymate backend on {host}:{port} (debug={debug})")
    # use socketio.run so socket endpoints work
    socketio.run(app, host=host, port=port, debug=debug)
