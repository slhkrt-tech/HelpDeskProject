"""
settings.py
Projenin genel yapılandırmasını içerir:
- Güvenlik ayarları
- Uygulamalar
- Veritabanı bağlantısı
- Statik / medya dosyaları
- Şablon (template) ayarları
- Yetkilendirme ve kullanıcı modeli
"""

import os
from pathlib import Path

# Proje ana dizini

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# GÜVENLİK AYARLARI
# ============================================================

# Geliştirme ortamı için geçici secret key
# Production’da bu değer ortam değişkeninden okunmalı.

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key')

# DEBUG = True -> geliştirme sürecinde hata detaylarını gösterir.
# Production’da kesinlikle False olmalı.

DEBUG = True

# '*' -> her isteğe izin verir (sadece local ortamda kabul edilebilir)

ALLOWED_HOSTS = ['*']


# ============================================================
# UYGULAMALAR
# ============================================================

INSTALLED_APPS = [

    # Django çekirdek uygulamaları

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Üçüncü parti uygulamalar

    'crispy_forms',

    # Proje uygulamaları

    'tickets',
    'accounts',
]

# Crispy Forms ayarları

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
# URL ve UYGULAMA BAŞLATMA AYARLARI
# ============================================================

ROOT_URLCONF = 'helpdesk.urls'
WSGI_APPLICATION = 'helpdesk.wsgi.application'


# ============================================================
# VERİTABANI AYARLARI
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
# ŞABLON AYARLARI
# ============================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # Ortak template klasörü
        'APP_DIRS': True,  # Uygulamaların kendi template klasörlerini kullanmasına izin verir
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
# DİL VE ZAMAN AYARLARI
# ============================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True


# ============================================================
# STATİK VE MEDYA DOSYALARI
# ============================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # collectstatic çıktısı

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise: statik dosyaları production’da hızlı servis eder

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ============================================================
# GİRİŞ/ÇIKIŞ VE KULLANICI MODELİ
# ============================================================

LOGIN_REDIRECT_URL = '/tickets/'
LOGOUT_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'accounts.CustomUser'


# ============================================================
# OTOMATİK ID AYARI
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'