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

from tickets import admin_views as admin_panel_views
from django.contrib.auth import views as auth_views

urlpatterns = [

    # Admin paneli (varsayılan /admin/ yolunu özel panele yönlendiriyoruz)
    # Not: admin uygulaması hâlâ kurulu, sadece URL yönlendirmesi yapıyoruz.
    # Yönlendirme artık yeni özel admin paneline
    path('admin/', RedirectView.as_view(url='/admin-panel/', permanent=False)),

    # Yeni özel admin paneli (bağımsız): index + alt bölümler
    path('admin-panel/', admin_panel_views.admin_index, name='admin_index'),
    path('admin-panel/login/', auth_views.LoginView.as_view(template_name='registration/login_admin.html'), name='admin_login'),
    path('admin-panel/tickets/', admin_panel_views.panel_list, name='admin_tickets'),
    path('admin-panel/tickets/<int:pk>/', admin_panel_views.panel_detail, name='admin_ticket_detail'),
    path('admin-panel/users/', admin_panel_views.users_list, name='admin_users'),
    path('admin-panel/users/<int:pk>/edit/', admin_panel_views.user_edit, name='admin_user_edit'),
    path('admin-panel/groups/', admin_panel_views.groups_list, name='admin_groups'),
    path('admin-panel/comments/', admin_panel_views.comments_list, name='admin_comments'),
    path('admin-panel/comments/<int:pk>/delete/', admin_panel_views.comment_delete, name='admin_comment_delete'),
    path('admin-panel/comments/<int:pk>/restore/', admin_panel_views.comment_restore, name='admin_comment_restore'),

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
