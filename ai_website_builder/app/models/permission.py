from app import mongo
from bson.objectid import ObjectId
from datetime import datetime

class Permission:
    # Available permissions in the system
    PERMISSIONS = [
        'create_website',
        'read_website', 
        'update_website',
        'delete_website',
        'manage_users',
        'manage_roles',
        'manage_permissions'
    ]
    
    @staticmethod
    def get_all_permissions():
        return Permission.PERMISSIONS
    
    @staticmethod
    def is_valid_permission(permission):
        return permission in Permission.PERMISSIONS