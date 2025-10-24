@echo off
REM Alpha Production Deployment Script (Windows)
REM HelpDesk Alpha Release - Local Production Setup

echo 🚀 HelpDesk Alpha Production Deployment
echo ========================================

REM Environment setup
echo 📋 Setting up Alpha Production environment...
set DJANGO_SECRET_KEY=alpha-prod-helpdesk-2025-secure-key
set DEBUG=False
set ALPHA_MODE=True

REM Check Python version
echo 🐍 Checking Python version...
python --version

REM Install/Update dependencies
echo 📦 Installing production dependencies...
pip install -r requirements.txt

REM Database setup
echo 🗄️  Setting up database...
python manage.py makemigrations
python manage.py migrate

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

REM Create superuser (if needed)
echo 👤 Creating superuser (if needed)...
echo from accounts.models import CustomUser; CustomUser.objects.filter(is_superuser=True).exists() or CustomUser.objects.create_superuser('admin', 'admin@helpdesk-alpha.local', 'alpha123!', role='admin') | python manage.py shell

REM Security check
echo 🔒 Running security checks...
python manage.py check --deploy

REM Create logs directory
if not exist logs mkdir logs
if not exist logs\django.log echo. > logs\django.log
if not exist logs\security.log echo. > logs\security.log

echo ✅ Alpha Production deployment completed!
echo.
echo 🌐 Starting Alpha Production server...
echo 📍 Access at: http://localhost:8000
echo 🔑 Admin credentials: admin / alpha123!
echo.

REM Start server
python manage.py runserver 0.0.0.0:8000

pause