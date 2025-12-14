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

# REDIS CONFIGURATION FOR CACHING AND CHANNELS
REDIS_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/0')

# Check if Redis packages are available
try:
    import redis
    import django_redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

# Django Channels Configuration
if HAS_REDIS:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [REDIS_URL],
            },
        },
    }
    
    # CACHING CONFIGURATION with Redis
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'ecolearn',
            'TIMEOUT': 1800,  # 30 minutes default
        }
    }
else:
    # Fallback to in-memory for development
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer'
        }
    }
    
    # Fallback to local memory cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# Cache time settings
CACHE_TTL = {
    'views': 900,  # 15 minutes for views
    'queries': 1800,  # 30 minutes for queries
    'static': 86400,  # 24 hours for static content
}

# SESSION CONFIGURATION
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# DATABASE CONFIGURATION
# Use PostgreSQL for production, SQLite for development
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL and HAS_DJ_DATABASE_URL:
    # Production: Use PostgreSQL via DATABASE_URL
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
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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

# Twilio Configuration (SMS & WhatsApp)
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

# Session Security
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour (in seconds)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True  # Update session expiry on every request

# CSRF Protection
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = True

# Logging Configuration for Security
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


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
