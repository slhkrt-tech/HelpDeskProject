# Yardım Masası Sistemi 🎫

Modern, güvenli ve üretime hazır yardım masası talep yönetim sistemi. Django ile geliştirilmiş, dakikalar içinde kurulum!

## 🚀 Hızlı Başlangıç

### 1. Projeyi İndirin
```bash
git clone https://github.com/slhkrt-tech/HelpDeskProject.git
cd HelpDeskProject
```

### 2. Gerekli Bağımlılıkları Kurun
```bash
pip install -r requirements.txt
```

### 3. Veritabanını Hazırlayın
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 4. Admin Kullanıcısı Oluşturun
```bash
python manage.py createsuperuser
```

### 5. Sunucuyu Başlatın
```bash
python manage.py runserver
```

### 6. Uygulamaya Erişin
- **Ana URL**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin/

**İşte bu kadar! Yardım Masası sisteminiz çalışıyor!** 🎉

## 🎯 Sistem Özellikleri

### ✅ Kapsamlı Talep Yönetimi
- Talep oluşturma, güncelleme, kapatma
- Kategori yönetimi
- Yorum sistemi
- Durum takibi
- Dosya eklentileri
- Otomatik atama
- Öncelik seviyeleri
- SLA takibi

### ✅ Kullanıcı Yönetimi
- Rol tabanlı erişim (Admin, Destek, Müşteri)
- Kullanıcı grupları ve izinler
- Profil yönetimi
- Güvenli kimlik doğrulama
- Token tabanlı API erişimi
- Çoklu kullanıcı desteği

### ✅ Admin Dashboard
- Gerçek zamanlı sistem analitikleri
- Kullanıcı yönetim arayüzü
- Sistem raporları ve istatistikleri
- CSV dışa aktarma
- Performans metrikleri
- Sistem durumu izleme

### ✅ Modern Arayüz
- Bootstrap 5 ile responsive tasarım
- Koyu/Açık tema desteği
- Mobil uyumlu
- Sidebar navigasyon
- Gerçek zamanlı bildirimler
- Gradient tasarım

## 🛠️ Teknoloji Yığını

- **Backend**: Django 5.2.7 + Django REST Framework
- **Veritabanı**: SQLite (geliştirme), PostgreSQL (üretim)
- **Frontend**: Bootstrap 5.3 + JavaScript ES6
- **Güvenlik**: Token auth, CSRF koruması, input validasyonu
- **Önbellek**: Django Cache Framework
- **Logging**: Yapılandırılabilir loglama sistemi

## 📋 Sistem Gereksinimleri

- Python 3.8+
- Django 5.2.7
- Modern web tarayıcısı
- 1GB RAM (minimum)
- 500MB disk alanı

## 🔧 Kurulum

### Geliştirme Ortamı
```bash
# Sanal ortam oluşturun
python -m venv venv

# Sanal ortamı etkinleştirin (Windows)
venv\Scripts\activate

# Bağımlılıkları kurun
pip install -r requirements.txt

# Veritabanını oluşturun
python manage.py makemigrations
python manage.py migrate

# Statik dosyaları toplayın
python manage.py collectstatic --noinput

# Geliştirme sunucusunu başlatın
python manage.py runserver
```

## 🌐 Erişim Noktaları

- **Ana Sayfa**: http://127.0.0.1:8000/
- **Giriş**: http://127.0.0.1:8000/accounts/login/
- **Kayıt**: http://127.0.0.1:8000/accounts/signup/
- **Admin Panel**: http://127.0.0.1:8000/accounts/admin/
- **Müşteri Panel**: http://127.0.0.1:8000/accounts/customer-panel/
- **Destek Panel**: http://127.0.0.1:8000/accounts/support-panel/

## 👤 Varsayılan Hesaplar

```
🔑 Admin Hesabı:
   Kullanıcı Adı: admin
   Şifre: (kurulumda belirleyeceksiniz)
   Rol: Sistem Yöneticisi

👨‍💼 Test Hesapları:
   Destek: support / support123
   Müşteri: customer / customer123
```

## 🔒 Güvenlik Özellikleri

- **Token Kimlik Doğrulama**: Güvenli API erişimi
- **CSRF Koruması**: Cross-site request forgery önleme
- **XSS Koruması**: Input temizleme ve sanitizasyon
- **Rate Limiting**: Brute force saldırı koruması
- **Güvenli Oturumlar**: HttpOnly, Secure, SameSite cookies
- **Şifre Politikası**: Güçlü şifre gereksinimleri
- **İzin Sistemi**: Rol tabanlı erişim kontrolü

## � Kullanıcı Arayüzleri

### Müşteri Paneli
- Yeni talep oluşturma
- Mevcut talepleri görüntüleme
- Talep durumu takibi
- Yorumlar ve dosya ekleme
- Profil yönetimi

### Destek Paneli
- Atanan talepleri yönetme
- Müşterilere yanıt verme
- Talep durumu güncelleme
- İç notlar ekleme
- Performans metrikleri

### Admin Paneli
- Kapsamlı kullanıcı yönetimi
- Sistem konfigürasyonu
- Analitik ve raporlar
- Veri dışa aktarma
- Token yönetimi
- Sistem izleme

## 📊 API Dokümantasyonu

### Kimlik Doğrulama
```bash
POST /accounts/api/login/     # Kullanıcı girişi
POST /accounts/api/logout/    # Kullanıcı çıkışı
GET  /accounts/api/profile/   # Kullanıcı profili
POST /accounts/api/signup/    # Kullanıcı kaydı
```

### Talep Yönetimi
```bash
GET    /tickets/api/                    # Talep listesi
POST   /tickets/api/create/             # Talep oluştur
GET    /tickets/api/{id}/               # Talep detayı
PUT    /tickets/api/{id}/update/        # Talep güncelle
POST   /tickets/api/{id}/comment/       # Yorum ekle
```

## 🧪 Test ve Geliştirme

### Test Çalıştırma
```bash
# Tüm testleri çalıştır
python manage.py test

# Belirli uygulamayı test et
python manage.py test tickets

# Debug modu
export DEBUG=True
python manage.py runserver
```

## 🤝 Katkıda Bulunma

1. Repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi yapın
4. Testleri çalıştırın
5. Pull Request oluşturun

## 📞 Destek

- **GitHub Issues**: Hata raporları ve özellik istekleri
- **Dokümantasyon**: Sistem içi yardım sistemi
- **E-posta**: slhkrt333@gmail.com

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 🎯 Kullanıma Hazır!

**Kurulum tamamlandığında:**

1. **http://127.0.0.1:8000** adresine gidin
2. Admin hesabı oluşturun
3. İlk taleplerinizi oluşturmaya başlayın!

**Yardım Masası sisteminiz artık hazır!** 🚀

### 📋 İlk Adımlar

- [ ] Admin hesabını oluştur
- [ ] Destek personeli hesapları ekle
- [ ] Talep kategorilerini yapılandır
- [ ] Sistem yedekleme planını oluştur

**Başarılı bir Yardım Masası işletimi için tüm özellikler hazır!** ✨