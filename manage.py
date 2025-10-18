import os  # Ortam değişkenleriyle çalışma için
import sys  # Komut satırı argümanlarını almak için


def main():
    # Django'nun hangi ayar dosyasını kullanacağını belirler.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Eğer Django yüklenmemişse geliştiriciye bilgi verir.
        raise ImportError(
            "Django’yu içe aktaramadık. PYTHONPATH yüklü ve ortam "
            "değişkenin kullanılabilir olduğuna emin misiniz? "
            "Sanal ortamı aktif ettiğinizden emin misiniz? "
        ) from exc
    # Komut satırından gelen Django komutlarını çalıştırır (runserver, migrate, vb.)
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()