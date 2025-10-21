# accounts/admin.py
# ================================================================================
# Django Admin Panel Configuration - Custom User Model
# CustomUser modeli için admin panel yapılandırması
# ================================================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, CustomAuthToken
from .forms import CustomUserCreationForm, CustomUserChangeForm

# ================================================================================
# Custom User Admin Configuration
# ================================================================================

class CustomUserAdmin(UserAdmin):
    """
    CustomUser modeli için özelleştirilmiş admin interface
    Rol tabanlı kullanıcı yönetimi ve gelişmiş filtreleme
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    # Liste görünümü - hangi alanlar gösterilecek
    list_display = ("username", "email", "role", "is_staff", "is_active", "is_superuser")
    list_filter = ("role", "is_staff", "is_active", "is_superuser", "groups")
    
    # Detay görünümü alanları
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Role & Groups", {"fields": ("role", "groups")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    
    # Yeni kullanıcı ekleme formu
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "password1", "password2", "is_staff", "is_active", "is_superuser", "groups"),
        }),
    )
    
    # Arama ve sıralama
    search_fields = ("username", "email", "role")
    ordering = ("username",)

# ================================================================================
# Custom Auth Token Admin Configuration
# ================================================================================

@admin.register(CustomAuthToken)
class CustomAuthTokenAdmin(admin.ModelAdmin):
    """
    Custom authentication token'lar için admin interface
    Token yönetimi ve güvenlik takibi
    """
    list_display = ('user', 'username', 'created', 'expires_at', 'last_used', 'is_active', 'is_expired')
    list_filter = ('is_active', 'created', 'expires_at')
    search_fields = ('user__username', 'username')
    readonly_fields = ('key', 'created', 'password_hash')
    ordering = ('-created',)

    def is_expired(self, obj):
        """Token'ın süresi dolmuş mu kontrolü"""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'

# Admin panel'i kaydet
admin.site.register(CustomUser, CustomUserAdmin)