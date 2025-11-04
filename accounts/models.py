# accounts/models.py
"""
HelpDesk Kullanıcı Modelleri
===========================

- CustomUser: Rol tabanlı kullanıcı modeli (admin, support, customer)
- CustomAuthToken: Gelişmiş token authentication sistemi, çoklu cihaz desteği
- SystemSettings: Sistem konfigürasyon ayarları (singleton)
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import secrets

# ================================================================================
# Kullanıcı Modeli
# ================================================================================

class CustomUser(AbstractUser):
    """
    Django'nun varsayılan kullanıcı modelini genişleten özel kullanıcı sınıfı.
    """

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

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='Bu kullanıcının ait olduğu gruplar.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Bu kullanıcının sahip olduğu özel izinler.',
        verbose_name='user permissions',
    )

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        db_table = 'accounts_customuser'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def get_full_name_or_username(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username
    
    def save(self, *args, **kwargs):
        # Superuser'lar için admin role'ünü zorla
        if self.is_superuser:
            self.role = 'admin'
        
        # Mevcut admin kullanıcısının role'ünü değiştirmeyi engelle
        if self.pk and self.is_superuser:
            try:
                old_instance = CustomUser.objects.get(pk=self.pk)
                if old_instance.is_superuser and old_instance.role == 'admin':
                    self.role = 'admin'  # Admin role'ünü koru
            except CustomUser.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)

# ================================================================================
# Token Modeli (Çoklu cihaz desteği ile)
# ================================================================================

class CustomAuthToken(models.Model):
    """
    Gelişmiş authentication token modeli.
    Çoklu cihaz destekli, kullanıcı başına birden fazla token.
    """
    
    key = models.CharField(
        max_length=128, 
        unique=True,
        help_text="Token için benzersiz anahtar"
    )
    
    user = models.ForeignKey(
        CustomUser, 
        related_name='auth_tokens',
        on_delete=models.CASCADE,
        help_text="Token'ın sahibi olan kullanıcı"
    )
    
    device_name = models.CharField(
        max_length=100,
        default='Unknown device',
        help_text="Token hangi cihaz için oluşturuldu"
    )

    created = models.DateTimeField(auto_now_add=True, help_text="Token oluşturulma tarihi")
    expires_at = models.DateTimeField(help_text="Token'ın geçerlilik süresi")
    last_used = models.DateTimeField(null=True, blank=True, help_text="Son kullanım tarihi")
    is_active = models.BooleanField(default=True, help_text="Token aktif mi?")
    
    # Opsiyonel şifre hash alanı (isteğe bağlı)
    password_hash = models.CharField(max_length=255, blank=True, help_text="Hash'lenmiş şifre")

    class Meta:
        verbose_name = "Auth Token"
        verbose_name_plural = "Auth Tokens"
        db_table = 'accounts_customauthtoken'
        ordering = ['-created']

    def save(self, *args, **kwargs):
        # Token key yoksa oluştur
        if not self.key:
            self.key = self.generate_key()
        # Süre sonu yoksa varsayılan 7 gün
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
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
        return f"Token for {self.user.username} ({self.device_name})"

# ================================================================================
# Sistem Ayarları Modeli (Singleton)
# ================================================================================

class SystemSettings(models.Model):
    """
    Sistem ayarları tablosu - tek kayıt (singleton) kullanılır.
    """

    site_name = models.CharField(max_length=200, default='Yardım Masası', help_text="Sitenin adı")
    site_description = models.TextField(default='Müşteri destek ve talep yönetim sistemi', help_text="Site açıklaması")
    admin_email = models.EmailField(default='admin@example.com', help_text="Sistem yöneticisi e-posta adresi")
    timezone = models.CharField(max_length=50, default='Europe/Istanbul', help_text="Sistem zaman dilimi")

    smtp_host = models.CharField(max_length=200, blank=True, null=True, help_text="SMTP sunucu adresi")
    smtp_port = models.PositiveIntegerField(default=587, help_text="SMTP port")
    smtp_username = models.CharField(max_length=200, blank=True, null=True, help_text="SMTP kullanıcı adı")
    smtp_password = models.CharField(max_length=200, blank=True, null=True, help_text="SMTP şifresi")
    smtp_use_tls = models.BooleanField(default=True, help_text="TLS kullanımı")

    token_expiry_days = models.PositiveIntegerField(default=30, help_text="Token geçerlilik süresi (gün)")
    max_login_attempts = models.PositiveIntegerField(default=5, help_text="Maks giriş denemesi")
    session_timeout_minutes = models.PositiveIntegerField(default=30, help_text="Oturum zaman aşımı")
    require_password_change = models.BooleanField(default=False, help_text="İlk girişte şifre değişimi zorunlu mu?")
    enable_2fa = models.BooleanField(default=False, help_text="İki faktörlü kimlik doğrulama aktif mi?")

    created_at = models.DateTimeField(auto_now_add=True, help_text="Oluşturulma tarihi")
    updated_at = models.DateTimeField(auto_now=True, help_text="Son güncelleme tarihi")
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, help_text="Son güncelleyen kullanıcı")

    class Meta:
        verbose_name = 'Sistem Ayarları'
        verbose_name_plural = 'Sistem Ayarları'
        db_table = 'accounts_systemsettings'

    def __str__(self):
        return f"Sistem Ayarları - {self.site_name}"

    def save(self, *args, **kwargs):
        # Singleton kontrolü
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

# ================================================================================
# Sistem Log Modeli
# ================================================================================

class SystemLog(models.Model):
    """
    Sistem aktivite logları
    """
    
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Bilgi'),
        ('WARNING', 'Uyarı'),
        ('ERROR', 'Hata'),
        ('CRITICAL', 'Kritik'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Zaman")
    level = models.CharField(max_length=10, choices=LOG_LEVELS, default='INFO', verbose_name="Seviye")
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kullanıcı")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")
    action = models.CharField(max_length=100, verbose_name="İşlem")
    message = models.TextField(verbose_name="Mesaj")
    extra_data = models.JSONField(null=True, blank=True, verbose_name="Ek Veri")
    
    class Meta:
        verbose_name = 'Sistem Logu'
        verbose_name_plural = 'Sistem Logları'
        ordering = ['-timestamp']
        db_table = 'accounts_systemlog'
    
    def __str__(self):
        return f"[{self.level}] {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @classmethod
    def log(cls, level, action, message, user=None, ip_address=None, extra_data=None):
        """
        Log kaydı oluşturma yardımcı metodu
        """
        return cls.objects.create(
            level=level,
            action=action,
            message=message,
            user=user,
            ip_address=ip_address,
            extra_data=extra_data
        )