from django.http import JsonResponse
from django.urls import resolve
import json

class RBACMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self.check_permission(request):
            return JsonResponse({
                'error': 'Permission denied',
                'message': 'You do not have permission to access this resource'
            }, status=403)

        response = self.get_response(request)
        return response

    def check_permission(self, request):
        skip_urls = [
            '/api/auth/login/',
            '/api/auth/register/',
            '/admin/',
            '/api/auth/verify-token/',]
        
        if any(request.path.startswith(url) for url in skip_urls):
            return True
        
        if not request.path.startswith('/api/'):
            return True
        
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return True
        
        try:
            resolved = resolve(request.path)
        except:
            return True
        
        permission_map = {
            'website_builder': {
                'resource': 'websites',
                'actions': {
                    'GET': 'read',
                    'POST': 'create',
                    'PUT': 'update',
                    'PATCH': 'update',
                    'DELETE': 'delete'}},
            'rbac': {
                'resource': 'roles',
                'actions': {
                    'GET': 'read',
                    'POST': 'create',
                    'PUT': 'update',
                    'PATCH': 'update',
                    'DELETE': 'delete'
                }
            }
        }
        
        app_name = resolved.app_name
        if app_name in permission_map:
            resource = permission_map[app_name]['resource']
            action = permission_map[app_name]['actions'].get(request.method, 'read')
            
            if request.user.role and request.user.role.name == 'Admin':
                return True
            return request.user.has_permission(resource, action)
        
        return True