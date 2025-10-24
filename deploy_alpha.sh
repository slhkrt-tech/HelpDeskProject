#!/bin/bash
# Alpha Production Deployment Script
# HelpDesk Alpha Release - Local Production Setup

echo "🚀 HelpDesk Alpha Production Deployment"
echo "========================================"

# Environment setup
echo "📋 Setting up Alpha Production environment..."
export DJANGO_SECRET_KEY="alpha-prod-helpdesk-2025-secure-key"
export DEBUG="False"
export ALPHA_MODE="True"

# Check Python version
echo "🐍 Checking Python version..."
python --version

# Install/Update dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements.txt

# Database setup
echo "🗄️  Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser (if needed)
echo "👤 Creating superuser (if needed)..."
echo "from accounts.models import CustomUser; CustomUser.objects.filter(is_superuser=True).exists() or CustomUser.objects.create_superuser('admin', 'admin@helpdesk-alpha.local', 'alpha123!', role='admin')" | python manage.py shell

# Security check
echo "🔒 Running security checks..."
python manage.py check --deploy

# Create logs directory
mkdir -p logs
touch logs/django.log
touch logs/security.log

echo "✅ Alpha Production deployment completed!"
echo ""
echo "🌐 Starting Alpha Production server..."
echo "📍 Access at: http://localhost:8000"
echo "🔑 Admin credentials: admin / alpha123!"
echo ""

# Start server
python manage.py runserver 0.0.0.0:8000