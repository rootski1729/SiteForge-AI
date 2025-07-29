from rest_framework import serializers
from .models import Role, Permission, RoleAssignment
from authentication.models import User

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = '__all__'

    def get_users_count(self, obj):
        return obj.user_set.count()

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids)
            instance.permissions.set(permissions)
        
        return instance

class RoleAssignmentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_email = serializers.CharField(source='assigned_by.email', read_only=True)

    class Meta:
        model = RoleAssignment
        fields = '__all__'

class UserRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(write_only=True)
    current_role = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'current_role', 'role_name')
        read_only_fields = ('id', 'email', 'username', 'first_name', 'last_name', 'current_role')

    def update(self, instance, validated_data):
        role_name = validated_data.get('role_name')
        if role_name:
            try:
                role = Role.objects.get(name=role_name)
                instance.role = role
                instance.save()
            except Role.DoesNotExist:
                raise serializers.ValidationError(f"Role '{role_name}' does not exist")
        return instance