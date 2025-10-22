# 🎯 HelpDesk - Professional Ticket Management System

Modern, güvenli ve ölçeklenebilir Django tabanlı destek ticket yönetim sistemi. Kurumsal düzeyde güvenlik özellikleri ve kullanıcı dostu arayüz ile geliştirilmiştir.

## 🚀 Temel Özellikler

### 🔐 Güvenlik & Authentication
- **Token-based Authentication** - JWT benzeri özel token sistemi
- **Role-based Access Control** - Admin, Support, Customer rolleri
- **Rate Limiting** - Brute force saldırı koruması
- **Session Management** - Güvenli çerez yönetimi
- **Input Sanitization** - XSS ve SQL injection koruması
- **CSRF Protection** - Cross-site request forgery koruması

### 🎫 Ticket Management
- **Kapsamlı Ticket Sistemi** - Oluşturma, düzenleme, durum takibi
- **Kategori & SLA Yönetimi** - Öncelik ve yanıt süresi kontrolü
- **Comment Sistemi** - Ticket'lara yorum ekleme
- **Grup Tabanlı Erişim** - Kullanıcılar sadece kendi gruplarındaki ticket'ları görür
- **Status Tracking** - Detaylı durum geçiş sistemi
- **Auto Assignment** - Otomatik ticket atama

### 👥 User Management
- **Custom User Model** - Genişletilmiş kullanıcı profilleri
- **Group Management** - Kullanıcı grupları ve izin yönetimi
- **Admin Panel** - Gelişmiş kullanıcı yönetim arayüzü
- **Profile System** - Kullanıcı profil yönetimi

### 🎨 Modern UI/UX
- **Bootstrap 5.3** - Modern ve responsive tasarım
- **Dark/Light Theme** - Tema değiştirme sistemi
- **Role-based Dashboards** - Rol tabanlı özelleştirilmiş paneller
- **Interactive Components** - AJAX tabanlı dinamik işlemler
- **Mobile Responsive** - Tüm cihazlarda uyumlu

## 🛠 Teknoloji Stack

### Backend
- **Django 5.2.7** - Python web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Ana veritabanı
- **Redis/LocMem** - Caching sistemi

### Frontend
- **Bootstrap 5.3.2** - CSS framework
- **Bootstrap Icons** - Icon sistemi
- **Vanilla JavaScript** - Frontend interactivity
- **AJAX** - Asynchronous operations

### Security & Deployment
- **WhiteNoise** - Static file serving
- **CORS** - Cross-origin resource sharing
- **Rate Limiting** - Request throttling
- **Environment Variables** - Configuration management

## 🏗 Mimari & Yapı

```
helpdesk/
├── 📁 accounts/          # Kullanıcı yönetimi & kimlik doğrulama
│   ├── models.py        # CustomUser, CustomAuthToken
│   ├── views.py         # Authentication & user management
│   ├── middleware.py    # Token authentication middleware
│   ├── security.py      # Security utilities & decorators
│   └── templates/       # User interface templates
├── 📁 tickets/          # Ticket yönetim sistemi
│   ├── models.py        # Talep, Category, Comment, SLA
│   ├── views.py         # Ticket CRUD operations
│   ├── admin.py         # Django admin customizations
│   └── templates/       # Ticket interface templates
├── 📁 static/           # CSS, JS, images
├── 📁 templates/        # Base templates
└── 📁 helpdesk/         # Django project settings
```

## 🔧 Kurulum ve Konfigürasyon

### Ön Gereksinimler
- Python 3.11+
- PostgreSQL 12+
- Git

### 1. Proje Kurulumu
```bash
# Repository'yi klonla
git clone https://github.com/your-username/helpdesk-project.git
cd helpdesk-project

# Virtual environment oluştur
python -m venv venv

# Virtual environment'ı aktif et
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 2. Veritabanı Konfigürasyonu
```bash
# PostgreSQL veritabanı oluştur
createdb helpdesk_db

# Environment variables ayarla (opsiyonel)
# .env dosyası oluştur
echo "DB_NAME=helpdesk_db" > .env
echo "DB_USER=postgres" >> .env
echo "DB_PASSWORD=your_password" >> .env
echo "DB_HOST=localhost" >> .env
echo "DB_PORT=5432" >> .env
echo "DEBUG=True" >> .env
```

### 3. Django Setup
```bash
# Veritabanı migrasyonlarını çalıştır
python manage.py makemigrations
python manage.py migrate

