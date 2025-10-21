#!/bin/sh
# Bu betik, Django projesini başlatmadan önce gerekli adımları otomatik olarak gerçekleştirir.

# Hata oluşursa betiği hemen durdurur (örneğin migrate başarısız olursa)
set -e

echo "1️⃣  Veritabanı migrasyonları uygulanıyor..."
python manage.py migrate
echo "✅ Veritabanı migrasyonları tamamlandı."

echo "2️⃣  Statik dosyalar toplanıyor..."
python manage.py collectstatic --noinput
echo "✅ Statik dosyalar toplandı."

echo "3️⃣  Gunicorn başlatılıyor..."
# Gunicorn, WSGI tabanlı Python uygulamalarını çalıştıran bir sunucu
# HelpDeskProject.wsgi -> Django uygulamasının giriş noktası
exec gunicorn HelpDeskProject.wsgi:application --bind 0.0.0.0:8000

# Not:
# 0.0.0.0:8000 -> Sunucuyu dış dünyaya açar (8000 portu üzerinden dinler)
# exec komutu, mevcut kabuk sürecini Gunicorn süreciyle değiştirir