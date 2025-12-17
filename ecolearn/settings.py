"""
Django settings for ecolearn project - Optimized for Render deployment
"""

import os
from pathlib import Path
from decouple import config

# Try to import optional packages, fallback if not available
try:
    import dj_database_url
    HAS_DJ_DATABASE_URL = True
except ImportError:
    HAS_DJ_DATABASE_URL = False

try:
    import cloudinary
    import cloudinary_storage
    HAS_CLOUDINARY = True
except ImportError:
    HAS_CLOUDINARY = False

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver,*.onrender.com').split(',')

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://*.onrender.com',
]

# Application definition
INSTALLED_APPS = [
    'daphne',  # Must be first for Channels
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',  # Required for allauth
    
    # Third-party apps
    'whitenoise.runserver_nostatic',  # WhiteNoise for static files
    
    # Django Allauth (email/password only)
    'allauth',
    'allauth.account',
    
    'channels',  # Django Channels for WebSockets
    'import_export',  # Django Import-Export
    'accounts',
    'elearning',
    'community',
    'reporting',
    'payments',
    'gamification',
    'collaboration',
    'admin_dashboard',
    'ai_assistant',
    'security',
]

# Add optional apps if available
if HAS_CLOUDINARY:
    # Insert cloudinary_storage before django.contrib.staticfiles
    staticfiles_index = INSTALLED_APPS.index('django.contrib.staticfiles')
    INSTALLED_APPS.insert(staticfiles_index, 'cloudinary_storage')
    INSTALLED_APPS.append('cloudinary')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Language switching
    'security.middleware.SecurityMiddleware',
    'security.middleware.AuditMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required for allauth
    'accounts.middleware.UserLanguageMiddleware',  # User's preferred language
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecolearn.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',  # For language support
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.user_language',  # Custom language processor
                'accounts.context_processors.unread_notifications',  # Unread notifications count
                'admin_dashboard.context_processors.pending_proofs_count',  # Pending proofs badge
            ],
        },
    },
]

WSGI_APPLICATION = 'ecolearn.wsgi.application'
ASGI_APPLICATION = 'ecolearn.asgi.application'

# SIMPLIFIED CACHING AND CHANNELS CONFIGURATION (NO REDIS)
print("🔧 Using simplified local cache and session configuration (no Redis)")

# Django Channels Configuration - In-Memory Only
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# LOCAL MEMORY CACHE CONFIGURATION
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ecolearn-cache',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # Maximum number of cache entries
            'CULL_FREQUENCY': 3,  # Fraction of entries to cull when MAX_ENTRIES is reached
        }
    }
}

# Cache time settings - Reduced for memory optimization
CACHE_TTL = {
    'views': 300,  # 5 minutes for views (reduced)
    'queries': 600,  # 10 minutes for queries (reduced)
    'static': 86400,  # 24 hours for static content
}

# Memory optimization settings will be applied after DATABASES is defined

# SESSION CONFIGURATION - DATABASE SESSIONS ONLY
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour (in seconds)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True  # Update session expiry on every request

# DATABASE CONFIGURATION
DATABASE_URL = config('DATABASE_URL', default=None)
USE_MYSQL = config('USE_MYSQL', default=False, cast=bool)

# Check if MySQL configuration is requested
if USE_MYSQL:
    # Use MySQL configuration from .env
    DATABASES = {
        'default': {
            'ENGINE': config('DB_ENGINE', default='django.db.backends.mysql'),
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
    print(f"✅ MySQL database configured: {DATABASES['default']['NAME']} at {DATABASES['default']['HOST']}")

elif not DEBUG and DATABASE_URL:
    # Production: Use PostgreSQL
    print(f"🔍 PRODUCTION MODE - DEBUG={DEBUG}")
    print(f"🔍 DATABASE_URL present: {bool(DATABASE_URL)}")
    print(f"🔍 HAS_DJ_DATABASE_URL: {HAS_DJ_DATABASE_URL}")
    
    if not HAS_DJ_DATABASE_URL:
        print("❌ ERROR: dj-database-url package is missing!")
        raise ImportError("dj-database-url is required for production database configuration!")
    
    try:
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
        }
        # Ensure PostgreSQL client is used and configure connection pooling
        DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
        DATABASES['default']['OPTIONS'] = {
            'sslmode': 'require',  # Required for most cloud PostgreSQL services
        }
        # Connection pooling settings for better performance
        DATABASES['default']['CONN_MAX_AGE'] = 600
        
        print(f"✅ Production database configured: {DATABASES['default']['ENGINE']}")
        print(f"✅ Database host: {DATABASES['default'].get('HOST', 'Not specified')}")
        
    except Exception as e:
        print(f"❌ ERROR parsing DATABASE_URL: {e}")
        raise

elif DATABASE_URL and HAS_DJ_DATABASE_URL:
    # Development with DATABASE_URL (optional PostgreSQL)
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
    }
    DATABASES['default']['CONN_MAX_AGE'] = 600
else:
    # Local development: Use SQLite as fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("✅ SQLite database configured for local development")

