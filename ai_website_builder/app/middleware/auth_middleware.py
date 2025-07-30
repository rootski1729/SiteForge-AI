from functools import wraps
from flask import request, jsonify
from app.auth.utils import get_user_from_token

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1] 
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        current_user = get_user_from_token(token)
        if not current_user:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        request.current_user = current_user
        return f(*args, **kwargs)
    
    return decorated_function