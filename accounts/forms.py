from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')  # CustomUser alanlarına göre ekleme yapabilirsiniz


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # Gerekirse diğer alanları da ekleyin

# Bu formlar, Django'nun yerleşik UserCreationForm ve UserChangeForm'u genişleterek
# proje özel CustomUser modelini kullanır. Alanlar kasıtlı olarak basit tutulmuştur;
# ihtiyaç halinde role veya diğer özel alanlar eklenebilir.
