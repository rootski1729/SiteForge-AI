from flask import request, jsonify
from app.api import api_bp
from app.middleware.auth_middleware import require_auth
from app.middleware.permission_middleware import require_permission
from app.services.gemini_service import GeminiService
from app.models.website import Website

@api_bp.route('/generate-website', methods=['POST'])
@require_auth
@require_permission('create_website')
def generate_website():
    try:
        data = request.get_json()
        
        required_fields = ['business_type', 'industry']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        business_type = data['business_type']
        industry = data['industry']
        company_name = data.get('company_name', 'Your Company')
        
        gemini_service = GeminiService()
        website_content = gemini_service.generate_website_content(
            business_type, industry, company_name)
        
        website = Website(
            title=f"{company_name} - {business_type}",
            content=website_content,
            owner_id=request.current_user['_id'],
            business_type=business_type,
            industry=industry,
            template_id='default')
        
        website_id = website.save()
        
        return jsonify({
            'message': 'Website generated successfully',
            'website_id': website_id,
            'content': website_content}), 201
        
    except Exception as e:
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
        if (user_role.get('name') != 'admin' and 
            str(website_data['owner_id']) != str(request.current_user['_id'])):
            return jsonify({'error': 'Access denied'}), 403
        
        gemini_service = GeminiService()
        new_content = gemini_service.generate_website_content(
            website_data['business_type'],
            website_data['industry'],
            website_data['title'].split(' - ')[0])
        
        Website.update_website(website_id, {'content': new_content})
        
        return jsonify({
            'message': 'Content regenerated successfully',
            'content': new_content}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500