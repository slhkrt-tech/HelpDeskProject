@echo off
REM Alpha Production Server Startup Script (Windows)
REM HelpDesk Alpha Release - Gunicorn Production Server

echo 🚀 HelpDesk Alpha Production Server
echo ===================================

REM Check if in virtual environment
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  Warning: Not in virtual environment
    echo    Consider activating venv first
    echo.
)

REM Environment setup
echo 📋 Setting up Alpha Production environment...
set DJANGO_SECRET_KEY=alpha-prod-helpdesk-2025-secure-key
set DEBUG=False
set ALPHA_MODE=True

REM Install production dependencies
echo 📦 Installing production dependencies...
pip install -r requirements_production.txt

REM Database setup
echo 🗄️  Database migration...
python manage.py migrate --noinput

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

REM Create logs directory
if not exist logs mkdir logs
if not exist logs\gunicorn_error.log echo. > logs\gunicorn_error.log
if not exist logs\gunicorn_access.log echo. > logs\gunicorn_access.log

REM Alpha production setup
echo 👤 Alpha production setup...
python manage.py alpha_production --setup

echo ✅ Alpha Production server ready!
echo.
echo 🌐 Starting Waitress production server (Windows optimized)...
echo 📍 Access at: http://localhost:8000
@echo off
REM HelpDesk System - One-Click Production Deployment
REM Download from GitHub and run locally with production settings

echo.
echo 🎫 HelpDesk System - Production Deployment
echo ==========================================
echo.

REM Check Python
echo 🐍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version

echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo 🗄️  Setting up database...
python manage.py migrate --noinput
if errorlevel 1 (
    echo ❌ Database setup failed!
    pause
    exit /b 1
)

echo.
echo � Creating admin user and setting up system...
python manage.py alpha_production --setup
if errorlevel 1 (
    echo ❌ Setup failed!
    pause
    exit /b 1
)

echo.
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ✅ HelpDesk Production Setup Complete!
echo.
echo 🌐 Starting production server...
echo.
echo 📍 URL: http://localhost:8000
echo 👤 Admin: admin / alpha123!
echo 🛑 Stop: Ctrl+C
echo.
echo ==========================================

REM Start production server
python production_server.py

echo.
echo 🛑 HelpDesk server stopped.
echo Thank you for using HelpDesk System!
pause
echo  Stop server: Ctrl+C
echo.

REM Start Waitress server (Windows compatible)
python production_server.py

echo.
echo 🛑 Alpha Production server stopped.
pause