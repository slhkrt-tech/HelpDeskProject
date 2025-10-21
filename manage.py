import os   # Ortam değişkenleri (environment variables) ile çalışmak için
import sys  # Komut satırından argüman almak için kullanılır


def main():
    """
    Django komutlarını yönetmek için ana fonksiyon.
    Örneğin: runserver, makemigrations, migrate gibi komutlar burada çalıştırılır.
    """

    # Django'nun hangi ayar dosyasını (settings.py) kullanacağını belirtir
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')

    try:
        # Django'nun komut satırı arayüzünü içe aktarır
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Eğer Django kurulmamışsa kullanıcıyı bilgilendirir
        raise ImportError(
            "Django modülü içe aktarılamadı.\n"
            "PYTHONPATH’in doğru ayarlandığından ve sanal ortamın (virtualenv) aktif olduğundan emin olun."
        ) from exc

    # Komut satırından gelen Django komutlarını çalıştırır
    execute_from_command_line(sys.argv)


# Bu dosya doğrudan çalıştırıldığında (örneğin: python manage.py) ana fonksiyon çağrılır
if __name__ == '__main__':
    main()