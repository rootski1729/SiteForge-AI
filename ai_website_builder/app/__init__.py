# app/__init__.py

from flask import Flask
from flask_pymongo import PyMongo
from config import config

# ✅ Global mongo instance to be imported anywhere via: from app import mongo
mongo = PyMongo()

def create_app(config_name='default'):
    app = Flask(__name__, template_folder='app/templates')
    app.config.from_object(config[config_name])

    # ✅ Initialize MongoDB
    mongo.init_app(app)

    # ✅ Register Blueprints
    from app.auth import auth_bp
    from app.api import api_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    # ✅ Ensure DB connection is active before creating roles/users
    with app.app_context():
        try:
            mongo.db.command('ping')  # test DB
            print("MongoDB connected successfully!")
            from app.models.role import Role
            from app.models.user import User
            Role.create_default_roles()
            User.create_admin_user()
        except Exception as e:
            print(f"MongoDB error: {e}")

    return app
