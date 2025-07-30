from app import mongo
from bson.objectid import ObjectId
from datetime import datetime, timezone

class Role:
    def __init__(self, name, description, permissions=None):
        self.name = name
        self.description = description
        self.permissions = permissions or []
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def save(self):
        role_data = {
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        result = mongo.db.roles.insert_one(role_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(role_id):
        return mongo.db.roles.find_one({'_id': ObjectId(role_id)})
    
    @staticmethod
    def find_by_name(name):
        return mongo.db.roles.find_one({'name': name})
    
    @staticmethod
    def get_all_roles():
        return list(mongo.db.roles.find({}))
    
    @staticmethod
    def update_role(role_id, data):
        data['updated_at'] = datetime.now(timezone.utc)
        return mongo.db.roles.update_one(
            {'_id': ObjectId(role_id)},
            {'$set': data}
        )
    
    @staticmethod
    def delete_role(role_id):
        return mongo.db.roles.delete_one({'_id': ObjectId(role_id)})
    
    @staticmethod
    def create_default_roles():
        default_roles = [
            {
                'name': 'admin',
                'description': 'Full access to all resources',
                'permissions': ['create_website', 'read_website', 'update_website', 'delete_website', 
                            'manage_users', 'manage_roles', 'manage_permissions']},
            {
                'name': 'editor',
                'description': 'Can create and edit websites',
                'permissions': ['create_website', 'read_website', 'update_website']},
            {
                'name': 'viewer',
                'description': 'Can only view websites',
                'permissions': ['read_website']}]

        for role_data in default_roles:
            if not mongo.db.roles.find_one({'name': role_data['name']}):
                role_data['created_at'] = datetime.now(timezone.utc)
                role_data['updated_at'] = datetime.now(timezone.utc)
                mongo.db.roles.insert_one(role_data)
                print(f"Created default role: {role_data['name']}")