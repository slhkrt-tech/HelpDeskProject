#apps.py, django uygulamasının proje içindeki yapılandırma noktasıdır
#ID alanları ve uygulama adı gibi temel ayarları belirler

from django.apps import AppConfig #django uygulamaları için temel konfigürasyon sınıfıdır


class TicketsConfig(AppConfig): #tickets uygulaması için bir konfigürasyon sınıfı
    default_auto_field = 'django.db.models.BigAutoField' #bu uygulamadaki modellerin ID alanları için varsayılan tip, 64-bit integer, büyük veritabanları için güvenli
    name = 'tickets' #uygulamanın proje içindeki ad, django bu isimle uygulamayı tanır ve INSTALLED_APPS’e eklenir