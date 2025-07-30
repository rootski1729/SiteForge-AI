from functools import wraps
from flask import request, jsonify
from app.auth.utils import get_user_from_token

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            token = None
            auth_header = request.headers.get('Authorization')
            
            if auth_header:
                try:
                    # Extract token from "Bearer <token>" format
                    token = auth_header.split(" ")[1] 
                except IndexError:
                    return jsonify({'error': 'Invalid token format. Use: Bearer <token>'}), 401
            
            if not token:
                return jsonify({'error': 'Token is missing. Please provide Authorization header.'}), 401
            
            current_user = get_user_from_token(token)
            if not current_user:
                return jsonify({'error': 'Token is invalid or expired'}), 401
            
            # Check if user is active
            if not current_user.get('is_active', True):
                return jsonify({'error': 'Account is deactivated'}), 401
            
            # Attach user to request object
            request.current_user = current_user
            return f(*args, **kwargs)
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function