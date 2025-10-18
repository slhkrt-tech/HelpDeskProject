"""helpdesk.wsgi

WSGI sunucuları (ör. Gunicorn) için Django uygulamasının giriş noktası.
Bu dosya genellikle deploy ortamında kullanılır; development sırasında runserver kullanılır.
"""

import os
from django.core.wsgi import get_wsgi_application

# Hangi Django ayar dosyasının kullanılacağını belirle (varsayılan: helpdesk.settings)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')

# WSGI uygulaması, WSGI sunucuları tarafından çağrılır.
application = get_wsgi_application()