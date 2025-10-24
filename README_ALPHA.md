# HelpDesk Alpha Production 🚀

## Alpha Production Release v1.0.0-alpha

Bu HelpDesk uygulamasının **Alpha Production** sürümüdür. Localhost üzerinde production benzeri ayarlarla çalışacak şekilde optimize edilmiştir.

## 🎯 Alpha Production Özellikleri

### ✅ Production Optimizations
- **DEBUG = False** (Production modu)
- **Argon2 Password Hashing** (En güvenli)
- **Rotating Log Files** (10MB, 5 backup)
- **Optimized Caching** (5000 entries)
- **Security Headers** (HSTS, XSS Protection)
- **Rate Limiting** (API throttling)
- **Session Security** (30 dakika timeout)

### 🔒 Security Features
- Token-based authentication
- CSRF protection (Strict SameSite)
- XSS filtering
- Content type sniffing protection
- Secure cookie settings
- Input validation & sanitization

### 📊 Monitoring & Logging
- **Security Logs**: `logs/security.log`
- **Application Logs**: `logs/django.log`
- **Console Errors Only** (WARNING+ levels)
- **Log Rotation** (Automatic cleanup)

## 🚀 Deployment

### Hızlı Başlatma (Windows)
```cmd
deploy_alpha.bat
```

### Manuel Kurulum
```bash
# 1. Environment setup
export DEBUG=False
export ALPHA_MODE=True

# 2. Dependencies
pip install -r requirements.txt

# 3. Database
python manage.py migrate

# 4. Alpha setup
python manage.py alpha_production --setup

# 5. Static files
python manage.py collectstatic --noinput

# 6. Start server
python manage.py runserver 0.0.0.0:8000
```

## 👤 Default Credentials

```
Username: admin
Password: alpha123!
Email: admin@helpdesk-alpha.local
Role: Administrator
```

## 🌐 Access Points

- **Main Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/accounts/admin/
- **API Endpoints**: http://localhost:8000/api/
- **Tickets**: http://localhost:8000/tickets/

## 🛠️ Management Commands

```bash
# System status
python manage.py alpha_production --status

# Create admin user
python manage.py alpha_production --create-admin

# System cleanup
python manage.py alpha_production --cleanup

# Security check
python manage.py check --deploy
```

## 📈 Performance Settings

### Database
- **PostgreSQL** with connection pooling
- **Optimized queries** (select_related, prefetch_related)
- **Database indexes** on frequently queried fields

### Caching
- **Local Memory Cache** (5000 entries)
- **Template caching** enabled
- **Static file compression** (WhiteNoise)

### Security
- **Rate limiting**: 50/hour (anonymous), 500/hour (authenticated)
- **Session timeout**: 30 minutes
- **Token expiration**: 7 days
- **CSRF protection**: Strict SameSite

## 🐛 Debugging

### Log Locations
```
logs/django.log      - Application logs (WARNING+)
logs/security.log    - Security events (WARNING+)
```

### Common Issues
1. **Database Connection**: Check PostgreSQL service
2. **Static Files**: Run `collectstatic`
3. **Permissions**: Check file permissions in logs/
4. **Memory**: Monitor cache usage

## 📊 Alpha Production vs Development

| Feature | Development | Alpha Production |
|---------|-------------|------------------|
| DEBUG | True | False |
| Logging | INFO+ | WARNING+ |
| Sessions | 1 hour | 30 minutes |
| Rate Limiting | 1000/hour | 500/hour |
| Password Hashing | PBKDF2 | Argon2 |
| CSRF SameSite | Lax | Strict |
| Cache Entries | 1000 | 5000 |

## 🔄 Updates & Maintenance

### Regular Tasks
```bash
# Clean expired tokens
python manage.py alpha_production --cleanup

# Check system status
python manage.py alpha_production --status

# Security audit
python manage.py check --deploy
```

### Backup Important Files
- Database: `helpdesk_alpha_db`
- Logs: `logs/` directory
- Media: `media/` directory (if any)
- Settings: `.env.alpha`

## 🎯 Next Steps (Real Production)

1. **HTTPS Setup** (SSL certificates)
2. **Real SMTP** (Email configuration)
3. **External Database** (Production PostgreSQL)
4. **Reverse Proxy** (Nginx/Apache)
5. **Process Manager** (Gunicorn/uWSGI)
6. **Container Deployment** (Docker)

---

**Alpha Production Ready** ✅  
**Local Testing** ✅  
**Security Hardened** ✅  
**Performance Optimized** ✅