from flask import request, jsonify, render_template_string
from app.api import api_bp
from app.middleware.auth_middleware import require_auth
from app.middleware.permission_middleware import require_permission
from app.models.website import Website
from bson.objectid import ObjectId

@api_bp.route('/websites', methods=['GET'])
@require_auth
@require_permission('read_website')
def get_websites():
    try:
        user_role = request.current_user.get('role', {})
        
        if user_role.get('name') == 'admin':
            websites = Website.get_all_websites()
        else:
            websites = Website.find_by_owner(request.current_user['_id'])
        for website in websites:
            website['_id'] = str(website['_id'])
            website['owner_id'] = str(website['owner_id'])
        
        return jsonify({'websites': websites}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/websites/<website_id>', methods=['GET'])
@require_auth
@require_permission('read_website')
def get_website(website_id):
    try:
        website_data = Website.find_by_id(website_id)
        if not website_data:
            return jsonify({'error': 'Website not found'}), 404
        
        user_role = request.current_user.get('role', {})
        if (user_role.get('name') not in ['admin', 'viewer'] and 
            str(website_data['owner_id']) != str(request.current_user['_id'])):
            return jsonify({'error': 'Access denied'}), 403
        
        website_data['_id'] = str(website_data['_id'])
        website_data['owner_id'] = str(website_data['owner_id'])
        
        return jsonify({'website': website_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/websites/<website_id>', methods=['PUT'])
@require_auth
@require_permission('update_website')
def update_website(website_id):
    try:
        website_data = Website.find_by_id(website_id)
        if not website_data:
            return jsonify({'error': 'Website not found'}), 404
        
        user_role = request.current_user.get('role', {})
        if (user_role.get('name') != 'admin' and 
            str(website_data['owner_id']) != str(request.current_user['_id'])):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        update_data = {}
        
        allowed_fields = ['title', 'content', 'is_published', 'template_id']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            Website.update_website(website_id, update_data)
            return jsonify({'message': 'Website updated successfully'}), 200
        else:
            return jsonify({'error': 'No valid fields to update'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/websites/<website_id>', methods=['DELETE'])
@require_auth
@require_permission('delete_website')
def delete_website(website_id):
    try:
        website_data = Website.find_by_id(website_id)
        if not website_data:
            return jsonify({'error': 'Website not found'}), 404
        
        user_role = request.current_user.get('role', {})
        if (user_role.get('name') != 'admin' and 
            str(website_data['owner_id']) != str(request.current_user['_id'])):
            return jsonify({'error': 'Access denied'}), 403
        
        Website.delete_website(website_id)
        return jsonify({'message': 'Website deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/preview/<website_id>')
def preview_website(website_id):
    try:
        website_data = Website.find_by_id(website_id)
        if not website_data:
            return "Website not found", 404
        
        if not website_data.get('is_published', False):
            return "Website not published", 403
        
        content = website_data.get('content', {})
        
        template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ title }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; line-height: 1.6; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 0; text-align: center; }
                .hero h1 { font-size: 3em; margin-bottom: 20px; }
                .hero p { font-size: 1.2em; margin-bottom: 30px; }
                .btn { background: #ff6b6b; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }
                .section { padding: 60px 0; }
                .services { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 30px; }
                .service-card { background: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center; }
                .contact { background: #f8f9fa; }
            </style>
        </head>
        <body>
            <!-- Hero Section -->
            <section class="hero">
                <div class="container">
                    <h1>{{ hero.title }}</h1>
                    <p>{{ hero.subtitle }}</p>
                    <a href="#contact" class="btn">{{ hero.cta_text }}</a>
                </div>
            </section>
            
            <!-- About Section -->
            <section class="section">
                <div class="container">
                    <h2>{{ about.title }}</h2>
                    <p>{{ about.content }}</p>
                </div>
            </section>
            
            <!-- Services Section -->
            <section class="section">
                <div class="container">
                    <h2>Our Services</h2>
                    <div class="services">
                        {% for service in services %}
                        <div class="service-card">
                            <h3>{{ service.title }}</h3>
                            <p>{{ service.description }}</p>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </section>
            
            <!-- Contact Section -->
            <section class="section contact" id="contact">
                <div class="container">
                    <h2>{{ contact.title }}</h2>
                    <p>{{ contact.content }}</p>
                </div>
            </section>
        </body>
        </html>
        """
        
        return render_template_string(template, 
                                    title=website_data.get('title', 'Website'),
                                    hero=content.get('hero', {}),
                                    about=content.get('about', {}),
                                    services=content.get('services', []),
                                    contact=content.get('contact', {}))
        
    except Exception as e:
        return f"Error: {str(e)}", 500