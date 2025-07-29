from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from authentication.models import User
from .models import Role, Permission, RoleAssignment
from .serializers import *
from .permissions import IsAdmin


class PermissionListView(generics.ListCreateAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        return Permission.objects()

class PermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAdmin]
    
    def get_object(self):
        try:
            return Permission.objects(id=self.kwargs['pk']).first()
        except:
            from django.http import Http404
            raise Http404
class RoleListView(generics.ListCreateAPIView):
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        return Role.objects()

class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]
    
    def get_object(self):
        try:
            return Role.objects(id=self.kwargs['pk']).first()
        except:
            from django.http import Http404
            raise Http404

class UserListView(generics.ListAPIView):
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        return User.objects()

class UserRoleUpdateView(generics.UpdateAPIView):
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdmin]
    
    def get_object(self):
        try:
            return User.objects(id=self.kwargs['pk']).first()
        except:
            from django.http import Http404
            raise Http404

@api_view(['POST'])
@permission_classes([IsAdmin])
def assign_role(request):
    user_id = request.data.get('user_id')
    role_id = request.data.get('role_id')
    
    try:
        user = User.objects(id=user_id).first()
        role = Role.objects(id=role_id).first()
        
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if not role:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.role = role
        user.save()
        assignment = RoleAssignment.objects(user=user, role=role).first()
        if not assignment:
            assignment = RoleAssignment(user=user, role=role, assigned_by=request.user)
            assignment.save()
        
        return Response({
            'message': f'Role {role.name} assigned to {user.email} successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdmin])
def initialize_default_roles(request):
    permissions_data = [
        {'name': 'Create Website', 'codename': 'create_website', 'resource': 'websites', 'action': 'create'},
        {'name': 'Read Website', 'codename': 'read_website', 'resource': 'websites', 'action': 'read'},
        {'name': 'Update Website', 'codename': 'update_website', 'resource': 'websites', 'action': 'update'},
        {'name': 'Delete Website', 'codename': 'delete_website', 'resource': 'websites', 'action': 'delete'},
        
        {'name': 'Create User', 'codename': 'create_user', 'resource': 'users', 'action': 'create'},
        {'name': 'Read User', 'codename': 'read_user', 'resource': 'users', 'action': 'read'},
        {'name': 'Update User', 'codename': 'update_user', 'resource': 'users', 'action': 'update'},
        {'name': 'Delete User', 'codename': 'delete_user', 'resource': 'users', 'action': 'delete'},
        
        {'name': 'Create Role', 'codename': 'create_role', 'resource': 'roles', 'action': 'create'},
        {'name': 'Read Role', 'codename': 'read_role', 'resource': 'roles', 'action': 'read'},
        {'name': 'Update Role', 'codename': 'update_role', 'resource': 'roles', 'action': 'update'},
        {'name': 'Delete Role', 'codename': 'delete_role', 'resource': 'roles', 'action': 'delete'},]
    
    permissions = []
    for perm_data in permissions_data:
        permission = Permission.objects(codename=perm_data['codename']).first()
        if not permission:
            permission = Permission(**perm_data)
            permission.save()
        permissions.append(permission)
    
    admin_role = Role.objects(name='Admin').first()
    if not admin_role:
        admin_role = Role(
            name='Admin',
            description='Full access to all resources',
            is_default=False)
    admin_role.permissions = permissions
    admin_role.save()
    
    editor_permissions = Permission.objects(resource='websites')
    editor_role = Role.objects(name='Editor').first()
    if not editor_role:
        editor_role = Role(
            name='Editor',
            description='Can create and edit websites',
            is_default=False)
    editor_role.permissions = list(editor_permissions)
    editor_role.save()
    
    viewer_permissions = Permission.objects(action='read')
    viewer_role = Role.objects(name='Viewer').first()
    if not viewer_role:
        viewer_role = Role(
            name='Viewer',
            description='Read-only access to websites',
            is_default=True)
    viewer_role.permissions = list(viewer_permissions)
    viewer_role.save()
    
    return Response({
        'message': 'Default roles and permissions initialized successfully'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_permissions(request):
    if not request.user.role:
        return Response({'permissions': []}, status=status.HTTP_200_OK)
    
    user_permissions = request.user.role.permissions
    
    permissions_data = []
    for perm in user_permissions:
        permissions_data.append({
            'id': str(perm.id),
            'name': perm.name,
            'codename': perm.codename,
            'resource': perm.resource,
            'action': perm.action,
            'description': perm.description})
    
    return Response({
        'role': request.user.role.name,
        'permissions': permissions_data
    }, status=status.HTTP_200_OK)