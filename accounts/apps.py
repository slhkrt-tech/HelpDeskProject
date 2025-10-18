from django.apps import AppConfig


# AccountsConfig: accounts uygulamasının başlangıç yapılandırmasını barındırır.
# Uygulama başlatılırken sinyal bağlama veya özel başlatma işleri burada tanımlanabilir.
class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Varsayılan PK tipi
    name = 'accounts'  # INSTALLED_APPS içinde kullanılan uygulama adı