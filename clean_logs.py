#!/usr/bin/env python
"""
Django Log Temizleme Script'i
HelpDesk projesi için log ve cache temizliği yapar
"""

import os
import sys
import django
from pathlib import Path

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from accounts.models import CustomAuthToken
from django.utils import timezone
from datetime import timedelta

def clean_logs():
    """Log dosyalarını temizle"""
    log_files = [
        'logs/django.log',
        'logs/security.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write('')
            print(f"✓ {log_file} temizlendi")

def clean_expired_sessions():
    """Eski session'ları temizle"""
    expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
    count = expired_sessions.count()
    expired_sessions.delete()
    print(f"✓ {count} adet eski session silindi")

def clean_expired_tokens():
    """Eski custom token'ları temizle"""
    expired_tokens = CustomAuthToken.objects.filter(expires_at__lt=timezone.now())
    count = expired_tokens.count()
    expired_tokens.delete()
    print(f"✓ {count} adet eski token silindi")

def clean_old_tokens(days=7):
    """X günden eski kullanılmayan token'ları temizle"""
    cutoff_date = timezone.now() - timedelta(days=days)
    old_tokens = CustomAuthToken.objects.filter(
        last_used__lt=cutoff_date
    ).exclude(last_used__isnull=True)
    count = old_tokens.count()
    old_tokens.delete()
    print(f"✓ {count} adet {days} günden eski token silindi")

if __name__ == "__main__":
    print("=== HelpDesk Log ve Cache Temizliği ===\n")
    
    clean_logs()
    clean_expired_sessions()
    clean_expired_tokens()
    clean_old_tokens(7)
    
    print(f"\n✅ Temizlik tamamlandı - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")