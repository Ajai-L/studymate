import os
import functools
from uuid import uuid4
from datetime import datetime
from flask import session, redirect, url_for, flash

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    ext = original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else "pdf"
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    return f"{timestamp}_{uuid4().hex}.{ext}"


def login_required(view_func):
    @functools.wraps(view_func)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(**kwargs)

    return wrapped_view