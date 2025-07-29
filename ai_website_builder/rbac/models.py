from django.db import models

# Create your models here.
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

class Permission(Document):
    name = fields.StringField(max_length=100, unique=True, required=True)
    codename = fields.StringField(max_length=100, unique=True, required=True)
    resource = fields.StringField(max_length=50, required=True)
    action = fields.StringField(max_length=50, required=True) 
    description = fields.StringField()
    created_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'permissions',
        'indexes': [
            ('resource', 'action'),
            'codename'
        ]
    }

    def __str__(self):
        return f"{self.resource}.{self.action}"

class Role(Document):
    name = fields.StringField(max_length=50, unique=True, required=True)
    description = fields.StringField()
    permissions = fields.ListField(fields.ReferenceField(Permission))
    is_default = fields.BooleanField(default=False)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'roles',
        'indexes': ['name']
    }

    def __str__(self):
        return self.name

    def has_permission(self, resource, action):
        for permission in self.permissions:
            if permission.resource == resource and permission.action == action:
                return True
        return False

    def get_permissions_list(self):
        return [(p.resource, p.action) for p in self.permissions]

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

class RoleAssignment(Document):
    user = fields.ReferenceField('authentication.User', required=True)
    role = fields.ReferenceField(Role, required=True)
    assigned_by = fields.ReferenceField('authentication.User', required=False)
    assigned_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'role_assignments',
        'indexes': [
            ('user', 'role'), 
        ]
    }

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"