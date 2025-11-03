# tickets/urls.py
# ================================================================================
# Ticket Yönetimi URL Konfigürasyonu
# Talep (ticket) yönetimi için URL pattern'ları
# ================================================================================

from django.urls import path
from . import views

urlpatterns = [
    # --------------------------------------------------------------------------
    # Ticket Listesi - Ana Sayfa
    # --------------------------------------------------------------------------
    path("", views.ticket_list, name="ticket_list"),

    # --------------------------------------------------------------------------
    # Yeni Ticket Oluşturma
    # --------------------------------------------------------------------------
    path("create/", views.ticket_create, name="ticket_create"),

    # --------------------------------------------------------------------------
    # Ticket Detay Sayfası ve Yorum Ekleme
    # --------------------------------------------------------------------------
    path("<int:pk>/", views.ticket_detail, name="ticket_detail"),
    
    # --------------------------------------------------------------------------
    # Ticket Durum Değiştirme (AJAX)
    # Sadece Admin/Support kullanıcılar tarafından erişilebilir
    # --------------------------------------------------------------------------
    path("<int:pk>/change-status/", views.change_ticket_status, name="change_ticket_status"),
    
    # --------------------------------------------------------------------------
    # Ticket Atama Güncelleme (AJAX)
    # Sadece Admin/Support kullanıcılar tarafından erişilebilir
    # --------------------------------------------------------------------------
    path("<int:pk>/update-assignment/", views.update_ticket_assignment, name="update_ticket_assignment"),

    # --------------------------------------------------------------------------
    # Admin ve Kategori Yönetimi
    # --------------------------------------------------------------------------
    path("admin/", views.tickets_admin_view, name="tickets_admin"),
    path("categories/", views.ticket_categories_view, name="ticket_categories"),
    
    # --------------------------------------------------------------------------
    # Ticket Durum Güncelleme (AJAX) - Yeni Endpoint
    # --------------------------------------------------------------------------
    path("update-status/", views.update_ticket_status, name="update_ticket_status"),

    # --------------------------------------------------------------------------
    # NOT:
    # Signup ve kullanıcı-grup yönetimi artık 'accounts' app'inde
    # --------------------------------------------------------------------------
]