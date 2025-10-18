"""`helpdesk` projesinin WSGI giriş noktası.

Bu modül, üretim ortamlarında (ör. Gunicorn/uwsgi) kullanılan WSGI uygulamasını
sağlar. Geliştirme sırasında `manage.py runserver` kullanılır fakat deploy için
bu dosya gereklidir.
"""

import os

from django.core.wsgi import get_wsgi_application

# Django hangi ayarlar modülünü kullanacağını belirler
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')

# WSGI uygulaması: WSGI uyumlu sunucular tarafından çağrılır
application = get_wsgi_application()
