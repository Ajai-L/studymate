import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), 'studymate.db'))}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads")),
    )
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 32 * 1024 * 1024))  # 32 MB
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_TIME_LIMIT = None

    # AI Model config
    GRANITE_MODEL_PATH = os.environ.get(
        "GRANITE_MODEL_PATH", "ibm-granite/granite-3.3-8b-instruct"
    )
    GRANITE_MAX_NEW_TOKENS = int(os.environ.get("GRANITE_MAX_NEW_TOKENS", 512))
    GRANITE_TEMPERATURE = float(os.environ.get("GRANITE_TEMPERATURE", 0.2))
    GRANITE_TOP_P = float(os.environ.get("GRANITE_TOP_P", 0.95))