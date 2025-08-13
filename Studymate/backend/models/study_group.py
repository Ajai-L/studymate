#!/usr/bin/env python3
"""
Study Group Model - Database schema for study groups
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StudyGroup(db.Model):
    __tablename__ = 'study_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = db.relationship('User', backref='owned_groups', lazy=True)
    members = db.relationship('User', secondary='group_members', backref='study_groups', lazy=True)
    resources = db.relationship('Resource', backref='group', lazy=True)
    progress = db.relationship('Progress', backref='group', lazy=True)
    
    def to_dict(self):
        """Convert study group object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<StudyGroup {self.name}>'
