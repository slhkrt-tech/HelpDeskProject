"""
settings.py
HelpDesk Project - Django yapılandırması
"""

import os
from pathlib import Path

# ============================================================
# PROJE ANA DİZİNİ
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# GÜVENLİK AYARLARI - ALPHA PRODUCTION
# ============================================================

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'alpha-production-secret-key-change-for-real-production')
DEBUG = False  # Alpha production için DEBUG kapalı
ALPHA_MODE = True  # Alpha production flag

# Alpha production için localhost only
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1',
    '[::1]',
    '192.168.1.*',  # Local network
    os.getenv('ALLOWED_HOST', 'localhost')
]

# Security headers - Alpha production optimized
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'  # Strict security for alpha production
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = 'same-origin'

# HTTPS settings - Alpha production (localhost için relaxed)
SECURE_SSL_REDIRECT = False  # Alpha production'da localhost için kapalı
SESSION_COOKIE_SECURE = False  # Alpha production'da localhost için kapalı
CSRF_COOKIE_SECURE = False  # Alpha production'da localhost için kapalı

# ============================================================
# UYGULAMALAR - ALPHA PRODUCTION
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Üçüncü parti - Production optimized
    'rest_framework',
    'rest_framework.authtoken',
    'widget_tweaks',
    'crispy_forms',

    # Yerel uygulamalar
    'tickets',
    'accounts',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ============================================================
# MIDDLEWARE - ALPHA PRODUCTION
# ============================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files - production
    'accounts.security.SecurityMiddleware',  # Custom security middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.middleware.TokenAuthMiddleware',  # Token authentication middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================
# URL / WSGI - ALPHA PRODUCTION
# ============================================================

ROOT_URLCONF = 'helpdesk.urls'
WSGI_APPLICATION = 'helpdesk.wsgi.application'

# Gunicorn production server settings
ALLOWED_HOSTS.extend(['0.0.0.0'])  # Gunicorn için
USE_TZ = True
TIME_ZONE = 'Europe/Istanbul'

# ============================================================
# VERİTABANI VE CACHE
# ============================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'helpdesk_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', '123456'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'prefer',
        }
    }
}

# Cache configuration - Alpha production optimized
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'alpha-production-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 5000,  # Increased for production
            'CULL_FREQUENCY': 2,  # More aggressive cleanup
        }
    }
}

# Database connection pooling
DATABASE_CONNECTION_POOLING = {
    'default': {
        'MAX_CONNS': 20,
        'MAX_CONNS_PER_APP': 5,
    }
}

# ============================================================
# TEMPLATE
# ============================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",
            BASE_DIR / "tickets" / "templates",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================================
# ŞİFRE GÜVENLİĞİ
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Password hashing - Alpha production optimized
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # En güvenli hasher
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# ============================================================
# DİL / ZAMAN
# ============================================================

LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ============================================================
# STATİK / MEDYA
# ============================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================
# GİRİŞ / ÇIKIŞ / KULLANICI MODELİ
# ============================================================

LOGIN_REDIRECT_URL = '/tickets/'
LOGOUT_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'accounts.CustomUser'

# ============================================================
# CSRF VE SESSION GÜVENLİĞİ
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://127.0.0.1:8001',
    'http://localhost:8001',
    'https://127.0.0.1:8000',
    'https://localhost:8000',
]

# CSRF Security - Alpha production
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False  # Alpha production'da localhost için kapalı
CSRF_COOKIE_SAMESITE = 'Strict'  # Daha güvenli
CSRF_USE_SESSIONS = False
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# Session Security - Alpha production
SESSION_COOKIE_SECURE = False  # Alpha production'da localhost için kapalı
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'  # Daha güvenli
SESSION_COOKIE_AGE = 1800  # 30 dakika (daha kısa)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Additional security settings - Alpha production
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB (daha kısıtlayıcı)
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 500  # Daha kısıtlayıcı

# ============================================================
# DİĞER
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# DJANGO REST FRAMEWORK GÜVENLİK
# ============================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '50/hour',  # Daha kısıtlayıcı
        'user': '500/hour'  # Daha kısıtlayıcı
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ============================================================
# LOGGİNG SİSTEMİ
# ============================================================

LOGGING = {
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
        'security': {
            'format': 'SECURITY {levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',  # Alpha production: sadece warning ve error
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
            'maxBytes': 10*1024*1024,  # 10MB
            'backupCount': 5,
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'security',
            'maxBytes': 10*1024*1024,  # 10MB
            'backupCount': 5,
        },
        'console': {
            'level': 'ERROR',  # Alpha production: sadece error console'da
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['file', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'tickets': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'root': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}

# ============================================================
# E-POSTA AYARLARI - ALPHA PRODUCTION
# ============================================================

# Alpha production için console backend (gerçek SMTP henüz kurulmadı)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Gelecek real production için SMTP ayarları (şimdilik yorum)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
# EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# Şifre sıfırlama e-postası ayarları
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@helpdesk-alpha.local')
EMAIL_SUBJECT_PREFIX = '[HelpDesk Alpha] '

# E-posta timeout ayarları
EMAIL_TIMEOUT = 10  # Daha kısa timeout