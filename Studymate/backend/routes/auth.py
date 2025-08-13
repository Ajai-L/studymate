#!/usr/bin/env python3
"""
Authentication Routes - User registration, login, logout
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import logging
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from models import User

bp = Blueprint('auth', __name__)
logger = logging.getLogger('studymate.auth')

@bp.route("/", methods=["GET"])
def info():
    return jsonify({"message": "Authentication routes active."}), 200

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json(force=True, silent=True)
    logger.info(f"Received data in /register: {data}")

    required_fields = ['name', 'email', 'password']
    missing = [field for field in required_fields if not data or field not in data or not data[field]]

    if missing:
        logger.warning(f"Missing required fields: {missing}")
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    try:
        # Check if user already exists
        if User.query.filter_by(username=data['name']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        # Create new user
        user = User(
            username=data['name'],
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            password_hash=generate_password_hash(data['password'])
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        logger.exception("Registration failed")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.get_json(silent=True)
    print("Received data in /login:", data)

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get current user profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': user.to_dict()}), 200


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json(silent=True)
    print("Received data in /profile update:", data)

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'bio' in data:
        user.bio = data['bio']

    user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'user': user.to_dict()}), 200


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token invalidation)"""
    return jsonify({'message': 'Logged out successfully'}), 200
