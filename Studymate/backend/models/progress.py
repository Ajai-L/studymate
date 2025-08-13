#!/usr/bin/env python3
"""
Progress Model - Database schema for tracking user progress
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Progress(db.Model):
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    study_group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id'), nullable=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=True)
    study_time_minutes = db.Column(db.Integer, default=0)
    completed_tasks = db.Column(db.Integer, default=0)
    total_tasks = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='progress', lazy=True)
    study_group = db.relationship('StudyGroup', backref='progress', lazy=True)
    resource = db.relationship('Resource', backref='progress', lazy=True)
    
    def to_dict(self):
        """Convert progress object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'study_group_id': self.study_group_id,
            'resource_id': self.resource_id,
            'study_time_minutes': self.study_time_minutes,
            'completed_tasks': self.completed_tasks,
            'total_tasks': self.total_tasks,
            'notes': self.notes,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def completion_percentage(self):
        """Calculate completion percentage"""
        if self.total_tasks == 0:
            return 0
        return (self.completed_tasks / self.total_tasks) * 100
    
    def __repr__(self):
        return f'<Progress user_id={self.user_id} date={self.date}>'