# Memory optimization settings for production
if not DEBUG:
    # Reduce database connection pool size
    DATABASES['default']['CONN_MAX_AGE'] = 300  # 5 minutes instead of 10

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Africa/Lusaka'
USE_I18N = True
USE_TZ = True

# Supported Languages
LANGUAGES = [
    ('en', 'English'),
    ('bem', 'Chibemba'),
    ('ny', 'Chinyanja'),
]

# Language cookie settings
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 31536000  # 1 year

# CLOUDINARY CONFIGURATION - GLOBAL FOR ALL APPS
if HAS_CLOUDINARY:
    import cloudinary.uploader
    import cloudinary.api
    
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
        'API_KEY': config('CLOUDINARY_API_KEY', default=''),
        'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
        'SECURE': True,
    }

    # Configure Cloudinary
    cloudinary.config(
        cloud_name=config('CLOUDINARY_CLOUD_NAME', default=''),
        api_key=config('CLOUDINARY_API_KEY', default=''),
        api_secret=config('CLOUDINARY_API_SECRET', default=''),
        secure=True
    )

# STATIC FILES CONFIGURATION WITH WHITENOISE
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration for static files compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_MAX_AGE = 31536000  # 1 year cache for static files

# MEDIA FILES CONFIGURATION
if HAS_CLOUDINARY:
    # Use Cloudinary for media files in production
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    # Use local storage for development
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CLOUDINARY TRANSFORMATIONS - GLOBAL PRESETS
CLOUDINARY_TRANSFORMATIONS = {
    'profile_picture': {'width': 200, 'height': 200, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'},
    'thumbnail': {'width': 400, 'height': 300, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'},
    'banner': {'width': 1200, 'height': 400, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'},
    'gallery': {'width': 800, 'height': 600, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'},
    'icon': {'width': 100, 'height': 100, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'},
    'report_photo': {'width': 600, 'height': 450, 'crop': 'fill', 'format': 'webp', 'quality': 'auto'},
}

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Login/Logout
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'  # Redirect to landing page on logout/session expiry

# Gemini AI Configuration
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')

# Africa's Talking Configuration (Primary SMS Provider)
AFRICAS_TALKING_USERNAME = config('AFRICAS_TALKING_USERNAME', default='sandbox')
AFRICAS_TALKING_API_KEY = config('AFRICAS_TALKING_API_KEY', default='')

# Twilio Configuration (Backup & WhatsApp)
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_API_KEY_SID = config('TWILIO_API_KEY_SID', default='')
TWILIO_API_KEY_SECRET = config('TWILIO_API_KEY_SECRET', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')
TWILIO_WHATSAPP_NUMBER = config('TWILIO_WHATSAPP_NUMBER', default='whatsapp:+14155238886')

# Security Settings
ENCRYPTION_KEY = config('ENCRYPTION_KEY', default='HqQOIjSgnmFaRQn56qQmkF2lkN6X365g-GWYRGqumXA=')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session Security (consolidated with session configuration above)
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True

# CSRF Protection
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = True

# Logging Configuration - Production-ready for Render deployment
def get_logging_config():
    """
    Get logging configuration that works in both development and production.
    Uses file logging in development, console-only in production (Render-compatible).
    """
    # Base configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {asctime} {message}',
                'style': '{',
            },
            'production': {
                'format': '[{asctime}] {levelname} {name}: {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG' if DEBUG else 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple' if DEBUG else 'production',
            },
        },
        'loggers': {
            'security': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.security': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    }
    
    # Add file logging only in development
    if DEBUG:
        logs_dir = os.path.join(BASE_DIR, 'logs')
        try:
            # Try to create logs directory
            os.makedirs(logs_dir, exist_ok=True)
            
            # Add file handler if directory creation succeeds
            config['handlers']['file'] = {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': os.path.join(logs_dir, 'security.log'),
                'formatter': 'verbose',
            }
            
            # Add file handler to security logger
            config['loggers']['security']['handlers'] = ['file', 'console']
            
        except (OSError, PermissionError):
            # If we can't create logs directory, stick with console only
            pass
    
    return config

# Apply logging configuration
LOGGING = get_logging_config()


# ===================================================================
# DJANGO ALLAUTH CONFIGURATION
# ===================================================================

SITE_ID = 1

# Authentication backends
AUTHENTICATION_BACKENDS = [
    # Django default
    'django.contrib.auth.backends.ModelBackend',
    # Allauth specific
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth settings - Phone number only, no email verification
ACCOUNT_LOGIN_METHODS = {'username'}  # Use username instead of email
ACCOUNT_SIGNUP_FIELDS = ['username*', 'password1*', 'password2*']  # No email required
ACCOUNT_EMAIL_VERIFICATION = 'none'  # No email verification
ACCOUNT_UNIQUE_EMAIL = False  # Email not required to be unique
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False  # No email confirmation
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/5m',  # Replaces ACCOUNT_LOGIN_ATTEMPTS_LIMIT/TIMEOUT
}



# Redirect URLs
LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'



# Custom adapter to handle user creation
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://*.onrender.com',
]

