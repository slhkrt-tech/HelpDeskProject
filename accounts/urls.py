"""accounts uygulaması için kimlik doğrulama URL'leri.

Bu modülde login/logout gibi temel auth yolları tanımlıdır.
"""

from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
