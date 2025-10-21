# accounts/forms.py
# ================================================================================
# Django Forms - Custom User Model Forms
# Kullanıcı oluşturma ve düzenleme formları
# ================================================================================

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    Yeni kullanıcı oluşturma formu
    Django'nun varsayılan UserCreationForm'unun CustomUser modeline uyarlanmış hali
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'role')  # Role alanı eklendi
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Form alanlarına Bootstrap sınıfları ekle
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CustomUserChangeForm(UserChangeForm):
    """
    Mevcut kullanıcı düzenleme formu
    Admin panelinde ve kullanıcı profil sayfalarında kullanılır
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'first_name', 'last_name')  # Gerekli alanlar
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Form alanlarına Bootstrap sınıfları ekle
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'