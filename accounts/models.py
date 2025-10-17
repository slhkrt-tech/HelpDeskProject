from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

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