from flask import Blueprint, request, jsonify
from models import db, User, StudyGroup, Resource, Progress

bp = Blueprint('analytics', __name__)

@bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard analytics data"""
    user_count = User.query.count()
    group_count = StudyGroup.query.count()
    resource_count = Resource.query.count()
    progress_count = Progress.query.count()
    
    return jsonify({
        'total_users': user_count,
        'total_groups': group_count,
        'total_resources': resource_count,
        'total_progress_entries': progress_count
    })

@bp.route('/user-progress/<int:user_id>', methods=['GET'])
def get_user_progress(user_id):
    """Get progress analytics for a specific user"""
    user = User.query.get_or_404(user_id)
    progress = Progress.query.filter_by(user_id=user_id).all()
    
    total_resources = len(progress)
    completed_resources = len([p for p in progress if p.completion_percentage == 100])
    average_completion = sum([p.completion_percentage for p in progress]) / total_resources if total_resources > 0 else 0
    
    return jsonify({
        'user_id': user_id,
        'total_resources': total_resources,
        'completed_resources': completed_resources,
        'average_completion': round(average_completion, 2),
        'progress_details': [{
            'resource_id': p.resource_id,
            'completion_percentage': p.completion_percentage,
            'last_accessed': p.last_accessed.isoformat()
        } for p in progress]
    })

@bp.route('/group-stats/<int:group_id>', methods=['GET'])
def get_group_stats(group_id):
    """Get analytics for a specific study group"""
    group = StudyGroup.query.get_or_404(group_id)
    
    # Get members of this group (assuming we have a relationship)
    # This is a placeholder - adjust based on actual model relationships
    member_count = 0  # Placeholder
    
    return jsonify({
        'group_id': group_id,
        'group_name': group.name,
        'member_count': member_count,
        'created_at': group.created_at.isoformat()
    })

@bp.route('/popular-resources', methods=['GET'])
def get_popular_resources():
    """Get most popular resources based on usage"""
    # Placeholder implementation - adjust based on actual usage tracking
    resources = Resource.query.limit(10).all()
    
    return jsonify([{
        'id': resource.id,
        'title': resource.title,
        'type': resource.type,
        'created_at': resource.created_at.isoformat()
    } for resource in resources])
