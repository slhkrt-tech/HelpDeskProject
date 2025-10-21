"""
urls.py
Tüm proje genelinde URL yönlendirmelerini tanımlar:
- Ana sayfa
- Tickets uygulaması
- Kullanıcı kimlik doğrulama (login/logout)
- Özelleştirilmiş admin panelleri
"""

from django.urls import include, path
from django.contrib.auth import views as auth_views
from accounts.views import home_view

urlpatterns = [

    # Ana sayfa (Token kontrolü ile role-based yönlendirme)
    path('', home_view, name='home'),

    # Tickets uygulaması

    path('tickets/', include('tickets.urls')),

    # Accounts uygulaması (tek login sistemi ve özelleştirilmiş admin paneller)
    
    path('accounts/', include('accounts.urls')),

    # Django auth URL'leri (password reset vb.) - Özelleştirilmiş
    path('auth/password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             success_url='/auth/password_reset/done/'
         ), 
         name='password_reset'),
    
    path('auth/password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('auth/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/auth/reset/done/'
         ), 
         name='password_reset_confirm'),
    
    path('auth/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]