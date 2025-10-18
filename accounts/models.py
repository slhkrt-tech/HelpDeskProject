from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# CustomUser: Django'nun AbstractUser sınıfını genişletir.
# Projenin kullanıcı modeline "role" alanı eklenmiştir (admin/support/customer).
# Ayrıca groups ve user_permissions ilişkilerinde related_name kullanılarak
# admin arayüzünde isim çakışmaları önlenir.
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

    # Kullanıcının dahil olduğu gruplar (related_name ile çakışma önlendi).
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text="Kullanıcının dahil olduğu gruplar."
    )

    # Kullanıcının özel izinleri.
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',
        blank=True,
        help_text="Kullanıcının sahip olduğu özel izinler."
    )

    def __str__(self):
        # Admin panelinde ve debug çıktılarında daha anlamlı gösterim sağlar.
        return f"{self.username} ({self.get_role_display()})"