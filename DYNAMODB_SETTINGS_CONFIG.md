"""
DynamoDB Settings Configuration for auth_project/settings.py

This file contains the settings needed for DynamoDB integration.
Add these configurations to your auth_project/settings.py

These replace the original PostgreSQL DATABASES configuration.
"""

# ==================== DATABASE CONFIGURATION ====================

# For DynamoDB, we don't use Django's traditional DATABASES setting
# DynamoDB is managed separately via pynamodb

# Don't load DATABASE_URL if using DynamoDB
USE_DYNAMODB = os.environ.get('USE_DYNAMODB', 'False').lower() == 'true'

if USE_DYNAMODB:
    # ✅ Remove/Comment out the old DATABASES configuration:
    # DATABASES = {
    #     'default': dj_database_url.config(...)
    # }
    
    # Set minimal database config (Django still needs a DB for built-in apps)
    # Use SQLite locally or use DynamoDB for everything
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    
    # AWS DynamoDB Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    
    # DynamoDB Table Prefix (for dev/prod separation)
    DYNAMODB_TABLE_PREFIX = os.environ.get('DYNAMODB_TABLE_PREFIX', 'recruithub-')
    
    # For local DynamoDB testing (comment out for production)
    # DYNAMODB_LOCAL_HOST = 'http://localhost:8000'
    DYNAMODB_LOCAL_HOST = os.environ.get('DYNAMODB_LOCAL_HOST', None)
    
    # DynamoDB Session Backend
    SESSION_ENGINE = 'core.dynamodb_session_backend'
    SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
    
else:
    # PostgreSQL Configuration (Original)
    DATABASES = {
        'default': dj_database_url.config(
            default='sqlite:///db.sqlite3',
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    
    # Database SSL for secure production connections
    if not DEBUG and 'postgresql' in DATABASES['default'].get('ENGINE', ''):
        DATABASES['default']['OPTIONS'] = {
            'sslmode': 'require',
        }


# ==================== AWS S3 CONFIGURATION ====================

# AWS S3 Configuration (for media files - works with both DBs)
USE_S3 = os.environ.get('USE_S3', 'False').lower() == 'true'

if USE_S3:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    
    # S3 Security Settings
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_DEFAULT_ACL = None  # No default ACL
    AWS_QUERYSTRING_AUTH = True  # Require query string authentication
    AWS_S3_ADDRESSING_STYLE = 'virtual'
    
    # Media Files
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    MEDIA_LOCATION = 'media'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'


# ==================== EMAIL CONFIGURATION ====================

# Email backend for sending emails
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'  # Console for development
)

# For Resend (modern email provider)
if 'resend' in EMAIL_BACKEND:
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')

# For Gmail SMTP
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'


# ==================== SECURITY CONFIGURATION ====================

# CORS / Domain Configuration
CSRF_TRUSTED_ORIGINS = [
    origin.strip() 
    for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'https://vakverse.com,https://*.vakverse.com'
    ).split(',')
]


# ==================== LOGGING CONFIGURATION (Important for DynamoDB debugging) ====================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',  # Change to 'DEBUG' for DynamoDB debugging
    },
    'loggers': {
        'pynamodb': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    },
}


# ==================== RENDER DEPLOYMENT CHECKS ====================

# Verify critical environment variables are set in production
if not DEBUG:
    critical_vars = {
        'SECRET_KEY': 'Django security key',
        'ALLOWED_HOSTS': 'Allowed domain names',
    }
    
    if USE_DYNAMODB:
        critical_vars.update({
            'AWS_ACCESS_KEY_ID': 'AWS access key',
            'AWS_SECRET_ACCESS_KEY': 'AWS secret key',
            'AWS_REGION': 'AWS region',
        })
    
    if USE_S3:
        critical_vars.update({
            'AWS_STORAGE_BUCKET_NAME': 'S3 bucket name',
            'AWS_S3_REGION_NAME': 'S3 region',
        })
    
    for var, description in critical_vars.items():
        value = os.environ.get(var)
        if not value:
            raise ImproperlyConfigured(
                f"CRITICAL: {var} environment variable is required in production.\n"
                f"Description: {description}"
            )
