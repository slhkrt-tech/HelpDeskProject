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
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    
    # Şifre sıfırlama sistemi
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete_view, name='password_reset_complete'),
    
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
    path('admin/users/<int:user_id>/assign-groups/', views.admin_user_assign_groups_view, name='admin_user_assign_groups'),
    
    # Grup ve yetki yönetimi
    path('admin/groups/', views.admin_groups_view, name='admin_groups'),
    path('admin/groups/create/', views.admin_group_create_view, name='admin_group_create'),
    path('admin/groups/<int:group_id>/edit/', views.admin_group_edit_view, name='admin_group_edit'),
    path('admin/groups/<int:group_id>/delete/', views.admin_group_delete_view, name='admin_group_delete'),
    path('admin/permissions/', views.admin_permissions_view, name='admin_permissions'),
    
    # Raporlar ve analitik
    path('admin/reports/', views.admin_reports_view, name='admin_reports'),
    path('admin/analytics/', views.admin_analytics_view, name='admin_analytics'),
    
    # Sistem yönetimi
    path('admin/settings/', views.admin_settings_view, name='admin_settings'),
    path('admin/logs/', views.admin_logs_view, name='admin_logs'),
    path('admin/tokens/', views.admin_tokens_view, name='admin_tokens'),
    path('admin/backup/', views.admin_backup_view, name='admin_backup'),
    path('admin/maintenance/', views.admin_maintenance_view, name='admin_maintenance'),
    
    # Hızlı işlemler
    path('admin/users/bulk-import/', views.admin_bulk_import_view, name='admin_bulk_import'),
    path('admin/notifications/', views.admin_notifications_view, name='admin_notifications'),
    path('admin/cache/', views.admin_cache_view, name='admin_cache'),
    path('admin/export/', views.admin_export_view, name='admin_export'),
    
    # ================================
    # Customer Management Pages
    # ================================
    
    # Müşteri profil yönetimi - Ana profile URL'i
    path('profile/', views.customer_profile_view, name='profile'),
    path('customer/profile/', views.customer_profile_view, name='customer_profile'),
    path('customer/profile-edit/', views.customer_profile_edit_view, name='customer_profile_edit'),
    path('customer/change-password/', views.customer_change_password_view, name='customer_change_password'),
    
    # ================================
    # API Endpoints
    # ================================
    
    path('api/signup/', views.signup_api_view, name='signup_api'),
]