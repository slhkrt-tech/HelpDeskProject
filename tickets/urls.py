from django.urls import path

from . import views

urlpatterns = [

    # Ticket listesi
    # - Supervisor grubu veya admin tüm ticketları görebilir
    # - Normal kullanıcı sadece kendi grubundaki ticketları görebilir

    path("", views.ticket_list, name="ticket_list"),

    # Yeni ticket oluşturma
    # - Form gönderildiğinde ticket kaydedilir
    # - Oluşturan kullanıcı otomatik atanır
    path("create/", views.ticket_create, name="ticket_create"),

    # Ticket detay sayfası
    # - Normal kullanıcı sadece kendi ticketını görebilir
    # - Staff kullanıcılar status ve atama güncelleyebilir

    path("<int:pk>/", views.ticket_detail, name="ticket_detail"),

    # Kullanıcı kayıt (signup)
    # - Kayıt sonrası kullanıcı otomatik giriş yapar

    path("signup/", views.signup, name="signup"),

    # Kullanıcıyı bir gruba ekleme (yalnızca staff veya admin)

    path("user/<int:user_id>/add-group/", views.add_user_to_group, name="add_user_to_group"),
]
