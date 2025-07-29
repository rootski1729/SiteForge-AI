from django.urls import path
from . import views

urlpatterns = [
    path('permissions/', views.PermissionListView.as_view(), name='permission-list'),
    path('permissions/<int:pk>/', views.PermissionDetailView.as_view(), name='permission-detail'),
    path('roles/', views.RoleListView.as_view(), name='role-list'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role-detail'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/role/', views.UserRoleUpdateView.as_view(), name='user-role-update'),
    path('assign-role/', views.assign_role, name='assign-role'),
    path('initialize/', views.initialize_default_roles, name='initialize-roles'),
    path('my-permissions/', views.my_permissions, name='my-permissions'),]