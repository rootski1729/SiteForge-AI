# Fixed app.py - Replace your current app.py with this

from flask import render_template
from app import create_app
import os

# Create the Flask app using the factory pattern
app = create_app()

# Health check route (can be moved to a separate blueprint if needed)
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'AI Website Builder API is running'}

# Frontend Routes - Move these to a separate blueprint for better organization
@app.route('/')
def index():
    return '''
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
        <h1>AI Website Builder</h1>
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)