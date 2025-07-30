from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
from datetime import timezone

class User:
    def __init__(self, email, password, role_id=None, is_active=True):
        self.email = email
        self.password_hash = self.hash_password(password)
        self.role_id = role_id
        self.is_active = is_active
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def save(self):
        user_data = {
            'email': self.email,
            'password_hash': self.password_hash,
            'role_id': self.role_id,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        result = mongo.db.users.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({'email': email})
    
    @staticmethod
    def find_by_id(user_id):
        return mongo.db.users.find_one({'_id': ObjectId(user_id)})
    
    @staticmethod
    def get_all_users():
        return list(mongo.db.users.find({}))
    
    @staticmethod
    def update_user_role(user_id, role_id):
        return mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'role_id': ObjectId(role_id),
                    'updated_at': datetime.now(timezone.utc),
                }
            },
        )
    
    @staticmethod
    def delete_user(user_id):
        return mongo.db.users.delete_one({'_id': ObjectId(user_id)})
    
    @staticmethod
    def create_admin_user():
        admin_role = mongo.db.roles.find_one({'name': 'admin'})
        if admin_role and not mongo.db.users.find_one({'email': 'admin@admin.com'}):
            admin_user = User('admin@admin.com', 'admin123', admin_role['_id'])
            admin_user.save()
            print("Default admin user created: admin@admin.com / admin123")