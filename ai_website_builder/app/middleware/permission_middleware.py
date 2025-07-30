from functools import wraps
from flask import request, jsonify

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = request.current_user.get('role')
            if not user_role:
                return jsonify({'error': 'User role not found'}), 403
            
            user_permissions = user_role.get('permissions', [])
            
            if permission not in user_permissions:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = request.current_user.get('role')
            if not user_role or user_role.get('name') != role_name:
                return jsonify({'error': f'Role {role_name} required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator