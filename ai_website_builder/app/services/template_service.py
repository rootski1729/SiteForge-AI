class TemplateService:
    @staticmethod
    def get_available_templates():
        return [
            {
                'id': 'default',
                'name': 'Default Template',
                'description': 'Clean and professional template'
            },
            {
                'id': 'modern',
                'name': 'Modern Template', 
                'description': 'Contemporary design with animations'
            },
            {
                'id': 'minimal',
                'name': 'Minimal Template',
                'description': 'Simple and elegant design'
            }
        ]
    
    @staticmethod
    def get_template_html(template_id='default'):
        templates={
            'default': """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{{ title }}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 0; line-height: 1.6; }
                    .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                    .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 0; text-align: center; }
                    .hero h1 { font-size: 3em; margin-bottom: 20px; }
                    .hero p { font-size: 1.2em; margin-bottom: 30px; }
                    .btn { background: #ff6b6b; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }
                    .section { padding: 60px 0; }
                    .services { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 30px; }
                    .service-card { background: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center; }
                    .contact { background: #f8f9fa; }
                </style>
            </head>
            <body>
                <section class="hero">
                    <div class="container">
                        <h1>{{ hero.title }}</h1>
                        <p>{{ hero.subtitle }}</p>
                        <a href="#contact" class="btn">{{ hero.cta_text }}</a>
                    </div>
                </section>
                
                <section class="section">
                    <div class="container">
                        <h2>{{ about.title }}</h2>
                        <p>{{ about.content }}</p>
                    </div>
                </section>
                
                <section class="section">
                    <div class="container">
                        <h2>Our Services</h2>
                        <div class="services">
                            {% for service in services %}
                            <div class="service-card">
                                <h3>{{ service.title }}</h3>
                                <p>{{ service.description }}</p>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </section>
                
                <section class="section contact" id="contact">
                    <div class="container">
                        <h2>{{ contact.title }}</h2>
                        <p>{{ contact.content }}</p>
                    </div>
                </section>
            </body>
            </html>
            """
        }
        return templates.get(template_id, templates['default'])