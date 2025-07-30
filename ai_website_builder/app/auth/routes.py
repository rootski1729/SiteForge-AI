from flask import request, jsonify, current_app
from app.auth import auth_bp
from app.models.user import User
from app.models.role import Role
from app.auth.utils import generate_token
import re

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data=request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        email_pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Invalid email format'}), 400

        if User.find_by_email(data['email']):
            return jsonify({'error': 'User already exists'}), 409

        viewer_role=Role.find_by_name('viewer')
        if not viewer_role:
            return jsonify({'error': 'Default role not found'}), 500

        user=User(data['email'], data['password'], viewer_role['_id'])
        user_id=user.save()

        token=generate_token(user_id)

        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user_id': user_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data=request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        user_data=User.find_by_email(data['email'])
        if not user_data:
            return jsonify({'error': 'Invalid credentials'}), 401

        user=User(user_data['email'], '')
        user.password_hash=user_data['password_hash']

        if not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user_data.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 401

        token=generate_token(str(user_data['_id']))

        role_data=Role.find_by_id(user_data['role_id'])

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user_data['_id']),
                'email': user_data['email'],
                'role': role_data['name'] if role_data else 'viewer'
            }}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
