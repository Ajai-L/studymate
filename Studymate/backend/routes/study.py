from flask import Blueprint, request, jsonify
from models import db, User, StudyGroup, Resource, Progress

bp = Blueprint('study', __name__)

@bp.route('/groups', methods=['GET'])
def get_study_groups():
    """Get all study groups"""
    groups = StudyGroup.query.all()
    return jsonify([{
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'created_at': group.created_at.isoformat()
    } for group in groups])

@bp.route('/groups', methods=['POST'])
def create_study_group():
    """Create a new study group"""
    data = request.get_json()
    
    group = StudyGroup(
        name=data.get('name'),
        description=data.get('description', ''),
        created_by=data.get('created_by')
    )
    
    db.session.add(group)
    db.session.commit()
    
    return jsonify({
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'created_at': group.created_at.isoformat()
    }), 201

@bp.route('/progress', methods=['GET'])
def get_progress():
    """Get user progress"""
    user_id = request.args.get('user_id')
    if user_id:
        progress = Progress.query.filter_by(user_id=user_id).all()
    else:
        progress = Progress.query.all()
    
    return jsonify([{
        'id': p.id,
        'user_id': p.user_id,
        'resource_id': p.resource_id,
        'completion_percentage': p.completion_percentage,
        'last_accessed': p.last_accessed.isoformat()
    } for p in progress])
