from flask import Blueprint, request, jsonify
from models import db, StudyGroup, User

bp = Blueprint('groups', __name__)

@bp.route('/', methods=['GET'])
def get_groups():
    """Get all groups"""
    groups = StudyGroup.query.all()
    return jsonify([{
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'created_at': group.created_at.isoformat()
    } for group in groups])

@bp.route('/', methods=['POST'])
def create_group():
    """Create a new group"""
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

@bp.route('/<int:group_id>', methods=['GET'])
def get_group(group_id):
    """Get a specific group"""
    group = StudyGroup.query.get_or_404(group_id)
    return jsonify({
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'created_at': group.created_at.isoformat()
    })

@bp.route('/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    """Update a group"""
    group = StudyGroup.query.get_or_404(group_id)
    data = request.get_json()
    
    group.name = data.get('name', group.name)
    group.description = data.get('description', group.description)
    
    db.session.commit()
    
    return jsonify({
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'created_at': group.created_at.isoformat()
    })

@bp.route('/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    """Delete a group"""
    group = StudyGroup.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    return jsonify({'message': 'Group deleted successfully'})
