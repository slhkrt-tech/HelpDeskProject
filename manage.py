

import os #ortam değişkenleri ile çalışmak için
import sys #komut satırı argümanlarını almak için


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings') #django hangi ayar dosyasını kullanacağını bilir, setdefault → ortam değişkeni yoksa ayarlar
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc: #django yüklü değilse kullanıcıya uyarı verir
        raise ImportError(
            "Django’yu içe aktaramadık. PYTHONPATH yüklü ve ortam "
            "değişkenin kullanılabilir olduğuna emin misiniz? "
            "Sanal ortamı aktif ettiğinizden emin misiniz? "
        ) from exc
    execute_from_command_line(sys.argv) #komut satırındaki Django komutlarını çalıştırır


if __name__ == '__main__':
    main()
