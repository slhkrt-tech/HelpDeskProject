"""
urls.py
Tüm proje genelinde URL yönlendirmelerini tanımlar:
- Admin paneli
- Ana sayfa
- Tickets uygulaması
- Kullanıcı kimlik doğrulama (login/logout)
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView, RedirectView

urlpatterns = [

    # Admin paneli (varsayılan /admin/ yolunu özel panele yönlendiriyoruz)
    # Not: admin uygulaması hâlâ kurulu, sadece URL yönlendirmesi yapıyoruz.
    path('admin/', RedirectView.as_view(url='/tickets/panel/', permanent=False)),

    # Ana sayfa

    path('', TemplateView.as_view(template_name='tickets/home.html'), name='home'),

    # Tickets uygulaması

    path('tickets/', include('tickets.urls')),

    # Kimlik doğrulama (login/logout)

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Diğer Django auth URL'leri (password reset vb.)

    path('accounts/', include('django.contrib.auth.urls')),
]
