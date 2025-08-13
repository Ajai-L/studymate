from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy in app.py via db.init_app(app)
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    settings = db.relationship("UserSettings", backref="user", uselist=False, cascade="all, delete-orphan")
    files = db.relationship("UploadedFile", backref="user", lazy=True, cascade="all, delete-orphan")
    messages = db.relationship("ChatHistory", backref="user", lazy=True, cascade="all, delete-orphan")


class UploadedFile(db.Model):
    __tablename__ = "uploaded_files"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(1024), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    extracted_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class ChatHistory(db.Model):
    __tablename__ = "chat_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = db.Column(db.String(16), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)
    related_file_id = db.Column(db.Integer, db.ForeignKey("uploaded_files.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    preferred_exam = db.Column(db.String(64), nullable=True)  # e.g., GATE, JEE, NEET
    theme = db.Column(db.String(32), nullable=True, default="light")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)