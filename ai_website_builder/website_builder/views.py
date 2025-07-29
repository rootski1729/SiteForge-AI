from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q

from .models import *
from .serializers import *
from .ai_service import AIWebsiteGenerator, ContentOptimizer
from rbac.permissions import IsAdminOrEditor, WebsitePermission

class WebsiteListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WebsiteCreateSerializer
        return WebsiteListSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role and user.role.name == 'Admin':
            return Website.objects.all()
        return Website.objects.filter(owner=user)
    
    def perform_create(self, serializer):
        website = serializer.save()
        business_name = getattr(website, '_business_name', '')
        ai_generator = AIWebsiteGenerator()
        try:
            ai_content = ai_generator.generate_website_content(
                website.business_type,
                website.industry,
                business_name or website.title
            )
            ai_content = ContentOptimizer.optimize_meta_tags(ai_content)
            ai_content = ContentOptimizer.validate_content_structure(ai_content)
            website.hero_title = ai_content.get('hero_title', '')
            website.hero_subtitle = ai_content.get('hero_subtitle', '')
            website.about_section = ai_content.get('about_section', '')
            website.services_section = ai_content.get('services', [])
            website.contact_info = ai_content.get('contact_info', {})
            website.meta_title = ai_content.get('meta_title', '')
            website.meta_description = ai_content.get('meta_description', '')
            website.meta_keywords = ai_content.get('meta_keywords', '')
            layout_data = ai_generator.generate_layout_structure(
                website.template_type, 
                ai_content
            )
            website.layout_data = layout_data
            website.save()
            self._create_default_sections(website, ai_content)
        except Exception as e:
            print(f"AI Generation Error: {str(e)}")
    
    def _create_default_sections(self, website, ai_content):
        default_sections = [
            {
                'section_type': 'hero',
                'title': ai_content.get('hero_title', ''),
                'content': ai_content.get('hero_subtitle', ''),
                'data': {'cta_text': 'Get Started', 'cta_link': '#contact'},
                'order': 1
            },
            {
                'section_type': 'about',
                'title': 'About Us',
                'content': ai_content.get('about_section', ''),
                'data': {},
                'order': 2
            },
            {
                'section_type': 'services',
                'title': 'Our Services',
                'content': '',
                'data': {'services': ai_content.get('services', [])},
                'order': 3
            },
            {
                'section_type': 'contact',
                'title': 'Contact Us',
                'content': 'Get in touch with us today',
                'data': ai_content.get('contact_info', {}),
                'order': 4
            }
        ]
        for section_data in default_sections:
            WebsiteSection.objects.create(website=website, **section_data)

class WebsiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Website.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return WebsiteUpdateSerializer
        return WebsiteDetailSerializer
    
    def get_object(self):
        website = get_object_or_404(Website, pk=self.kwargs['pk'])
        user = self.request.user
        if user.role and user.role.name == 'Admin':
            return website
        if website.owner != user:
            self.permission_denied(self.request, "You don't have permission to access this website")
        return website
    
    def perform_destroy(self, instance):
        if not instance.can_delete(self.request.user):
            self.permission_denied(self.request, "You don't have permission to delete this website")
        instance.delete()

class WebsitePublishView(generics.UpdateAPIView):
    queryset = Website.objects.all()
    serializer_class = WebsitePublishSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        website = get_object_or_404(Website, pk=self.kwargs['pk'])
        if not website.can_edit(self.request.user):
            self.permission_denied(self.request, "You don't have permission to publish this website")
        return website
    
    def perform_update(self, serializer):
        website = serializer.save()
        if website.status == 'published' and not website.published_at:
            website.published_at = timezone.now()
            website.save()

class WebsiteSectionListCreateView(generics.ListCreateAPIView):
    serializer_class = WebsiteSectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        website = get_object_or_404(Website, pk=self.kwargs['website_pk'])
        user = self.request.user
        if user.role and user.role.name == 'Admin':
            return website.sections.all()
        if website.owner != user:
            self.permission_denied(self.request, "You don't have permission to access this website")
        return website.sections.all()
    
    def perform_create(self, serializer):
        website = get_object_or_404(Website, pk=self.kwargs['website_pk'])
        if not website.can_edit(self.request.user):
            self.permission_denied(self.request, "You don't have permission to edit this website")
        serializer.save(website=website)

class WebsiteSectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WebsiteSectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        website = get_object_or_404(Website, pk=self.kwargs['website_pk'])
        section = get_object_or_404(WebsiteSection, pk=self.kwargs['pk'], website=website)
        user = self.request.user
        if user.role and user.role.name == 'Admin':
            return section
        if website.owner != user:
            self.permission_denied(self.request, "You don't have permission to access this website")
        return section

