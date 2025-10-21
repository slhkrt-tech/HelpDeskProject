# tickets/urls.py  
# ================================================================================
# Ticket Management URL Configuration
# Talep yönetimi için URL pattern'ları
# ================================================================================

from django.urls import path
from . import views

urlpatterns = [
    
    # Ticket listesi - Ana sayfa
    path("", views.ticket_list, name="ticket_list"),

    # Yeni ticket oluşturma
    path("create/", views.ticket_create, name="ticket_create"),

    # Ticket detay sayfası ve yorum ekleme
    path("<int:pk>/", views.ticket_detail, name="ticket_detail"),
    
    # Ticket durum değiştirme (AJAX) - Admin/Support only
    path("<int:pk>/change-status/", views.change_ticket_status, name="change_ticket_status"),

    # NOT: signup ve user group management artık accounts app'inde
]