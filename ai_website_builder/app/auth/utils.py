import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app
from app.models.user import User
from app.models.role import Role

def generate_token(user_id):
    payload={
        'user_id': user_id,
        'exp': datetime.now(timezone.utc)
        + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    try:
        payload=jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_from_token(token):
    payload=decode_token(token)
    if payload:
        user_data=User.find_by_id(payload['user_id'])
        if user_data:
            role_data=Role.find_by_id(user_data['role_id'])
            user_data['role']=role_data
            return user_data
    return None