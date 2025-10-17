from django.apps import AppConfig

# "accounts" uygulamasının yapılandırma sınıfı.
# Django, bu sınıfı uygulamayı başlatırken otomatik olarak çağırır.
# Burada sinyallerin bağlanması veya uygulamaya özel başlangıç işlemleri tanımlanabilir.

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Otomatik oluşturulan birincil anahtar tipi
    name = 'accounts'  # Uygulama adı (INSTALLED_APPS'ta referans alınır)