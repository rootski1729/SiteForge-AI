from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from .models import User
from rbac.models import Role

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role_name = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        if User.objects(email=attrs['email']).first():
            raise serializers.ValidationError("Email already exists")
        
        if User.objects(username=attrs['username']).first():
            raise serializers.ValidationError("Username already exists")
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        role_name = validated_data.pop('role_name', 'Viewer')
        
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        
        try:
            role = Role.objects(name=role_name).first()
            if role:
                user.role = role
        except:
            pass
            
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = User.objects(email=email).first()
            if not user or not user.check_password(password):
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must provide email and password')
        
        return attrs

class UserSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role_name = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    def get_role_name(self, obj):
        return obj.role.name if obj.role else None

class UserProfileSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role_info = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    
    def get_role_info(self, obj):
        if obj.role:
            return {
                'id': str(obj.role.id),
                'name': obj.role.name,
                'description': obj.role.description
            }
        return None
    
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance