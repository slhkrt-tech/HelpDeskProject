#django.contrib.auth.urls sayesinde login/ logout/ password view'ları hazır kullanılır.
#from django.contrib import admin #django admin paneli

from django.urls import path #URL tanımlama ve başka URLconf’leri dahil etme
from . import views
from django.views.generic import TemplateView #statik bir HTML sayfası göstermek için

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"), #tüm ticket’ları listeleyen view
    path("create/", views.ticket_create, name="ticket_create"), #yeni ticket oluşturma formu
    path("<int:pk>/", views.ticket_detail, name="ticket_detail"), #ID’ye göre ticket detay sayfası
]