# accounts/urls.py
# ================================================================================
# User Account Management URL Configuration  
# Kullanıcı hesapları, kimlik doğrulama ve yönetim panel'leri
# ================================================================================

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    # ================================
    # Authentication Views
    # ================================
    
    # Temel giriş/çıkış sistemi
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    
    # ================================
    # API Endpoints (Token-based)
    # ================================
    
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/safe-logout/', views.api_safe_logout, name='api_safe_logout'),
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/profile/', views.api_user_profile, name='api_user_profile'),
    
    # ================================
    # Role-Based Dashboard Panels
    # ================================
    
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('support-panel/', views.support_panel_view, name='support_panel'),
    path('customer-panel/', views.customer_panel_view, name='customer_panel'),
    
    # ================================
    # Admin Management Pages
    # ================================
    
    # Kullanıcı yönetimi
    path('admin/users/', views.admin_users_view, name='admin_users'),
    path('admin/users/create/', views.admin_user_create_view, name='admin_user_create'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit_view, name='admin_user_edit'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete_view, name='admin_user_delete'),
    
    # Grup yönetimi
    path('admin/groups/', views.admin_groups_view, name='admin_groups'),
    path('admin/groups/create/', views.admin_group_create_view, name='admin_group_create'),
    path('admin/groups/<int:group_id>/delete/', views.admin_group_delete_view, name='admin_group_delete'),
    path('admin/users/<int:user_id>/assign-groups/', views.admin_user_assign_groups_view, name='admin_user_assign_groups'),
    
    # Sistem ayarları
    path('admin/settings/', views.admin_settings_view, name='admin_settings'),
    path('admin/reports/', views.admin_reports_view, name='admin_reports'),
    
    # ================================
    # Customer Management Pages
    # ================================
    
    # Müşteri profil yönetimi
    path('customer/profile/', views.customer_profile_view, name='customer_profile'),
    path('customer/profile-edit/', views.customer_profile_edit_view, name='customer_profile_edit'),
    path('customer/change-password/', views.customer_change_password_view, name='customer_change_password'),
]