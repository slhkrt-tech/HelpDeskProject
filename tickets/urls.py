from django.urls import path
from . import views

urlpatterns = [

    # Ticket listesi sayfası
    # - Supervisor grubu tüm ticketları görebilir
    # - Normal kullanıcı sadece kendi grubundaki ticketları görebilir

    path("", views.ticket_list, name="ticket_list"),

    # Yeni ticket oluşturma sayfası
    # - Form gönderildiğinde ticket kaydedilir
    # - Oluşturan kullanıcı otomatik atanır

    path("create/", views.ticket_create, name="ticket_create"),

    # Ticket detay sayfası
    # - Normal kullanıcı sadece kendi ticketını görebilir
    # - Staff kullanıcılar status ve atama güncelleyebilir

    path("<int:pk>/", views.ticket_detail, name="ticket_detail"),

    # Kullanıcı kayıt (signup) sayfası
    # - Kayıt sonrası kullanıcı otomatik giriş yapar
    
    path("signup/", views.signup, name="signup"),
]