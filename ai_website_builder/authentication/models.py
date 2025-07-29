# Create your models here.
from mongoengine import Document, EmbeddedDocument, fields
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime

class User(Document):
    username = fields.StringField(max_length=150, unique=True, required=True)
    email = fields.EmailField(unique=True, required=True)
    first_name = fields.StringField(max_length=30)
    last_name = fields.StringField(max_length=30)
    password = fields.StringField(max_length=128, required=True)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    role = fields.ReferenceField('rbac.Role', required=False)
    is_verified = fields.BooleanField(default=False)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'users',
        'indexes': ['email', 'username']
    }

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def has_permission(self, resource, action):
        if not self.role:
            return False
        return self.role.has_permission(resource, action)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)