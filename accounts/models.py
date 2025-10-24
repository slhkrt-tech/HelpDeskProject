from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import secrets

# Django'nun varsayılan kullanıcı modelini genişleten özel kullanıcı sınıfı.
# Yeni kullanıcı rolleri tanımlanır (admin, support, customer).
# Grup ve izin ilişkileri yeniden tanımlanarak isim çakışmaları önlenir.

class CustomUser(AbstractUser):

    # Kullanıcının sistemdeki rolünü belirtir.

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('support', 'Support'),
        ('customer', 'Customer'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='customer',
        help_text="Kullanıcının sistemdeki rolünü belirtir."
    )

    # Django'nun yerleşik 'groups' alanı yeniden tanımlandı.
    # related_name parametresi, ters ilişki adının diğer modellerle çakışmaması için değiştirildi.

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text="Kullanıcının dahil olduğu gruplar."
    )

    # Kullanıcının sahip olduğu özel izinler.
    # related_name yine çakışmayı önlemek için değiştirildi.

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',
        blank=True,
        help_text="Kullanıcının sahip olduğu özel izinler."
    )

    def __str__(self):

        # Admin panelinde kullanıcı nesneleri anlamlı görünsün diye

        return f"{self.username} ({self.get_role_display()})"


class CustomAuthToken(models.Model):
    """
    Gelişmiş authentication token modeli
    Kullanıcı bilgileri ve süre sonu dahil
    """
    key = models.CharField(max_length=128, unique=True)
    user = models.OneToOneField(
        'CustomUser', 
        related_name='custom_auth_token',
        on_delete=models.CASCADE
    )
    username = models.CharField(max_length=150)
    password_hash = models.CharField(max_length=255)  # Hashed password
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
            # Token 7 gün geçerli (güvenlik için kısaltıldı)
            self.expires_at = timezone.now() + timedelta(days=7)
        if not self.username:
            self.username = self.user.username
        super().save(*args, **kwargs)
    
    def generate_key(self):
        return secrets.token_urlsafe(64)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def refresh_token(self):
        """Token'ı yenile"""
        self.key = self.generate_key()
        self.expires_at = timezone.now() + timedelta(days=7)  # 7 gün
        self.save()
        return self.key
    
    def use_token(self):
        """Token kullanıldığını kaydet"""
        self.last_used = timezone.now()
        self.save()
    
    def set_password_hash(self, raw_password):
        """Şifreyi hash'le ve kaydet"""
        self.password_hash = make_password(raw_password)
    
    def __str__(self):
        return f"Custom Token for {self.username}"


class SystemSettings(models.Model):
    """
    Sistem ayarları tablosu - Admin panel ayarları
    """
    # Genel ayarlar
    site_name = models.CharField(max_length=200, default='Yardım Masası')
    site_description = models.TextField(default='Müşteri destek ve talep yönetim sistemi')
    admin_email = models.EmailField(default='admin@example.com')
    timezone = models.CharField(max_length=50, default='Europe/Istanbul')
    
    # E-posta ayarları
    smtp_host = models.CharField(max_length=200, blank=True, null=True)
    smtp_port = models.PositiveIntegerField(default=587)
    smtp_username = models.CharField(max_length=200, blank=True, null=True)
    smtp_password = models.CharField(max_length=200, blank=True, null=True)
    smtp_use_tls = models.BooleanField(default=True)
    
    # Güvenlik ayarları
    token_expiry_days = models.PositiveIntegerField(default=30)
    max_login_attempts = models.PositiveIntegerField(default=5)
    session_timeout_minutes = models.PositiveIntegerField(default=30)
    require_password_change = models.BooleanField(default=False)
    
    # Meta bilgiler
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
        """Singleton pattern - tek bir settings instance döndür"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings