# app/__init__.py - Final Fixed version

from flask import Flask
from flask_pymongo import PyMongo
from config import config
import os

# Global mongo instance
mongo = PyMongo()

def create_app(config_name='default'):
    # Get the absolute path to the templates directory
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(config[config_name])

    # Initialize MongoDB
    mongo.init_app(app)

    # Register Blueprints
    from app.auth import auth_bp
    from app.api import api_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Initialize database with default data
    with app.app_context():
        try:
            # Test MongoDB connection
            mongo.db.command('ping')
            print("✅ MongoDB connected successfully!")
            
            # Create default roles and admin user
            from app.models.role import Role
            from app.models.user import User
            Role.create_default_roles()
            User.create_admin_user()
            
        except Exception as e:
            print(f"❌ MongoDB error: {e}")
            print("Please check your MongoDB URI in config.py or .env file")

    return app