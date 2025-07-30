from functools import wraps
from flask import request, jsonify

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if not hasattr(request, 'current_user'):
                    return jsonify({'error': 'Authentication required'}), 401
                
                user_role = request.current_user.get('role')
                if not user_role:
                    return jsonify({'error': 'User role not found'}), 403
                
                user_permissions = user_role.get('permissions', [])
                
                if permission not in user_permissions:
                    return jsonify({
                        'error': f'Insufficient permissions. Required: {permission}',
                        'user_permissions': user_permissions}), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                print(f"Permission check error: {str(e)}")
                return jsonify({'error': 'Permission check failed'}), 500
        return decorated_function
    return decorator

def require_role(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if not hasattr(request, 'current_user'):
                    return jsonify({'error': 'Authentication required'}), 401
                
                user_role = request.current_user.get('role')
                if not user_role or user_role.get('name') != role_name:
                    current_role = user_role.get('name', 'unknown') if user_role else 'none'
                    return jsonify({
                        'error': f'Role {role_name} required. Current role: {current_role}'}), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                print(f"Role check error: {str(e)}")
                return jsonify({'error': 'Role check failed'}), 500
        return decorated_function
    return decorator