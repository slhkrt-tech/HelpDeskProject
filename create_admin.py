#!/usr/bin/env python
"""
Admin kullanıcı oluşturma aracı
Kullanım: python create_admin.py
"""

import os
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
django.setup()

from accounts.models import CustomUser


def create_admin_user():
    """Admin kullanıcı oluşturur, eğer kullanıcı zaten varsa uyarı verir."""

    try:
        # Kullanıcıdan bilgi al
        username = input("🧩 Admin kullanıcı adı: ").strip()
        email = input("📧 Email adresi: ").strip()
        password = input("🔑 Şifre: ").strip()

        # Boş alan kontrolü
        if not username or not email or not password:
            print("⚠️  Boş alan bırakma, tekrar dene.")
            return

        # Aynı kullanıcı var mı?
        if CustomUser.objects.filter(username=username).exists():
            print(f"⚠️  '{username}' adlı kullanıcı zaten mevcut.")
            return

        # Yeni admin kullanıcı oluştur
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='admin',
            is_active=True,
        )

        # Başarı mesajı
        print("\n✅ Admin kullanıcısı başarıyla oluşturuldu!\n")
        print(f"Kullanıcı adı : {user.username}")
        print(f"E-posta       : {user.email}")
        print(f"Rol           : {user.role}")
        print(f"Durum         : {'Aktif' if user.is_active else 'Pasif'}")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")


if __name__ == "__main__":
    # Script doğrudan çalıştırıldığında admin oluştur
    create_admin_user()