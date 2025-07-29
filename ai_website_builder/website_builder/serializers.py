from rest_framework import serializers
from .models import *
from authentication.serializers import UserSerializer

class WebsiteImageSerializer(serializers.ModelSerializer):
    image_source = serializers.ReadOnlyField()
    
    class Meta:
        model = WebsiteImage
        fields = '__all__'
        read_only_fields = ('website',)

class WebsiteSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteSection
        fields = '__all__'
        read_only_fields = ('website',)

class WebsiteListSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    sections_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Website
        fields = [
            'id', 'title', 'description', 'business_type', 'industry', 
            'template_type', 'status', 'owner_name', 'sections_count',
            'created_at', 'updated_at', 'published_at']
    
    def get_sections_count(self, obj):
        return obj.sections.count()

class WebsiteDetailSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    sections = WebsiteSectionSerializer(many=True, read_only=True)
    images = WebsiteImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Website
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')

class WebsiteCreateSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Website
        fields = [
            'title', 'description', 'business_type', 'industry', 
            'template_type', 'business_name']
    
    def create(self, validated_data):
        business_name = validated_data.pop('business_name', '')
        validated_data['owner'] = self.context['request'].user
        
        website = Website.objects.create(**validated_data)
        website._business_name = business_name
        
        return website

class WebsiteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = [
            'title', 'description', 'hero_title', 'hero_subtitle',
            'about_section', 'services_section', 'contact_info',
            'layout_data', 'custom_css', 'custom_js', 'status',
            'meta_title', 'meta_description', 'meta_keywords']

class WebsitePublishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ['status']
    
    def validate_status(self, value):
        if value not in ['published', 'draft', 'archived']:
            raise serializers.ValidationError("Invalid status")
        return value

class WebsiteAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteAnalytics
        fields = '__all__'
        read_only_fields = ('website',)

class AIGenerationRequestSerializer(serializers.Serializer):
    business_type = serializers.CharField(max_length=100)
    industry = serializers.CharField(max_length=100)
    business_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    template_type = serializers.ChoiceField(
        choices=Website.TEMPLATE_CHOICES,
        default='business')
    
    def validate_business_type(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Business type must be at least 2 characters long")
        return value.strip()
    
    def validate_industry(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Industry must be at least 2 characters long")
        return value.strip()