from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')  # CustomUser alanlarına göre ekleme yapabilirsin

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # Gerekirse diğer alanlar da eklenebilir

# Bu formlar Django'nun yerleşik UserCreationForm ve UserChangeForm'u genişleterek
# proje özel CustomUser modelini kullanır. Alanlar basit tutuldu; isterseniz
# role veya diğer özel alanları da ekleyebilirsiniz.