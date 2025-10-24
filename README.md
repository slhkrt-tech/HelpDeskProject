# HelpDesk System 🎫

Modern, secure and production-ready helpdesk ticketing system built with Django. Deploy locally in minutes!

## 🚀 Quick Start (1-Click Setup)

### 1. Download
```bash
git clone https://github.com/slhkrt-tech/HelpDeskProject.git
cd HelpDeskProject
```

### 2. One-Click Start
```bash
start_production.bat
```

### 3. Access Application
- **URL**: http://localhost:8000
- **Admin**: admin / alpha123!

**That's it! Your production-ready HelpDesk is running!** 🎉

## 🎯 What You Get

### ✅ Complete Ticketing System
- Create, update, close tickets
- Category management  
- Comment system
- Status tracking
- File attachments
- Auto-assignment

### ✅ User Management
- Role-based access (Admin, Support, Customer)
- User groups and permissions
- Profile management
- Secure authentication
- Token-based API access

### ✅ Admin Dashboard
- User management interface
- System settings
- Reports and statistics  
- CSV export functionality
- Real-time monitoring

### ✅ Production Features
- **Waitress WSGI server** (production-grade)
- **Multi-threading** (6 workers)
- **Security hardened** (CSRF, XSS, rate limiting)
- **Optimized performance** (caching, static files)
- **Health monitoring** (built-in status checks)

## 🛠️ Technology Stack

- **Backend**: Django 5.2.7 + Django REST Framework
- **Database**: PostgreSQL 
- **Frontend**: Bootstrap 5 + JavaScript
- **Server**: Waitress WSGI (Windows optimized)
- **Security**: Token auth, CSRF protection, input validation

## 📋 System Requirements

- Python 3.8+
- PostgreSQL 12+ 
- 2GB RAM minimum
- 1GB disk space
- Windows/Linux/Mac

## 🔧 Manual Setup (If Needed)

### Database Setup
```sql
CREATE DATABASE helpdesk_db;
CREATE USER postgres WITH PASSWORD '123456';
GRANT ALL PRIVILEGES ON DATABASE helpdesk_db TO postgres;
```

### Step-by-Step
```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create admin user
python manage.py alpha_production --setup

# Start production server
python production_server.py
```

## 🎮 Management Commands

```bash
# System status
python manage.py alpha_production --status

# Server health check  
python manage.py alpha_production --server-status

# System cleanup
python manage.py alpha_production --cleanup

# Start production server
python manage.py alpha_production --start-server
```

## 🌐 Access Points

- **Main App**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/accounts/admin/
- **Customer Panel**: http://localhost:8000/accounts/customer-panel/
- **Support Panel**: http://localhost:8000/accounts/support-panel/
- **API**: http://localhost:8000/api/

## 👤 Default Accounts

```
🔑 Admin Account:
   Username: admin
   Password: alpha123!
   Email: admin@helpdesk-alpha.local
   Role: Administrator
```

## 🔒 Security Features

- **Token Authentication**: Secure API access
- **CSRF Protection**: Cross-site request forgery prevention
- **XSS Protection**: Input sanitization 
- **Rate Limiting**: Brute force protection
- **Secure Sessions**: HttpOnly, Secure, SameSite cookies
- **Argon2 Hashing**: Military-grade password security
- **HSTS Headers**: HTTP Strict Transport Security

## 📊 Performance Features

- **Multi-threaded Server**: 6 worker threads
- **Connection Pooling**: Database optimization
- **Static File Compression**: WhiteNoise optimization
- **Memory Caching**: 5000 entry cache
- **Optimized Logging**: Production-level logging

## 📱 User Interfaces

### Customer Panel
- Create and track tickets
- View ticket history
- Add comments
- Update profile
- File attachments

### Support Panel  
- Manage assigned tickets
- Respond to customers
- Update ticket status
- View all tickets
- Internal notes

### Admin Panel
- Complete user management
- System configuration
- Reports and analytics
- Export data (CSV)
- Token management

## 🔧 Configuration Options

### Environment Variables
Create `.env` file for custom settings:
```env
DJANGO_SECRET_KEY=your-secret-key
DB_NAME=helpdesk_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DEBUG=False
```

### Custom Settings
Edit `helpdesk/settings.py` for advanced configuration:
- Database settings
- Security options
- Email configuration
- Logging levels

## 📊 API Documentation

### Authentication Endpoints
```bash
POST /accounts/api/login/     # User login
POST /accounts/api/logout/    # User logout  
GET  /accounts/api/profile/   # User profile
POST /accounts/api/signup/    # User registration
```

### Ticket Endpoints
```bash
GET    /tickets/                    # List tickets
POST   /tickets/create/             # Create ticket
GET    /tickets/{id}/               # Ticket detail
POST   /tickets/{id}/change-status/ # Update status
POST   /tickets/{id}/comment/       # Add comment
```

## 🚀 Production Deployment

### Local Production (Current)
- Waitress WSGI server
- SQLite/PostgreSQL database
- File-based static serving
- Local environment variables

### Enterprise Production (Next Steps)
- Docker containerization
- External PostgreSQL cluster
- Redis caching
- Nginx reverse proxy
- SSL certificates
- Load balancing
- Monitoring (Prometheus/Grafana)

## 🧪 Development

### Local Development Mode
```bash
# Development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test
```

### Debug Mode
Set `DEBUG=True` in settings for development features:
- Detailed error pages
- Development toolbar
- Hot reloading
- Verbose logging

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📞 Support

- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Built-in help system
- **Admin Panel**: System health monitoring

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🎯 Ready to Use!

**Just run `start_production.bat` and you're ready to go!**

Your production-ready HelpDesk system will be available at:
**http://localhost:8000** 

Login with **admin / alpha123!** and start managing tickets! 🚀