"""
Database Models for Studymate Platform
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models
from .study_group import StudyGroup
from .user import User
from .resource import Resource
from .progress import Progress

__all__ = ['db', 'User', 'StudyGroup', 'Resource', 'Progress']
