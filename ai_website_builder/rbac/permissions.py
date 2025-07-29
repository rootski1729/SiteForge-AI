from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role and 
            request.user.role.name == 'Admin')

class IsAdminOrEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role and 
            request.user.role.name in ['Admin', 'Editor'])

class HasPermission(permissions.BasePermission):
    def __init__(self, resource, action):
        self.resource = resource
        self.action = action

    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.has_permission(self.resource, self.action))

class ResourcePermission(permissions.BasePermission):
    resource_name = None
    
    def get_required_permission(self, request, view):
        method_permission_map = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',}
        
        action = method_permission_map.get(request.method, 'read')
        return self.resource_name, action

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(view, 'resource_name'):
            return True
        
        resource, action = self.get_required_permission(request, view)
        return request.user.has_permission(resource, action)

class WebsitePermission(ResourcePermission):
    resource_name = 'websites'

class UserManagementPermission(ResourcePermission):
    resource_name = 'users'

class RoleManagementPermission(ResourcePermission):
    resource_name = 'roles'