"""
wsgi.py
Django uygulamasının WSGI uyumlu sunucular (örneğin Gunicorn, uWSGI) tarafından çalıştırılmasını sağlayan giriş noktasıdır.
Bu dosya, Django’yu synchronous (senkron) ortamda çalıştırmak için standart arayüzü tanımlar.
"""

import os
from django.core.wsgi import get_wsgi_application

# Django'nun hangi ayar dosyasını kullanacağını belirtir.
# Eğer ortam değişkeni tanımlı değilse varsayılan olarak helpdesk.settings kullanılır.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')

# WSGI sunucusu (örneğin Gunicorn), bu nesne üzerinden Django uygulamasını çağırır.

application = get_wsgi_application()