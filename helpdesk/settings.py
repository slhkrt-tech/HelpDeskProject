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
# GÜVENLİK AYARLARI (ORTAM DEĞİŞKENLERİYLE)
# ============================================================

# SECRET_KEY üretimde zorunlu olacak şekilde ortamdan alınır. Geliştirme için
# fallback 'dev-secret-key' kullanılabilir, ancak prod'ta bu kabul edilemez.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    # Eğer production olarak işaretlenmişse SECRET_KEY yoksa hata fırlat
    if os.getenv('ENV', 'development') == 'production':
        raise RuntimeError('DJANGO_SECRET_KEY environment variable must be set in production')
    SECRET_KEY = 'dev-secret-key'

# DEBUG: environment üzerinden okunur. Varsayılan geliştirme modu (True).
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')

# ALLOWED_HOSTS: virgülle ayrılmış host listesi veya varsayılan localhost
raw_allowed = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in raw_allowed.split(',') if h.strip()]

# ============================================================
# UYGULAMALAR
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Üçüncü parti

    'widget_tweaks',
    'crispy_forms',

    # Yerel uygulamalar

    'tickets',
    'accounts',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================
# URL / WSGI
# ============================================================

ROOT_URLCONF = 'helpdesk.urls'
WSGI_APPLICATION = 'helpdesk.wsgi.application'

# ============================================================
# VERİTABANI
# ============================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'helpdesk_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', '123456'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ============================================================
# TEMPLATE
# ============================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
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
# CSRF VE SESSION AYARLARI (ÇIKIŞ HATASI ÇÖZÜMÜ)
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_USE_SESSIONS = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# Güvenlik iyileştirmeleri: DEBUG False ise https cookie'leri ve HSTS etkinleştirilir
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
X_FRAME_OPTIONS = 'DENY'

# Basit logging konfigürasyonu (konsola yazma) - gerektiğinde genişletin
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'admin_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(BASE_DIR / 'logs' / 'admin_actions.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'helpdesk.admin_actions': {
            'handlers': ['admin_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================
# DİĞER
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