class WebsiteImageListCreateView(generics.ListCreateAPIView):
    serializer_class = WebsiteImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        website = get_object_or_404(Website, pk=self.kwargs['website_pk'])
        user = self.request.user
        if user.role and user.role.name == 'Admin':
            return website.images.all()
        if website.owner != user:
            self.permission_denied(self.request, "You don't have permission to access this website")
        return website.images.all()
    
    def perform_create(self, serializer):
        website = get_object_or_404(Website, pk=self.kwargs['website_pk'])
        if not website.can_edit(self.request.user):
            self.permission_denied(self.request, "You don't have permission to edit this website")
        serializer.save(website=website)

class WebsiteImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WebsiteImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        website = get_object_or_404(Website, pk=self.kwargs['website_pk'])
        image = get_object_or_404(WebsiteImage, pk=self.kwargs['pk'], website=website)
        user = self.request.user
        if user.role and user.role.name == 'Admin':
            return image
        if website.owner != user:
            self.permission_denied(self.request, "You don't have permission to access this website")
        return image

def website_preview(request, website_id):
    website = get_object_or_404(Website, pk=website_id)
    user = request.user
    if user.is_authenticated:
        if user.role and user.role.name == 'Admin':
            pass
        elif website.owner != user and not user.has_permission('websites', 'read'):
            return HttpResponse('Permission denied', status=403)
    else:
        if website.status != 'published':
            return HttpResponse('Website not found', status=404)
    sections = website.sections.filter(is_visible=True).order_by('order')
    images = website.images.all().order_by('order')
    context = {
        'website': website,
        'sections': sections,
        'images': images,
        'hero_title': website.hero_title,
        'hero_subtitle': website.hero_subtitle,
        'about_section': website.about_section,
        'services': website.services_section,
        'contact_info': website.contact_info,
    }
    if website.status == 'published':
        analytics, created = WebsiteAnalytics.objects.get_or_create(
            website=website,
            date=timezone.now().date(),
            defaults={'page_views': 0, 'unique_visitors': 0}
        )
        analytics.page_views += 1
        analytics.save()
    return render(request, 'preview/website_template.html', context)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsAdminOrEditor])
def generate_website_content(request):
    serializer = AIGenerationRequestSerializer(data=request.data)
    if serializer.is_valid():
        business_type = serializer.validated_data['business_type']
        industry = serializer.validated_data['industry']
        business_name = serializer.validated_data.get('business_name', '')
        template_type = serializer.validated_data.get('template_type', 'business')
        ai_generator = AIWebsiteGenerator()
        try:
            ai_content = ai_generator.generate_website_content(business_type, industry, business_name)
            layout_data = ai_generator.generate_layout_structure(template_type, ai_content)
            ai_content = ContentOptimizer.optimize_meta_tags(ai_content)
            ai_content = ContentOptimizer.validate_content_structure(ai_content)
            return Response({
                'content': ai_content,
                'layout': layout_data,
                'message': 'Content generated successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to generate content',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def website_analytics(request, website_id):
    website = get_object_or_404(Website, pk=website_id)
    user = request.user
    if user.role and user.role.name == 'Admin':
        pass
    elif website.owner != user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    analytics = WebsiteAnalytics.objects.filter(website=website).order_by('-date')[:30]
    total_views = sum(a.page_views for a in analytics)
    total_visitors = sum(a.unique_visitors for a in analytics)
    return Response({
        'website_id': website_id,
        'total_page_views': total_views,
        'total_unique_visitors': total_visitors,
        'daily_analytics': [
            {
                'date': a.date,
                'page_views': a.page_views,
                'unique_visitors': a.unique_visitors,
                'bounce_rate': a.bounce_rate
            }
            for a in analytics
        ]
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_websites(request):
    user = request.user
    websites = Website.objects.filter(owner=user).order_by('-created_at')
    serializer = WebsiteListSerializer(websites, many=True)
    return Response({
        'count': websites.count(),
        'websites': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def clone_website(request, website_id):
    original_website = get_object_or_404(Website, pk=website_id)
    user = request.user
    if user.role and user.role.name == 'Admin':
        pass
    elif original_website.owner != user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    cloned_website = Website.objects.create(
        title=f"{original_website.title} (Copy)",
        description=original_website.description,
        business_type=original_website.business_type,
        industry=original_website.industry,
        template_type=original_website.template_type,
        hero_title=original_website.hero_title,
        hero_subtitle=original_website.hero_subtitle,
        about_section=original_website.about_section,
        services_section=original_website.services_section,
        contact_info=original_website.contact_info,
        layout_data=original_website.layout_data,
        custom_css=original_website.custom_css,
        custom_js=original_website.custom_js,
        owner=user,
        status='draft',
        meta_title=original_website.meta_title,
        meta_description=original_website.meta_description,
        meta_keywords=original_website.meta_keywords
    )
    for section in original_website.sections.all():
        WebsiteSection.objects.create(
            website=cloned_website,
            section_type=section.section_type,
            title=section.title,
            content=section.content,
            data=section.data,
            order=section.order,
            is_visible=section.is_visible
        )
    serializer = WebsiteDetailSerializer(cloned_website)
    return Response({
        'message': 'Website cloned successfully',
        'website': serializer.data
    }, status=status.HTTP_201_CREATED)
