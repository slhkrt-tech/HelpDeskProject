#!/bin/bash
# Alpha Production Server Startup Script (Linux/Mac)
# HelpDesk Alpha Release - Gunicorn Production Server

echo "🚀 HelpDesk Alpha Production Server"
echo "==================================="

# Check if in virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Not in virtual environment"
    echo "   Consider activating venv first"
    echo
fi

# Environment setup
echo "📋 Setting up Alpha Production environment..."
export DJANGO_SECRET_KEY="alpha-prod-helpdesk-2025-secure-key"
export DEBUG="False"
export ALPHA_MODE="True"

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements_production.txt

# Database setup
echo "🗄️  Database migration..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create logs directory
echo "📄 Setting up logs..."
mkdir -p logs
touch logs/gunicorn_error.log
touch logs/gunicorn_access.log

# Alpha production setup
echo "👤 Alpha production setup..."
python manage.py alpha_production --setup

echo "✅ Alpha Production server ready!"
echo
echo "🌐 Starting Gunicorn production server..."
echo "📍 Access at: http://localhost:8000"
echo "🔑 Admin credentials: admin / alpha123!"
echo "📊 Server logs: logs/gunicorn_*.log"
echo "🛑 Stop server: Ctrl+C"
echo

# Start Gunicorn server
gunicorn --config gunicorn.conf.py helpdesk.wsgi:application

echo
echo "🛑 Alpha Production server stopped."