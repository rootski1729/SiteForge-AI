from flask import request, jsonify, render_template_string
from app.api import api_bp
from app.middleware.auth_middleware import require_auth
from app.middleware.permission_middleware import require_permission
from app.models.website import Website
from bson.objectid import ObjectId
from bson.errors import InvalidId

def serialize_object_id(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, ObjectId):
                obj[key]=str(value)
            elif isinstance(value, dict):
                serialize_object_id(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        serialize_object_id(item)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                serialize_object_id(item)
    return obj

def validate_object_id(obj_id):
    """Validate if string is a valid ObjectId"""
    try:
        ObjectId(obj_id)
        return True
    except (InvalidId, TypeError):
        return False

@api_bp.route('/websites', methods=['GET'])
@require_auth
@require_permission('read_website')
def get_websites():
    try:
        user_role=request.current_user.get('role', {})
        user_id=request.current_user['_id']
        
        if user_role.get('name') == 'admin':
            websites=Website.get_all_websites()
        elif user_role.get('name') == 'viewer':
            websites=Website.get_published_websites()
            print(f"[DEBUG] Viewer {user_id} retrieved {len(websites)} published websites")
        else:
            websites=Website.find_by_owner(user_id)
        websites=serialize_object_id(websites)
        
        print(f"[DEBUG] Retrieved {len(websites)} websites for user role: {user_role.get('name')}")
        return jsonify({'websites': websites}), 200
        
    except Exception as e:
        print(f"Error in get_websites: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/websites/published', methods=['GET'])
def get_published_websites_public():
    try:
        websites=Website.get_published_websites()
        
        websites=serialize_object_id(websites)
        
        print(f"[DEBUG] Retrieved {len(websites)} published websites for public access")
        return jsonify({'websites': websites}), 200
        
    except Exception as e:
        print(f"Error in get_published_websites_public: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/websites/<website_id>', methods=['GET'])
@require_auth
@require_permission('read_website')
def get_website(website_id):
    try:
        if not validate_object_id(website_id):
            return jsonify({'error': 'Invalid website ID format'}), 400
        
        website_data=Website.find_by_id(website_id)
        if not website_data:
            return jsonify({'error': f'Website with ID {website_id} not found'}), 404
        
        user_role=request.current_user.get('role', {})
        current_user_id=str(request.current_user['_id'])
        website_owner_id=str(website_data['owner_id'])
        
        if user_role.get('name') == 'admin':

            pass
        elif user_role.get('name') == 'viewer':
            if not website_data.get('is_published', False):
                return jsonify({'error': 'Access denied - website not published'}), 403
        else:
            if website_owner_id != current_user_id:
                return jsonify({'error': 'Access denied - not your website'}), 403
        
        website_data=serialize_object_id(website_data)
        
        return jsonify({'website': website_data}), 200
        
    except Exception as e:
        print(f"Error in get_website: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/websites/<website_id>', methods=['PUT'])
@require_auth
@require_permission('update_website')
def update_website(website_id):
    try:
        print(f"[DEBUG] Updating website with ID: {website_id}")
        
        if not validate_object_id(website_id):
            print(f"[ERROR] Invalid ObjectId format: {website_id}")
            return jsonify({
                'error': 'Invalid website ID format',
                'provided_id': website_id,
                'valid_format': 'ObjectId must be 24 characters long and contain only hexadecimal characters'}), 400
        
        website_data=Website.find_by_id(website_id)
        if not website_data:
            print(f"[ERROR] Website not found in database: {website_id}")
            return jsonify({
                'error': f'Website with ID {website_id} not found',
                'provided_id': website_id,
                'suggestion': 'The website may have been deleted or the ID is incorrect'}), 404
        
        user_role=request.current_user.get('role', {})
        current_user_id=str(request.current_user['_id'])
        website_owner_id=str(website_data['owner_id'])
        
        print(f"[DEBUG] User: {current_user_id}, Owner: {website_owner_id}, Role: {user_role.get('name')}")
        
        if user_role.get('name') == 'viewer':
            return jsonify({
                'error': 'Access denied - viewers cannot edit websites',
                'reason': 'Viewers have read-only access to published websites'}), 403
        elif user_role.get('name') != 'admin' and website_owner_id != current_user_id:
            return jsonify({
                'error': 'Access denied',
                'reason': 'You can only edit your own websites'}), 403
        
        data=request.get_json()
        if not data:
            return jsonify({'error': 'No data provided in request body'}), 400
        
        print(f"[DEBUG] Update data: {data}")
        
        update_data={}
        allowed_fields=['title', 'content', 'is_published', 'template_id']
        
        for field in allowed_fields:
            if field in data:
                update_data[field]=data[field]
        
        if not update_data:
            return jsonify({
                'error': 'No valid fields to update',
                'allowed_fields': allowed_fields,
                'provided_fields': list(data.keys())
            }), 400
        
        print(f"[DEBUG] Validated update data: {update_data}")
        
        result=Website.update_website(website_id, update_data)
        
        if result.modified_count == 0:
            print(f"[WARNING] No documents were modified for website ID: {website_id}")
            if not Website.find_by_id(website_id):
                return jsonify({
                    'error': 'Website was deleted during the update process',
                    'website_id': website_id}), 404
        
        print(f"[DEBUG] Website updated successfully: {website_id}")
        return jsonify({
            'message': 'Website updated successfully',
            'website_id': website_id,
            'updated_fields': list(update_data.keys())}), 200
        
    except Exception as e:
        print(f"Error in update_website: {str(e)}")
        return jsonify({
            'error': 'Internal server error during update',
            'details': str(e),
            'website_id': website_id
        }), 500

@api_bp.route('/websites/<website_id>', methods=['DELETE'])
@require_auth
@require_permission('delete_website')
def delete_website(website_id):
    try:
        if not validate_object_id(website_id):
            return jsonify({'error': 'Invalid website ID format'}), 400
        
        website_data=Website.find_by_id(website_id)
        if not website_data:
            return jsonify({'error': f'Website with ID {website_id} not found'}), 404
        
        user_role=request.current_user.get('role', {})
        current_user_id=str(request.current_user['_id'])
        if user_role.get('name') == 'viewer':
            return jsonify({'error': 'Access denied - viewers cannot delete websites'}), 403
        elif (user_role.get('name') != 'admin' and 
            str(website_data['owner_id']) != current_user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        Website.delete_website(website_id)
        return jsonify({'message': 'Website deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error in delete_website: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/preview/<website_id>')
def preview_website(website_id):
    try:
        if not validate_object_id(website_id):
            return "Invalid website ID format", 400
        
        website_data=Website.find_by_id(website_id)
        if not website_data:
            return "Website not found", 404
        
        if not website_data.get('is_published', False):
            return "Website not published", 403
        
        content=website_data.get('content', {})
        if isinstance(content, str):
            return f"<html><body><h1>{website_data.get('title', 'Website')}</h1><div>{content}</div></body></html>"
        
        template="""
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
                    <h1>{{ hero_title }}</h1>
                    <p>{{ hero_subtitle }}</p>
                    <a href="#contact" class="btn">{{ hero_cta }}</a>
                </div>
            </section>
            
            <!-- About Section -->
            <section class="section">
                <div class="container">
                    <h2>{{ about_title }}</h2>
                    <p>{{ about_content }}</p>
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
                    <h2>{{ contact_title }}</h2>
                    <p>{{ contact_content }}</p>
                </div>
            </section>
        </body>
        </html>
        """
        
        hero=content.get('hero', {})
        about=content.get('about', {})
        services=content.get('services', [])
        contact=content.get('contact', {})
        
        return render_template_string(template, 
                                    title=website_data.get('title', 'Website'),
                                    hero_title=hero.get('title', 'Welcome'),
                                    hero_subtitle=hero.get('subtitle', 'Professional website'),
                                    hero_cta=hero.get('cta_text', 'Get Started'),
                                    about_title=about.get('title', 'About Us'),
                                    about_content=about.get('content', 'Learn more about our business.'),
                                    services=services,
                                    contact_title=contact.get('title', 'Contact Us'),
                                    contact_content=contact.get('content', 'Get in touch with us today.'))
        
    except Exception as e:
        print(f"Error in preview_website: {str(e)}")
        return f"Error: {str(e)}", 500