# Superuser oluştur
python manage.py createsuperuser

# Static dosyaları topla (production için)
python manage.py collectstatic

# Development server başlat
python manage.py runserver
```

### 4. İlk Konfigürasyon
```bash
# Kategoriler oluştur
python manage.py shell
>>> from tickets.models import Category
>>> Category.objects.create(name="IT Support")
>>> Category.objects.create(name="HR")
>>> Category.objects.create(name="Finance")
>>> exit()

# Kullanıcı grupları oluştur (Django admin panelinden)
# http://127.0.0.1:8000/admin/
```

## 🎯 Kullanım Kılavuzu

### Erişim Noktaları
- **Ana Sayfa:** http://127.0.0.1:8000/
- **Giriş:** http://127.0.0.1:8000/accounts/login/
- **Admin Panel:** http://127.0.0.1:8000/accounts/admin-panel/
- **Ticket Listesi:** http://127.0.0.1:8000/tickets/
- **Django Admin:** http://127.0.0.1:8000/admin/

### Kullanıcı Rolleri

#### 🔴 Admin (Sistem Yöneticisi)
- Tüm ticket'ları görüntüleme ve yönetme
- Kullanıcı oluşturma, düzenleme, silme
- Grup yönetimi ve izin ataması
- Sistem konfigürasyonu
- Token yönetimi

#### 🟡 Support (Destek Personeli)
- Tüm ticket'ları görüntüleme
- Ticket durum güncelleme
- Yorum ekleme
- Ticket atama işlemleri

#### 🟢 Customer (Müşteri)
- Kendi ticket'larını görüntüleme
- Grup ticket'larını görüntüleme
- Yeni ticket oluşturma
- Yorumlarını ekleme

### API Endpoints
```bash
# Authentication
POST /accounts/api/login/     # Kullanıcı girişi
POST /accounts/api/logout/    # Kullanıcı çıkışı
POST /accounts/api/signup/    # Yeni kullanıcı kaydı
GET  /accounts/api/profile/   # Kullanıcı profili

# Ticket Management
GET    /tickets/              # Ticket listesi
POST   /tickets/create/       # Yeni ticket
GET    /tickets/{id}/         # Ticket detayı
POST   /tickets/{id}/change-status/  # Durum güncelleme
```

## 🔒 Güvenlik Özellikleri

### Authentication & Authorization
- Custom token-based authentication
- Role-based access control (RBAC)
- Session security (httponly, secure, samesite)
- Password strength validation
- Account lockout protection

### Data Protection
- Input sanitization (XSS prevention)
- SQL injection protection (Django ORM)
- CSRF token validation
- Secure headers (X-Frame-Options, X-Content-Type-Options)
- Rate limiting (brute force protection)

### Monitoring & Logging
```python
# Log dosyaları
logs/django.log     # Genel uygulama logları
logs/security.log   # Güvenlik olayları
```

## 🧪 Testing & Development

### Test Çalıştırma
```bash
# Tüm testleri çalıştır
python manage.py test

# Specific app test
python manage.py test accounts
python manage.py test tickets

# Coverage report
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Development Settings
```python
# settings.py development ayarları
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
DATABASES['default']['OPTIONS']['sslmode'] = 'prefer'
```

## 📚 Advanced Configuration

### Production Deployment
```bash
# Environment variables
export DEBUG=False
export ALLOWED_HOST=yourdomain.com
export SECRET_KEY=your-secret-key
export DB_HOST=your-db-host

# HTTPS ayarları
export SECURE_SSL_REDIRECT=True
export SESSION_COOKIE_SECURE=True
export CSRF_COOKIE_SECURE=True
```

### Custom Middleware
```python
# accounts/middleware.py - Token Authentication
# accounts/security.py - Security utilities
# Rate limiting ve IP tracking
```

### Database Optimization
```sql
-- PostgreSQL indexes
CREATE INDEX idx_ticket_status ON tickets_talep(status);
CREATE INDEX idx_ticket_user ON tickets_talep(user_id);
CREATE INDEX idx_token_user ON accounts_customauthtoken(user_id);
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

## 👥 Team & Support

- **Developer:** Salih KURT
- **Email:** slhkrt333@gmail.com
- **Documentation:** [Wiki Pages]()
- **Issues:** [GitHub Issues]()