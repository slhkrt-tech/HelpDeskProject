#settings.py dosyası, projenin tüm yapılandırmalarını (güvenlik, uygulamalar, veritabanı, statik dosyalar, zaman/dil, template) merkezi bir yerden yönetir
#os ve path modülleri, dosya ve klasör yollarını yönetmek için kullanılır

import os
from pathlib import Path

#projenin ana klasörünü tutar
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-i8$43=o4)s_tguv2ff)jve+lze-8mx#3@^sfcv+w7@!k(u69t2' #django’nun şifreleme ve güvenlik işlemlerinde kullandığı gizli anahtar
                                                                                  #production için farklı tut

DEBUG = True #ise hata mesajları ve debug bilgileri gösterilir, production’da false olmalı

ALLOWED_HOSTS = [] #projeyi hangi domain veya IP’lerin kullanabileceğini belirler

INSTALLED_APPS = [
    #django’nun hazır uygulamaları (admin, auth, sessions) ve kendi uygulamalar (tickets) burada listelenir
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tickets', #bu app
    'crispy_forms',  #opsiyonel
    'crispy_bootstrap5',  #opsiyonel
]
#crispy forms’un hangi stil paketini kullanacağını belirler
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    #django’nun HTTP isteğini işleyen ara katman yazılımlarıdır
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'helpdesk.urls' #django’ya ana URL konfigürasyon dosyasını gösterir

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"], #genel templates varsa
        'APP_DIRS': True, #her uygulamanın kendi templates klasörünü kullanmasını sağlar
        'OPTIONS': {
            'context_processors': [ #template’lere otomatik olarak değişken ekler
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
#WSGI sunucusunun (production için) Django uygulamasını çalıştırmasını sağlayan ana giriş noktasıdır
WSGI_APPLICATION = 'helpdesk.wsgi.application'




# Basit SQLite
#production’da PostgreSQL veya MySQL gibi daha güçlü bir veritabanı kullanılabilir
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [ #kullanıcı şifrelerinin güvenliğini sağlamak için çeşitli doğrulamalar yapılır
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




LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True #çok dilli destek

USE_TZ = True #zamanlar UTC bazlı tutulur

STATIC_URL = '/static/' #statik dosyaların URL yolu
STATICFILES_DIRS = [BASE_DIR / 'static'] #projede ekstra statik dosya klasörleri
LOGIN_REDIRECT_URL = '/tickets/' #login sonrası yönlendirilecek sayfa
LOGOUT_REDIRECT_URL = '/' #logout sonrası yönlendirilecek sayfa

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' #django modellerinde ID alanı için varsayılan olarak BigAutoField (64-bit integer) kullanılır
                                                     #böylece büyük veritabanlarında ID taşması sorunları önlenir
