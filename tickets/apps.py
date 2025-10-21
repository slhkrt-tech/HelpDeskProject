# apps.py, Django uygulamasının proje içindeki yapılandırma noktasıdır
# ID alanları ve uygulama adı gibi temel ayarları belirler

from django.apps import AppConfig

class TicketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Modellerde varsayılan ID tipi (64-bit integer)
    name = 'tickets'  # Uygulamanın proje içindeki adı