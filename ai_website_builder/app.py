# Fixed app.py - Replace your current app.py with this

from flask import Flask, render_template, send_from_directory
from flask_pymongo import PyMongo
from config import config
import os

from app import create_app

# Create Flask app with correct template folder
app = Flask(__name__, template_folder='templates')
app.config.from_object(config['default'])

# Initialize MongoDB
mongo = PyMongo()
mongo.init_app(app)

# Register Blueprints
from app.auth import auth_bp
from app.api import api_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(api_bp, url_prefix='/api')

# Initialize MongoDB connection first
with app.app_context():
    try:
        # Test MongoDB connection
        mongo.db.command('ping')
        print("MongoDB connected successfully!")
        
        # Initialize default roles and admin user
        from app.models.role import Role
        from app.models.user import User
        Role.create_default_roles()
        User.create_admin_user()
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        print("Please check your MongoDB URI in config.py")

# Frontend Routes
@app.route('/')
def index():
    return '''
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
        <h1>🤖 AI Website Builder</h1>
        <p>Create stunning websites powered by AI</p>
        <div style="margin: 30px 0;">
            <a href="/login" style="background: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin-right: 15px;">Login</a>
            <a href="/register" style="background: #27ae60; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">Register</a>
        </div>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 30px;">
            <h3>Demo Account:</h3>
            <p><strong>Admin:</strong> admin@admin.com / admin123</p>
            <p>Or create your own account to get started!</p>
        </div>
    </div>
    '''

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/create-website')
def create_website_page():
    return render_template('create_website.html')

@app.route('/my-websites')
def my_websites_page():
    return render_template('my_websites.html')

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'AI Website Builder API is running'}

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)