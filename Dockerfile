# Temel imaj: Python 3.12’nin küçük (slim) sürümü kullanılıyor
FROM python:3.12-slim

# .pyc dosyalarının (derlenmiş Python bytecode’ları) yazılmasını engeller
ENV PYTHONDONTWRITEBYTECODE 1

# Python çıktılarının anında terminale yazılmasını sağlar (log gecikmesini önler)
ENV PYTHONUNBUFFERED 1

# Uygulama dizinini oluştur ve çalışma dizinini /app olarak ayarla
WORKDIR /app

# Gereksinim dosyasını kopyala
COPY requirements.txt /app/

# Sistemde temel araçları ve PostgreSQL için gerekli kütüphaneleri kur, ardından Python bağımlılıklarını yükle
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    pip install --no-cache-dir -r requirements.txt

# Proje dosyalarının tamamını konteynıra kopyala
COPY . /app

# Statik dosyaları (CSS, JS, görseller vs.) topla
RUN python manage.py collectstatic --noinput

# Giriş betiğini (entrypoint) kopyala ve çalıştırılabilir hale getir
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Konteyner başlatıldığında entrypoint betiğini çalıştır
CMD ["/app/entrypoint.sh"]