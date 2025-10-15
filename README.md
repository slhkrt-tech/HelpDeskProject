# Helpdesk Project
Django tabanlı ticket yönetim sistemi. Kullanıcılar ticket oluşturabilir, destek ekibi bunları yönetebilir.

## Özellikler
- Ticket oluşturma, güncelleme, silme
- Kullanıcı ve destek ekibi rolleri
- Basit yönetici paneli (Django Admin)
- Geliştirmeye ve genişletilmeye uygun yapı

## Kurulum ve Çalıştırma
```bash
git clone https://github.com/slhkrt-tech/HelpDeskProject.git
cd HelpDeskProject
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Admin paneli: http://127.0.0.1:8000/admin/
Uygulama: http://127.0.0.1:8000/tickets/