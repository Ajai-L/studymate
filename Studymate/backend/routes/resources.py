from flask import Blueprint, request, jsonify
from models import db, Resource, User

bp = Blueprint('resources', __name__)

@bp.route('/', methods=['GET'])
def get_resources():
    """Get all resources"""
    resources = Resource.query.all()
    return jsonify([{
        'id': resource.id,
        'title': resource.title,
        'description': resource.description,
        'type': resource.type,
        'url': resource.url,
        'created_at': resource.created_at.isoformat()
    } for resource in resources])

@bp.route('/', methods=['POST'])
def create_resource():
    """Create a new resource"""
    data = request.get_json()
    
    resource = Resource(
        title=data.get('title'),
        description=data.get('description', ''),
        type=data.get('type', 'document'),
        url=data.get('url'),
        created_by=data.get('created_by')
    )
    
    db.session.add(resource)
    db.session.commit()
    
    return jsonify({
        'id': resource.id,
        'title': resource.title,
        'description': resource.description,
        'type': resource.type,
        'url': resource.url,
        'created_at': resource.created_at.isoformat()
    }), 201

@bp.route('/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    """Get a specific resource"""
    resource = Resource.query.get_or_404(resource_id)
    return jsonify({
        'id': resource.id,
        'title': resource.title,
        'description': resource.description,
        'type': resource.type,
        'url': resource.url,
        'created_at': resource.created_at.isoformat()
    })

@bp.route('/<int:resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """Update a resource"""
    resource = Resource.query.get_or_404(resource_id)
    data = request.get_json()
    
    resource.title = data.get('title', resource.title)
    resource.description = data.get('description', resource.description)
    resource.type = data.get('type', resource.type)
    resource.url = data.get('url', resource.url)
    
    db.session.commit()
    
    return jsonify({
        'id': resource.id,
        'title': resource.title,
        'description': resource.description,
        'type': resource.type,
        'url': resource.url,
        'created_at': resource.created_at.isoformat()
    })

@bp.route('/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    """Delete a resource"""
    resource = Resource.query.get_or_404(resource_id)
    db.session.delete(resource)
    db.session.commit()
    return jsonify({'message': 'Resource deleted successfully'})
