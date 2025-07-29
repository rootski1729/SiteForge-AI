from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.WebsiteListCreateView.as_view(), name='website-list-create'),
    path('<uuid:pk>/', views.WebsiteDetailView.as_view(), name='website-detail'),
    path('<uuid:pk>/publish/', views.WebsitePublishView.as_view(), name='website-publish'),
    path('<uuid:website_pk>/sections/', views.WebsiteSectionListCreateView.as_view(), name='website-section-list'),
    path('<uuid:website_pk>/sections/<int:pk>/', views.WebsiteSectionDetailView.as_view(), name='website-section-detail'),
    path('<uuid:website_pk>/images/', views.WebsiteImageListCreateView.as_view(), name='website-image-list'),
    path('<uuid:website_pk>/images/<int:pk>/', views.WebsiteImageDetailView.as_view(), name='website-image-detail'),
    path('<uuid:website_id>/preview/', views.website_preview, name='website-preview'),
    path('generate-content/', views.generate_website_content, name='generate-content'),
    path('<uuid:website_id>/analytics/', views.website_analytics, name='website-analytics'),
    path('my-websites/', views.my_websites, name='my-websites'),
    path('<uuid:website_id>/clone/', views.clone_website, name='clone-website'),]