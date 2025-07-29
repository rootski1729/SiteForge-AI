import google.generativeai as genai
import json
from django.conf import settings
from typing import Dict, List, Any
import re

class AIWebsiteGenerator:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_website_content(self, business_type: str, industry: str, business_name: str = "") -> Dict[str, Any]:
        """Generate website content using Gemini API"""
        
        prompt = self._create_content_prompt(business_type, industry, business_name)
        
        try:
            response = self.model.generate_content(prompt)
            
            if response.text:
                return self._parse_ai_response(response.text)
            else:
                return self._get_fallback_content(business_type, industry, business_name)
            
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return self._get_fallback_content(business_type, industry, business_name)
    
    def _create_content_prompt(self, business_type: str, industry: str, business_name: str) -> str:
        """Create a detailed prompt for content generation"""
        
        business_name_text = f" called '{business_name}'" if business_name else ""
        
        return f"""
        Create website content for a {business_type} business{business_name_text} in the {industry} industry.
        
        You must respond with ONLY a valid JSON object in the following exact format (no additional text, no markdown formatting, no code blocks):
        
        {{
            "hero_title": "Compelling main headline (max 10 words)",
            "hero_subtitle": "Supporting tagline that explains value proposition (max 25 words)",
            "about_section": "About us section content (2-3 paragraphs, professional tone)",
            "services": [
                {{
                    "title": "Service 1 Title",
                    "description": "Brief service description (2-3 sentences)",
                    "icon": "star"
                }},
                {{
                    "title": "Service 2 Title", 
                    "description": "Brief service description (2-3 sentences)",
                    "icon": "heart"
                }},
                {{
                    "title": "Service 3 Title",
                    "description": "Brief service description (2-3 sentences)", 
                    "icon": "check"
                }}
            ],
            "contact_info": {{
                "phone": "(555) 123-4567",
                "email": "info@example.com",
                "address": "123 Business Street, City, State 12345",
                "business_hours": "Monday - Friday: 9:00 AM - 5:00 PM"
            }},
            "meta_title": "SEO optimized page title (max 60 characters)",
            "meta_description": "SEO meta description (max 160 characters)",
            "meta_keywords": "5-8 relevant keywords separated by commas"
        }}
        
        Requirements:
        - Make the content professional, engaging, and specific to the {industry} industry
        - Use appropriate business terminology for {business_type}
        - Ensure all text is original and compelling
        - Keep within character limits specified
        - Use only these icon names: star, heart, check, briefcase, target, headphones, shield, globe, cog, users
        - Respond with ONLY the JSON object, no other text
        """
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response and extract structured data"""
        try:
            # Clean the response - remove any markdown formatting or extra text
            cleaned_response = response.strip()
            
            # Find JSON content
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_content = json.loads(json_str)
                
                # Validate the parsed content structure
                return self._validate_and_clean_content(parsed_content)
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing error: {str(e)}")
            # Try alternative parsing methods
            return self._extract_content_manually(response)
    
    def _validate_and_clean_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the AI-generated content"""
        
        # Ensure required fields exist
        required_fields = {
            'hero_title': 'Welcome to Your Business',
            'hero_subtitle': 'Professional services tailored to your needs',
            'about_section': 'We provide excellent services to our clients.',
            'services': [],
            'contact_info': {},
            'meta_title': 'Professional Business Services',
            'meta_description': 'Quality professional services for your business needs',
            'meta_keywords': 'business, professional, services, quality, reliable'
        }
        
        for field, default_value in required_fields.items():
            if field not in content or not content[field]:
                content[field] = default_value
        
        # Validate services structure
        if not isinstance(content['services'], list):
            content['services'] = []
        
        # Ensure services have required fields
        validated_services = []
        valid_icons = ['star', 'heart', 'check', 'briefcase', 'target', 'headphones', 'shield', 'globe', 'cog', 'users']
        
        for service in content['services'][:3]:  # Limit to 3 services
            if isinstance(service, dict):
                validated_service = {
                    'title': service.get('title', 'Professional Service'),
                    'description': service.get('description', 'Quality service description'),
                    'icon': service.get('icon', 'star') if service.get('icon') in valid_icons else 'star'
                }
                validated_services.append(validated_service)
        
        # Ensure we have at least 3 services
        while len(validated_services) < 3:
            validated_services.append({
                'title': f'Service {len(validated_services) + 1}',
                'description': 'Professional service offering',
                'icon': 'star'
            })
        
        content['services'] = validated_services
        
        # Validate contact_info structure
        if not isinstance(content['contact_info'], dict):
            content['contact_info'] = {}
        
        contact_defaults = {
            'phone': '(555) 123-4567',
            'email': 'info@business.com',
            'address': '123 Business Street, City, State 12345',
            'business_hours': 'Monday - Friday: 9:00 AM - 5:00 PM'
        }
        
        for field, default in contact_defaults.items():
            if field not in content['contact_info'] or not content['contact_info'][field]:
                content['contact_info'][field] = default
        
        # Ensure text length limits
        if len(content['hero_title']) > 80:
            content['hero_title'] = content['hero_title'][:77] + '...'
        
        if len(content['hero_subtitle']) > 150:
            content['hero_subtitle'] = content['hero_subtitle'][:147] + '...'
        
        if len(content['meta_title']) > 60:
            content['meta_title'] = content['meta_title'][:57] + '...'
        
        if len(content['meta_description']) > 160:
            content['meta_description'] = content['meta_description'][:157] + '...'
        
        return content
    
    def _extract_content_manually(self, response: str) -> Dict[str, Any]:
        """Manually extract content if JSON parsing fails"""
        
        # Try to extract key information from the response
        lines = response.split('\n')
        
        # Look for title-like content
        title = "Welcome to Your Business"
        subtitle = "Professional services tailored to your needs"
        
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 80:
                if any(word in line.lower() for word in ['welcome', 'professional', 'expert', 'quality', 'best']):
                    title = line.replace('"', '').replace("'", '')
                    break
        
        return {
            "hero_title": title,
            "hero_subtitle": subtitle,
            "about_section": response[:500] if len(response) > 500 else response,
            "services": [
                {"title": "Service 1", "description": "Professional service description", "icon": "star"},
                {"title": "Service 2", "description": "Quality service offering", "icon": "heart"},
                {"title": "Service 3", "description": "Dedicated support service", "icon": "check"}
            ],
            "contact_info": {
                "phone": "(555) 123-4567",
                "email": "info@business.com",
                "address": "123 Business Street, City, State 12345",
                "business_hours": "Monday - Friday: 9:00 AM - 5:00 PM"
            },
            "meta_title": "Professional Business Services",
            "meta_description": "Quality professional services for your business needs",
            "meta_keywords": "business, professional, services, quality, reliable"
        }
    
    def _get_fallback_content(self, business_type: str, industry: str, business_name: str) -> Dict[str, Any]:
        """Provide fallback content when AI service fails"""
        
        business_display = business_name if business_name else f"{business_type} Business"
        
        # Industry-specific customization
        industry_keywords = {
            'technology': ['innovation', 'digital', 'solutions', 'software', 'tech'],
            'healthcare': ['medical', 'health', 'care', 'wellness', 'treatment'],
            'education': ['learning', 'education', 'training', 'knowledge', 'academic'],
            'finance': ['financial', 'investment', 'banking', 'money', 'consulting'],
            'food': ['culinary', 'dining', 'restaurant', 'catering', 'cuisine'],
            'retail': ['shopping', 'products', 'merchandise', 'sales', 'store'],
            'real estate': ['property', 'homes', 'investment', 'buying', 'selling'],
            'automotive': ['vehicles', 'cars', 'automotive', 'repair', 'maintenance'],
            'construction': ['building', 'construction', 'renovation', 'contracting', 'development'],
            'legal': ['legal', 'law', 'attorney', 'consultation', 'representation']
        }
        
        keywords = industry_keywords.get(industry.lower(), ['professional', 'quality', 'service', 'business', 'excellence'])
        
        services_map = {
            'technology': [
                {'title': 'Software Development', 'description': 'Custom software solutions for your business needs', 'icon': 'cog'},
                {'title': 'IT Consulting', 'description': 'Expert technology consulting and strategic planning', 'icon': 'briefcase'},
                {'title': 'Technical Support', 'description': '24/7 technical support and maintenance services', 'icon': 'headphones'}
            ],
            'healthcare': [
                {'title': 'Patient Care', 'description': 'Comprehensive healthcare services with personalized attention', 'icon': 'heart'},
                {'title': 'Medical Consultation', 'description': 'Expert medical consultation and diagnosis', 'icon': 'shield'},
                {'title': 'Health Monitoring', 'description': 'Continuous health monitoring and preventive care', 'icon': 'check'}
            ],
            'education': [
                {'title': 'Online Learning', 'description': 'Interactive online courses and educational programs', 'icon': 'globe'},
                {'title': 'Tutoring Services', 'description': 'Personalized tutoring and academic support', 'icon': 'users'},
                {'title': 'Certification Programs', 'description': 'Professional certification and skill development', 'icon': 'target'}
            ]
        }
        
        default_services = [
            {'title': f'{industry} Consulting', 'description': f'Expert consulting services in {industry.lower()} to help your business grow', 'icon': 'briefcase'},
            {'title': 'Strategy Development', 'description': 'Comprehensive strategy development tailored to your business goals', 'icon': 'target'},
            {'title': 'Support Services', 'description': 'Ongoing support and maintenance to ensure your success', 'icon': 'headphones'}
        ]
        
        services = services_map.get(industry.lower(), default_services)
        
        return {
            "hero_title": f"Welcome to {business_display}",
            "hero_subtitle": f"Professional {business_type.lower()} services in the {industry.lower()} industry",
            "about_section": f"""
            We are a leading {business_type.lower()} company specializing in {industry.lower()} solutions. 
            With years of experience and a commitment to excellence, we provide our clients with 
            top-quality services that meet their unique needs.
            
            Our team of professionals is dedicated to delivering outstanding results and ensuring 
            customer satisfaction. We pride ourselves on our attention to detail, innovative approach, 
            and reliable service delivery.
            """.strip(),
            "services": services,
            "contact_info": {
                "phone": "(555) 123-4567",
                "email": f"info@{business_name.lower().replace(' ', '').replace('-', '')}.com" if business_name else "info@business.com",
                "address": "123 Business Street, City, State 12345",
                "business_hours": "Monday - Friday: 9:00 AM - 5:00 PM"
            },
            "meta_title": f"{business_display} - Professional {industry} Services",
            "meta_description": f"Professional {business_type.lower()} services in {industry.lower()}. Quality solutions for your business needs.",
            "meta_keywords": f"{business_type.lower()}, {industry.lower()}, {', '.join(keywords[:5])}"
        }
    
    def generate_layout_structure(self, template_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate website layout structure based on template type"""
        
        base_layout = {
            "header": {
                "type": "header",
                "components": ["logo", "navigation", "cta_button"]
            },
            "sections": [],
            "footer": {
                "type": "footer", 
                "components": ["contact_info", "social_links", "copyright"]
            }
        }
        
        # Define sections based on template type
        template_sections = {
            "business": [
                {"type": "hero", "components": ["title", "subtitle", "cta_button", "hero_image"]},
                {"type": "about", "components": ["title", "content", "image"]},
                {"type": "services", "components": ["title", "service_grid"]},
                {"type": "contact", "components": ["form", "info", "map"]}
            ],
            "portfolio": [
                {"type": "hero", "components": ["title", "subtitle", "portfolio_preview"]},
                {"type": "about", "components": ["title", "content", "skills"]}, 
                {"type": "portfolio", "components": ["filter", "gallery"]},
                {"type": "contact", "components": ["form", "info"]}
            ],
            "restaurant": [
                {"type": "hero", "components": ["title", "subtitle", "reservation_button"]},
                {"type": "about", "components": ["story", "chef_info"]},
                {"type": "menu", "components": ["menu_categories", "featured_items"]},
                {"type": "contact", "components": ["location", "hours", "reservation"]}
            ],
            "blog": [
                {"type": "hero", "components": ["title", "subtitle", "search"]},
                {"type": "featured_posts", "components": ["post_grid"]},
                {"type": "categories", "components": ["category_list"]},
                {"type": "about", "components": ["author_info"]}
            ],
            "ecommerce": [
                {"type": "hero", "components": ["title", "subtitle", "shop_button"]},
                {"type": "featured_products", "components": ["product_grid"]},
                {"type": "about", "components": ["brand_story"]},
                {"type": "contact", "components": ["support_info"]}
            ]
        }
        
        base_layout["sections"] = template_sections.get(template_type, template_sections["business"])
        
        return base_layout

    def generate_enhanced_content(self, business_type: str, industry: str, business_name: str = "", 
                                additional_info: str = "") -> Dict[str, Any]:
        """Generate enhanced content with additional business information"""
        
        enhanced_prompt = f"""
        Create comprehensive website content for a {business_type} business{f" called '{business_name}'" if business_name else ""} 
        in the {industry} industry.
        
        Additional Information: {additional_info}
        
        Generate content that includes:
        1. Compelling hero section with strong value proposition
        2. Detailed about section highlighting unique selling points
        3. Three main services with benefits-focused descriptions
        4. Professional contact information
        5. SEO-optimized meta tags
        
        Respond with ONLY a valid JSON object (no markdown, no code blocks):
        
        {{
            "hero_title": "Compelling main headline",
            "hero_subtitle": "Value proposition subtitle",
            "about_section": "Detailed about section (3-4 paragraphs)",
            "services": [
                {{"title": "Service 1", "description": "Benefits-focused description", "icon": "star"}},
                {{"title": "Service 2", "description": "Benefits-focused description", "icon": "heart"}},
                {{"title": "Service 3", "description": "Benefits-focused description", "icon": "check"}}
            ],
            "contact_info": {{
                "phone": "Professional phone number",
                "email": "Professional email",
                "address": "Professional address",
                "business_hours": "Business hours"
            }},
            "meta_title": "SEO title (under 60 chars)",
            "meta_description": "SEO description (under 160 chars)",
            "meta_keywords": "Relevant keywords"
        }}
        """
        
        try:
            response = self.model.generate_content(enhanced_prompt)
            if response.text:
                return self._parse_ai_response(response.text)
            else:
                return self._get_fallback_content(business_type, industry, business_name)
        except Exception as e:
            print(f"Enhanced content generation error: {str(e)}")
            return self._get_fallback_content(business_type, industry, business_name)


class ContentOptimizer:
    """Optimize content for SEO and readability"""
    
    @staticmethod
    def optimize_meta_tags(content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize meta tags for SEO"""
        
        # Ensure meta title is within 60 characters
        if len(content.get('meta_title', '')) > 60:
            content['meta_title'] = content['meta_title'][:57] + '...'
        
        # Ensure meta description is within 160 characters
        if len(content.get('meta_description', '')) > 160:
            content['meta_description'] = content['meta_description'][:157] + '...'
        
        return content
    
    @staticmethod
    def validate_content_structure(content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure content structure is complete"""
        
        required_fields = {
            'hero_title': 'Welcome to Our Business',
            'hero_subtitle': 'Professional services you can trust',
            'about_section': 'We provide excellent services to our clients.',
            'services': [],
            'contact_info': {},
            'meta_title': 'Business Website',
            'meta_description': 'Professional business website',
            'meta_keywords': 'business, professional, services'
        }
        
        for field, default_value in required_fields.items():
            if not content.get(field):
                content[field] = default_value
        
        return content
    
    @staticmethod
    def enhance_readability(content: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance content readability"""
        
        # Split long paragraphs in about section
        if 'about_section' in content and len(content['about_section']) > 500:
            paragraphs = content['about_section'].split('\n')
            if len(paragraphs) == 1:
                # Split long single paragraph
                sentences = content['about_section'].split('. ')
                mid_point = len(sentences) // 2
                content['about_section'] = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])
        
        return content
    
    @staticmethod
    def generate_seo_keywords(business_type: str, industry: str, content: Dict[str, Any]) -> str:
        """Generate SEO-optimized keywords based on content"""
        
        # Base keywords
        base_keywords = [business_type.lower(), industry.lower()]
        
        # Extract keywords from content
        text_content = f"{content.get('hero_title', '')} {content.get('about_section', '')}"
        
        # Common business keywords
        business_keywords = [
            'professional', 'services', 'quality', 'expert', 'business',
            'solutions', 'consulting', 'support', 'reliable', 'experienced'
        ]
        
        # Find relevant keywords in content
        found_keywords = []
        for keyword in business_keywords:
            if keyword in text_content.lower():
                found_keywords.append(keyword)
        
        # Combine and limit to 8 keywords
        all_keywords = base_keywords + found_keywords[:6]
        
        return ', '.join(all_keywords[:8])
    
    @staticmethod
    def optimize_for_mobile(content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for mobile viewing"""
        
        # Shorten hero title for mobile
        if len(content.get('hero_title', '')) > 50:
            words = content['hero_title'].split()
            if len(words) > 8:
                content['mobile_hero_title'] = ' '.join(words[:6]) + '...'
            else:
                content['mobile_hero_title'] = content['hero_title']
        else:
            content['mobile_hero_title'] = content.get('hero_title', '')
        
        # Optimize service descriptions for mobile
        if 'services' in content:
            for service in content['services']:
                if len(service.get('description', '')) > 120:
                    service['mobile_description'] = service['description'][:117] + '...'
                else:
                    service['mobile_description'] = service.get('description', '')
        
        return content