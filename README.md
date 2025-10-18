# Helpdesk Project
Django tabanlı ticket yönetim sistemi. Kullanıcılar ticket oluşturabilir, destek ekibi bunları yönetebilir.

## Özellikler
- Ticket oluşturma, güncelleme, silme
- Kullanıcı ve destek ekibi rolleri
- Basit yönetici paneli (Django Admin)
- Geliştirmeye ve genişletilmeye uygun yapı

## Kurulum ve Çalıştırma
# Helpdesk Project

Django tabanlı ticket yönetim sistemi. Kullanıcılar ticket oluşturabilir, destek ekibi bunları yönetebilir.

## Özellikler
- Ticket oluşturma, güncelleme, silme
- Kullanıcı ve destek ekibi rolleri
- Basit yönetici paneli (Django Admin)
- Geliştirmeye ve genişletilmeye uygun yapı

## Kurulum ve Çalıştırma (Yerel)

```bash
git clone https://github.com/slhkrt-tech/HelpDeskProject.git
cd HelpDeskProject
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows PowerShell
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Admin paneli: http://127.0.0.1:8000/admin/
Uygulama: http://127.0.0.1:8000/tickets/

## Local geliştirme - `.env` kullanımı

Bu repo, hassas bilgileri doğrudan saklamamak için ortam değişkenleriyle çalışır. Örnek bir dosya olan `.env.example` mevcuttur. Yerelde çalıştırmak için:

1. `.env.example` dosyasını kopyalayıp `.env` olarak kaydedin ve değerleri düzenleyin:

```powershell
copy .env.example .env
```

2. Virtualenv'i aktive edin ve bağımlılıkları yükleyin:

```powershell
venv\Scripts\activate
pip install -r requirements.txt
```

3. Veritabanı migration'larını çalıştırıp superuser oluşturun, ardından projeyi başlatın:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

NOT: `.env` dosyasını repoya eklemeyin. Üretim ortamında secrets yönetimi (CI secrets, Vault vb.) kullanın.

---

Daha fazla bilgi ve deployment talimatları için `docs/` veya bir PR isteği açabilirsiniz.

## Geliştirici araçları

Yerelde kod kalitesini korumak için `pre-commit` kullanmanızı öneriyoruz. İlk kurulum:

```powershell
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

CI otomasyonu için `.github/workflows/ci.yml` eklendi; push/pull request'lerde lint ve test aşamaları çalışacaktır.