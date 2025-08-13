#!/usr/bin/env python3
"""
Resource Model - Database schema for study resources
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Resource(db.Model):
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file_url = db.Column(db.String(500))
    file_type = db.Column(db.String(50))
    category = db.Column(db.String(100))
    tags = db.Column(db.String(500))
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    study_group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploader = db.relationship('User', backref='uploaded_resources', lazy=True)
    study_group = db.relationship('StudyGroup', backref='resources', lazy=True)
    
    def to_dict(self):
        """Convert resource object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'category': self.category,
            'tags': self.tags,
            'uploader_id': self.uploader_id,
            'study_group_id': self.study_group_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Resource {self.title}>'
