from django.db import models

# Create your models here.
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime
import uuid

class Website(Document):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),]
    
    TEMPLATE_CHOICES = [
        ('business', 'Business Template'),
        ('portfolio', 'Portfolio Template'),
        ('restaurant', 'Restaurant Template'),
        ('blog', 'Blog Template'),
        ('ecommerce', 'E-commerce Template'),]
    
    id = fields.StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    title = fields.StringField(max_length=200, required=True)
    description = fields.StringField()
    business_type = fields.StringField(max_length=100, required=True)
    industry = fields.StringField(max_length=100, required=True)
    template_type = fields.StringField(max_length=50, choices=TEMPLATE_CHOICES, default='business')
    
    hero_title = fields.StringField(max_length=200)
    hero_subtitle = fields.StringField()
    about_section = fields.StringField()
    services_section = fields.ListField(fields.DictField())
    contact_info = fields.DictField()
    
    layout_data = fields.DictField() 
    custom_css = fields.StringField()
    custom_js = fields.StringField()
    owner = fields.ReferenceField('authentication.User', required=True)
    status = fields.StringField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_ai_generated = fields.BooleanField(default=True)
    meta_title = fields.StringField(max_length=200)
    meta_description = fields.StringField()
    meta_keywords = fields.StringField(max_length=500)

    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    published_at = fields.DateTimeField()
    
    meta = {
        'collection': 'websites',
        'indexes': [
            '-created_at',
            'owner',
            'status']}
    
    def __str__(self):
        return self.title
    
    def is_owner_check(self, user):
        return str(self.owner.id) == str(user.id)
    
    def can_edit(self, user):
        if user.role and user.role.name == 'Admin':
            return True
        return self.is_owner_check(user) and user.has_permission('websites', 'update')
    
    def can_delete(self, user):
        if user.role and user.role.name == 'Admin':
            return True
        return self.is_owner_check(user) and user.has_permission('websites', 'delete')

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

class WebsiteSection(Document):
    SECTION_TYPES = [
        ('hero', 'Hero Section'),
        ('about', 'About Section'),
        ('services', 'Services Section'),
        ('portfolio', 'Portfolio Section'),
        ('testimonials', 'Testimonials Section'),
        ('contact', 'Contact Section'),
        ('footer', 'Footer Section'),
        ('custom', 'Custom Section'),]
    
    website = fields.ReferenceField(Website, required=True)
    section_type = fields.StringField(max_length=50, choices=SECTION_TYPES, required=True)
    title = fields.StringField(max_length=200)
    content = fields.StringField()
    data = fields.DictField()
    order = fields.IntField(default=0)
    is_visible = fields.BooleanField(default=True)
    
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'website_sections',
        'indexes': [
            'website',
            'order',
            ('website', 'section_type')]}
    
    def __str__(self):
        return f"{self.website.title} - {dict(self.SECTION_TYPES).get(self.section_type, self.section_type)}"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

class WebsiteImage(Document):
    website = fields.ReferenceField(Website, required=True)
    image_url = fields.URLField()
    image_file = fields.FileField()
    alt_text = fields.StringField(max_length=200)
    caption = fields.StringField(max_length=500)
    order = fields.IntField(default=0)
    
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'website_images',
        'indexes': [
            'website',
            'order']}
    
    def __str__(self):
        return f"{self.website.title} - Image {self.order}"
    
    @property
    def image_source(self):
        if self.image_url:
            return self.image_url
        elif self.image_file:
            return self.image_file.url
        return None

class WebsiteAnalytics(Document):
    website = fields.ReferenceField(Website, required=True)
    page_views = fields.IntField(default=0)
    unique_visitors = fields.IntField(default=0)
    bounce_rate = fields.FloatField(default=0.0)
    avg_session_duration = fields.IntField()
    date = fields.DateTimeField(required=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'website_analytics',
        'indexes': [
            ('website', 'date'),  
            '-date']}
    
    def __str__(self):
        return f"{self.website.title} - {self.date.strftime('%Y-%m-%d')}"