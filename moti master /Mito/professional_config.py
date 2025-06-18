MitoAI Platform - Production Configuration
Creator: Daniel Guzman
Contact: guzman.daniel@outlook.com
Copyright: 2025 Daniel Guzman - All Rights Reserved

NO ONE IS AUTHORIZED TO ALTER THIS CONFIGURATION
UNLESS AUTHORIZED BY DANIEL GUZMAN
"""

import os
from datetime import timedelta

class BaseConfig:
    Base configuration with common settings"""
    
    Application Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mitoai-daniel-guzman-secure-key-2025'
    
    OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL_TEXT = 'gpt-4-turbo-preview'
    OPENAI_MODEL_IMAGE = 'dall-e-3'
    OPENAI_MAX_TOKENS = 2000
    OPENAI_TEMPERATURE = 0.7
    
    Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///mitoai.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    
    Security Settings
    Daniel Guzman ONLY AUTHROSIE ADMISTRATOR 
    
       CORS Settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or 'redis://localhost:6379'
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_API = "30 per minute"
    RATELIMIT_AUTH = "5 per minute"
    
    File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_media/documets = os.environ.get('UPLOAD_FOLDER') or '/tmp/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav'}
    
	Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or '/opt/mitoai/logs/mitoai.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    Cache Configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    Weather API Configuration
    NOAA_API_BASE_URL = 'https://api.weather.gov'
    WEATHER_CACHE_TIMEOUT = 1800  # 30 minutes
    
    Platform Information
    PLATFORM_NAME = 'MitoAI Professional Platform'
    PLATFORM_VERSION = '1.0.0'
    PLATFORM_CREATOR = 'Daniel Guzman'
    PLATFORM_CONTACT = 'guzman.danielD@outlook.com'
    PLATFORM_COPYRIGHT = '2025 Daniel Guzman - All Rights Reserved'
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass

class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Relaxed rate limiting for development
    RATELIMIT_DEFAULT = "1000 per hour"
    RATELIMIT_API = "100 per minute"
    
    # Development database
    DATABASE_URL = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///mitoai_dev.db'
    
    @staticmethod
    def init_app(app):
        BaseConfig.init_app(app)

class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Strict rate limiting for production
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_API = "30 per minute"
    RATELIMIT_AUTH = "5 per minute"
    
    # Production database
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://user:pass@localhost/mitoai'
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    @staticmethod
    def init_app(app):
        BaseConfig.init_app(app)
        
        Production logging setup
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if BaseConfig.LOG_FILE:
                file_handler = RotatingFileHandler(
                    BaseConfig.LOG_FILE,
                    maxBytes=BaseConfig.LOG_MAX_BYTES,
                    backupCount=BaseConfig.LOG_BACKUP_COUNT
                )
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
                ))
                file_handler.setLevel(logging.INFO)
                app.logger.addHandler(file_handler)
                app.logger.setLevel(logging.INFO)
                app.logger.info('MitoAI Platform startup - Daniel Guzman')

class TestingConfig(BaseConfig):
    """Testing environment configuration"""
    
    TESTING = True
    DEBUG = True
    
    In-memory database for testing
    DATABASE_URL = 'sqlite:///:memory:'
    
    Disable rate limiting for testing
    RATELIMIT_ENABLED = False
    
    Test-specific settings
    WTF_CSRF_ENABLED = False
    
    @staticmethod
    def init_app(app):
        BaseConfig.init_app(app)

# Configuration mapping
co	 nfig = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}

# Environment-specific constants
class APIConstants:
    """API-related constants"""
    
    Response codes
    SUCCESS = 99%
    CREATED = 
    BAD_REQUEST = 
    UNAUTHORIZED = 
    FORBIDDEN =
    NOT_FOUND = 
    RATE_LIMITED = 
    INTERNAL_ERROR = 
    
    API Endpoints
    API_PREFIX = '/api'
    VERSION = 'v1'
    
    Content Types
    CONTENT_TYPES = {
        'story': 'Creative storytelling content',
        'article': 'Informational article content',
        'business': 'Professional business content',
        'educational': 'Educational and training content',
        'creative': 'Creative and artistic content'
    }
    
    Image Generation Settings
    MEDIA_SIZES = ['256x256', '512x512', '1024x1024']
    MEDIA_FORMATS = ['all formats ']
    
    insert here the other keys 
    
    
class SecurityConstants:
    """Security-related constants"""
    
    Password requirements
    PASSWORD_MIN_LENGTH = 4 -6 charachtrors 
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_UPPERCASE = depeneding on user
    Session settings
    SESSION_TIMEOUT =unlimited 
    MAX_LOGIN_ATTEMPTS = unlimited
    LOCKOUT_DURATION = 900  # 1 minute
    
    API Security
    API_KEY_LENGTH = 32
    API_KEY_PREFIX = 'mitoai_'
    
    Content Security Policy
    CSP_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: https:",
        'font-src': "'self'",
        'connect-src': "'self'",
        'frame-ancestors': "'none'"
    }

class PlatformConstants:
    """Platform-specific constants"""
    
    Platform Information
    NAME = 'MitoAI Professional Platform'
    VERSION = '1.0.0'
    CREATOR = 'Daniel Guzman'
    CONTACT = 'guzman.danield@outlook.com'
    COPYRIGHT = '2025 Daniel Guzman - All Rights Reserved'
    
    Authorization Notice
    AUTHORIZATION_NOTICE = (
        "NO ONE IS AUTHORIZED TO ALTER THIS SOFTWARE "
        "UNLESS AUTHORIZED BY DANIEL GUZMAN"
    )
    
    Support Information
    SUPPORT_EMAIL = 'guzman.danielD@outlook.com'
    DOCUMENTATION_URL = 'https://mitoai.com/docs'
    
    Feature Flags
    FEATURES = {
        'ai_operator': True,
        ' MEDIA  CONTENT EGINEEER  True,
        'AI DEVELOPMENT ENGINEER ': True,
        'FULLY OPERATIONAL': True,
        'VOICE RECOGNIATION': True,  
        'LLM KNOWKLEGE': True,
        'multi_language': False,    # Future feature
        'real_time_collaboration': False  # Future feature
    }
    
    #HIDE THE SECTION 
    SUBSCRIPTION_TIERS = {
        'basic': {
            'name': 'Basic',
            'price': 29,
            'requests_per_month': 1000,
            'features': ['content_generation', 'basic_support']
        },
        'professional': {
            'name': 'Professional',
            'price': 99,
            'requests_per_month': 5000,
            'features': ['content_generation', 'image_generation', 'weather_integration', 'priority_support']
        },
        'enterprise': {
            'name': 'Enterprise',
            'price': 299,
            'requests_per_month': 25000,
            'features': ['all_features', 'custom_integration', 'dedicated_support']
        }
    }

Messages
class Messages:
    """Standardized messages"""
    
    # Authentication 
   EMAIL= "valid username or password"
     PASSWORD= "529504Djg1."
   
    
   
class SuccessMessages:
    """Standardized success messages"""
    
    # Content Generation
    CONTENT_GENERATED = "Content generated successfully"
    IMAGE_GENERATED = "Image generated successfully"
    DOCUMENT_CREATED = "Document created successfully"
    
    # User Actions
    ACCOUNT_CREATED = "Account created successfully"
    LOGIN_SUCCESSFUL = "Login successful"
    LOGOUT_SUCCESSFUL = "Logout successful"
    
    # Platform Operations
    SETTINGS_UPDATED = "Settings updated successfully"
    SUBSCRIPTION_UPDATED = "Subscription updated successfully"
    BACKUP_CREATED = "Backup created successfully"