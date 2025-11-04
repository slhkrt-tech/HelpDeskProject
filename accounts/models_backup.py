# accounts/models.py
"""
Yardım Masası Kullanıcı Modelleri
===========================

- CustomUser: Rol tabanlı kullanıcı modeli (admin, support, customer)
- CustomAuthToken: Gelişmiş token authentication sistemi (tek token / kullanıcı)
- SystemSettings: Sistem ayarları (singleton)
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import secrets

# =======================================================================
# Kullanıcı Modeli
# =======================================================================

class CustomUser(AbstractUser):
    """
    Rol tabanlı kullanıcı modeli.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('support', 'Support'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer',
                            help_text="Kullanıcının sistemdeki rolü")

    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True,
                                    help_text="Kullanıcının dahil olduğu gruplar")
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_permissions_set',
                                              blank=True, help_text="Kullanıcının özel izinleri")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# =======================================================================
# Token Modeli
# =======================================================================

class CustomAuthToken(models.Model):
    """
    Kullanıcı başına tek token modeli.
    Token key, süre, son kullanım ve hash'lenmiş şifre içerir.
    """
    key = models.CharField(max_length=128, unique=True)
    user = models.OneToOneField(CustomUser, related_name='custom_auth_token',
                                on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    password_hash = models.CharField(max_length=255)  # Hash'lenmiş şifre
    created = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_used = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Custom Auth Token"
        verbose_name_plural = "Custom Auth Tokens"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        if not self.username:
            self.username = self.user.username
        super().save(*args, **kwargs)

    def generate_key(self):
        return secrets.token_urlsafe(64)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def refresh_token(self):
        self.key = self.generate_key()
        self.expires_at = timezone.now() + timedelta(days=7)
        self.save(update_fields=['key', 'expires_at'])
        return self.key

    def use_token(self):
        self.last_used = timezone.now()
        self.save(update_fields=['last_used'])

    def set_password_hash(self, raw_password):
        self.password_hash = make_password(raw_password)
        self.save(update_fields=['password_hash'])

    def __str__(self):
        return f"Custom Token for {self.username}"


# =======================================================================
# Sistem Ayarları Modeli (Singleton)
# =======================================================================

class SystemSettings(models.Model):
    """
    Sistem genel ayarları - tek kayıt (singleton)
    """
    site_name = models.CharField(max_length=200, default='Yardım Masası')
    site_description = models.TextField(default='Müşteri destek ve talep yönetim sistemi')
    admin_email = models.EmailField(default='admin@example.com')
    timezone = models.CharField(max_length=50, default='Europe/Istanbul')

    smtp_host = models.CharField(max_length=200, blank=True, null=True)
    smtp_port = models.PositiveIntegerField(default=587)
    smtp_username = models.CharField(max_length=200, blank=True, null=True)
    smtp_password = models.CharField(max_length=200, blank=True, null=True)
    smtp_use_tls = models.BooleanField(default=True)

    token_expiry_days = models.PositiveIntegerField(default=30)
    max_login_attempts = models.PositiveIntegerField(default=5)
    session_timeout_minutes = models.PositiveIntegerField(default=30)
    require_password_change = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return f"System Settings - {self.site_name}"

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings