import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY=os.getenv('SECRET_KEY') or 'your-secret-key-here'
    MONGO_URI=os.getenv('MONGODB_URI') or 'mongodb://localhost:27017/ai_website_builder'
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=24)
    GEMINI_API_KEY=os.getenv('GEMINI_API_KEY')
    
class DevelopmentConfig(Config):
    DEBUG=True

class ProductionConfig(Config):
    DEBUG=False

config={
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}