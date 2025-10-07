#django.contrib.auth.urls sayesinde login/ logout/ password view'ları hazır kullanılır.

from django.contrib import admin #django admin paneli
from django.urls import path, include #URL tanımlama ve başka URLconf’leri dahil etme
from django.views.generic import TemplateView #statik bir HTML sayfası göstermek için

urlpatterns = [
    path("admin/", admin.site.urls), #admin paneline yönlendirir
    path("", TemplateView.as_view(template_name="tickets/home.html"), name="home"), #anasayfa olarak tickets/home.html gösterilir
    path("tickets/", include("tickets.urls")), #tickets uygulamasının kendi urls.py dosyasını dahil eder
    path("accounts/", include("django.contrib.auth.urls")),  # login/logout hazır view'lar
]
from django.urls import path
from . import views #URL’lere yönlendirilecek fonksiyon veya class-based view’lar

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"), #tüm ticket’ları listeleyen view
    path("create/", views.ticket_create, name="ticket_create"), #yeni ticket oluşturma formu
    path("<int:pk>/", views.ticket_detail, name="ticket_detail"), #ID’ye göre ticket detay sayfası
]
