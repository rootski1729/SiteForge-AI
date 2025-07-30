import google.generativeai as genai
from flask import current_app
import json

class GeminiService:
    def __init__(self):
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_website_content(self, business_type, industry, company_name=None):
        try:
            prompt = f"""
            Create a professional website content structure for a {business_type} business in the {industry} industry.
            Company name: {company_name or 'Your Company'}
            
            Please generate content in JSON format with the following structure:
            {{
                "hero": {{
                    "title": "Main headline",
                    "subtitle": "Supporting text",
                    "cta_text": "Call to action button text"}},
                "about": {{
                    "title": "About section title",
                    "content": "About section content (2-3 paragraphs)"}},
                "services": [
                    {{
                        "title": "Service 1",
                        "description": "Service description"}},
                    {{
                        "title": "Service 2", 
                        "description": "Service description"}},
                    {{
                        "title": "Service 3",
                        "description": "Service description"}}
                ],
                "contact": {{
                    "title": "Contact section title",
                    "content": "Contact section content"}}
            }}
            
            Make it professional and specific to the {business_type} in {industry} industry.
            Return only valid JSON without any markdown formatting.
            """
            
            response = self.model.generate_content(prompt)

            content = response.text.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            if isinstance(content, str):
                website_data = json.loads(content)

            return website_data
            
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return self.get_fallback_content(business_type, industry, company_name)
    
    def get_fallback_content(self, business_type, industry, company_name=None):
        company = company_name or "Your Company"
        
        return {
            "hero": {
                "title": f"Welcome to {company}",
                "subtitle": f"Your trusted partner in {industry}",
                "cta_text": "Get Started"
            },
            "about": {
                "title": "About Us",
                "content": f"We are a leading {business_type} company specializing in {industry}. With years of experience and dedication to excellence, we provide top-quality services to our clients. Our team is committed to delivering innovative solutions that meet your specific needs."
            },
            "services": [
                {
                    "title": "Professional Consulting",
                    "description": f"Expert consulting services tailored to {industry} businesses."
                },
                {
                    "title": "Custom Solutions",
                    "description": "Customized solutions designed to meet your unique requirements."
                },
                {
                    "title": "Support & Maintenance",
                    "description": "Ongoing support and maintenance to ensure optimal performance."
                }
            ],
            "contact": {
                "title": "Get In Touch",
                "content": "Ready to take your business to the next level? Contact us today to discuss how we can help you achieve your goals."
            }
        }