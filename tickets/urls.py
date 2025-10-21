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
    # NOT:
    # Signup ve kullanıcı-grup yönetimi artık 'accounts' app'inde
    # --------------------------------------------------------------------------
]