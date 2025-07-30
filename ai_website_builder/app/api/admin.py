from flask import request, jsonify
from app.api import api_bp
from app.middleware.auth_middleware import require_auth
from app.middleware.permission_middleware import require_role
from app.models.user import User
from app.models.role import Role
from app.models.website import Website
from bson.objectid import ObjectId

# User Management Routes
@api_bp.route('/admin/users', methods=['GET'])
@require_auth
@require_role('admin')
def get_all_users():
    try:
        users = User.get_all_users()
        
        # Get role information for each user
        for user in users:
            user['_id'] = str(user['_id'])
            if user.get('role_id'):
                role_data = Role.find_by_id(user['role_id'])
                user['role'] = role_data['name'] if role_data else 'unknown'
            else:
                user['role'] = 'no_role'
            # Remove password hash from response
            user.pop('password_hash', None)
        
        return jsonify({'users': users}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/users/<user_id>/role', methods=['PUT'])
@require_auth
@require_role('admin')
def update_user_role(user_id):
    try:
        data = request.get_json()
        role_id = data.get('role_id')
        
        if not role_id:
            return jsonify({'error': 'role_id is required'}), 400
        
        # Verify role exists
        role_data = Role.find_by_id(role_id)
        if not role_data:
            return jsonify({'error': 'Role not found'}), 404
        
        # Verify user exists
        user_data = User.find_by_id(user_id)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        # Update user role
        User.update_user_role(user_id, role_id)
        
        return jsonify({'message': 'User role updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/users/<user_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def delete_user(user_id):
    try:
        # Prevent admin from deleting themselves
        if str(request.current_user['_id']) == user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        user_data = User.find_by_id(user_id)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        User.delete_user(user_id)
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Role Management Routes
@api_bp.route('/admin/roles', methods=['GET'])
@require_auth
@require_role('admin')
def get_all_roles():
    try:
        roles = Role.get_all_roles()
        
        for role in roles:
            role['_id'] = str(role['_id'])
        
        return jsonify({'roles': roles}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/roles', methods=['POST'])
@require_auth
@require_role('admin')
def create_role():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'description', 'permissions']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if role name already exists
        if Role.find_by_name(data['name']):
            return jsonify({'error': 'Role name already exists'}), 409
        
        role = Role(data['name'], data['description'], data['permissions'])
        role_id = role.save()
        
        return jsonify({
            'message': 'Role created successfully',
            'role_id': role_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/roles/<role_id>', methods=['PUT'])
@require_auth
@require_role('admin')
def update_role(role_id):
    try:
        data = request.get_json()
        
        role_data = Role.find_by_id(role_id)
        if not role_data:
            return jsonify({'error': 'Role not found'}), 404
        
        # Prevent modifying default roles
        if role_data['name'] in ['admin', 'editor', 'viewer']:
            return jsonify({'error': 'Cannot modify default roles'}), 400
        
        update_data = {}
        allowed_fields = ['description', 'permissions']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            Role.update_role(role_id, update_data)
            return jsonify({'message': 'Role updated successfully'}), 200
        else:
            return jsonify({'error': 'No valid fields to update'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/roles/<role_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def delete_role(role_id):
    try:
        role_data = Role.find_by_id(role_id)
        if not role_data:
            return jsonify({'error': 'Role not found'}), 404
        
        # Prevent deleting default roles
        if role_data['name'] in ['admin', 'editor', 'viewer']:
            return jsonify({'error': 'Cannot delete default roles'}), 400
        
        Role.delete_role(role_id)
        return jsonify({'message': 'Role deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard Statistics
@api_bp.route('/admin/dashboard', methods=['GET'])
@require_auth
@require_role('admin')
def admin_dashboard():
    try:
        # Get statistics
        total_users = len(User.get_all_users())
        total_websites = len(Website.get_all_websites())
        published_websites = len(Website.get_published_websites())
        total_roles = len(Role.get_all_roles())
        
        return jsonify({
            'statistics': {
                'total_users': total_users,
                'total_websites': total_websites,
                'published_websites': published_websites,
                'total_roles': total_roles
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500