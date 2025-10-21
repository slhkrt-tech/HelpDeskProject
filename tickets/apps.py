# apps.py
# ================================================================================
# Django Uygulama Yapılandırması
# Bu dosya, uygulamanın proje içindeki yapılandırma noktasıdır.
# Modellerin varsayılan ID tipi ve uygulama adı gibi temel ayarlar burada belirlenir.
# ================================================================================

from django.apps import AppConfig

class TicketsConfig(AppConfig):
    # Modellerde varsayılan ID tipi (64-bit integer)
    default_auto_field = 'django.db.models.BigAutoField'

    # Uygulamanın proje içindeki adı
    name = 'tickets'