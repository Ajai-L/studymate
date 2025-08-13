"""
API Routes for Studymate Platform
"""

from .auth import bp as auth_bp
from .study import bp as study_bp
from .resources import bp as resources_bp
from .groups import bp as groups_bp
from .analytics import bp as analytics_bp

__all__ = ['auth_bp', 'study_bp', 'resources_bp', 'groups_bp', 'analytics_bp']
