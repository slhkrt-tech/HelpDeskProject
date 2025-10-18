"""accounts uygulaması için kimlik doğrulama URL'leri.

Bu modülde login/logout gibi temel auth yolları tanımlıdır.
"""

from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]