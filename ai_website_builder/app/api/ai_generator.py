from flask import request, jsonify
from app.api import api_bp
from app.middleware.auth_middleware import require_auth
from app.middleware.permission_middleware import require_permission
from app.services.gemini_service import GeminiService
from app.models.website import Website
from bson.objectid import ObjectId

def serialize_object_id(obj):
    """Convert ObjectId to string in MongoDB documents"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, ObjectId):
                obj[key] = str(value)
            elif isinstance(value, dict):
                serialize_object_id(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        serialize_object_id(item)
    return obj

@api_bp.route('/generate-website', methods=['POST'])
@require_auth
@require_permission('create_website')
def generate_website():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['business_type', 'industry']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        business_type = data['business_type']
        industry = data['industry']
        company_name = data.get('company_name', 'Your Company')
        
        # Get current user ID
        current_user_id = request.current_user['_id']
        
        try:
            # Try to generate content with AI
            gemini_service = GeminiService()
            website_content = gemini_service.generate_website_content(
                business_type, industry, company_name)
        except Exception as ai_error:
            print(f"AI generation failed: {ai_error}")
            # Fall back to default content if AI fails
            website_content = {
                "hero": {
                    "title": f"Welcome to {company_name}",
                    "subtitle": f"Your trusted partner in {industry}",
                    "cta_text": "Get Started"
                },
                "about": {
                    "title": "About Us",
                    "content": f"We are a leading {business_type} company specializing in {industry}. Our team is dedicated to providing excellent service and innovative solutions."
                },
                "services": [
                    {
                        "title": "Professional Service",
                        "description": f"Expert {business_type} services tailored to your needs."
                    },
                    {
                        "title": "Quality Solutions",
                        "description": "High-quality solutions designed to meet your requirements."
                    },
                    {
                        "title": "Customer Support",
                        "description": "Dedicated support to ensure your success."
                    }
                ],
                "contact": {
                    "title": "Get In Touch",
                    "content": "Contact us today to learn how we can help your business grow."
                }
            }
        
        website = Website(
            title=f"{company_name} - {business_type}",
            content=website_content,
            owner_id=current_user_id,
            business_type=business_type,
            industry=industry,
            template_id='default')
        
        website_id = website.save()
        
        return jsonify({
            'message': 'Website generated successfully',
            'website_id': website_id,
            'content': website_content
        }), 201
        
    except Exception as e:
        print(f"Error in generate_website: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/regenerate-content/<website_id>', methods=['POST'])
@require_auth
@require_permission('update_website')
def regenerate_content(website_id):
    try:
        website_data = Website.find_by_id(website_id)
        if not website_data:
            return jsonify({'error': 'Website not found'}), 404
        
        user_role = request.current_user.get('role', {})
        current_user_id = str(request.current_user['_id'])
        
        # Check permissions
        if (user_role.get('name') != 'admin' and 
            str(website_data['owner_id']) != current_user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        try:
            # Try to regenerate with AI
            gemini_service = GeminiService()
            new_content = gemini_service.generate_website_content(
                website_data['business_type'],
                website_data['industry'],
                website_data['title'].split(' - ')[0] if ' - ' in website_data['title'] else website_data['title'])
        except Exception as ai_error:
            print(f"AI regeneration failed: {ai_error}")
            # Fall back to updated default content
            company_name = website_data['title'].split(' - ')[0] if ' - ' in website_data['title'] else website_data['title']
            new_content = {
                "hero": {
                    "title": f"Welcome to {company_name}",
                    "subtitle": f"Refreshed content for your {website_data['business_type']} business",
                    "cta_text": "Discover More"
                },
                "about": {
                    "title": "About Our Company",
                    "content": f"We continue to lead in {website_data['industry']} with innovative {website_data['business_type']} solutions. Our commitment to excellence drives everything we do."
                },
                "services": [
                    {
                        "title": "Premium Services",
                        "description": f"Top-tier {website_data['business_type']} services for discerning clients."
                    },
                    {
                        "title": "Innovation Focus", 
                        "description": "Cutting-edge solutions that set industry standards."
                    },
                    {
                        "title": "Expert Support",
                        "description": "Professional guidance from industry experts."
                    }
                ],
                "contact": {
                    "title": "Connect With Us",
                    "content": "Ready to experience the difference? Get in touch today."
                }
            }
        
        Website.update_website(website_id, {'content': new_content})
        
        return jsonify({
            'message': 'Content regenerated successfully',
            'content': new_content
        }), 200
        
    except Exception as e:
        print(f"Error in regenerate_content: {str(e)}")
        return jsonify({'error': str(e)}), 500