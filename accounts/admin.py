from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# CustomUser modelini Django admin paneline kaydediyoruz.
# UserAdmin, Django'nun yerleşik kullanıcı yönetimi arayüzünü kullanmamızı sağlar.
# Eğer CustomUser modelinde ek alanlar varsa (örneğin telefon, rol vs),
# bunları görüntülemek için UserAdmin özelleştirilebilir.

admin.site.register(CustomUser, UserAdmin)