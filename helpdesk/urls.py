#urls.py, gelen isteğin hangi view’a veya uygulamaya gideceğini belirleyen yönlendirme haritasıdır

from django.contrib import admin #django’nun admin panelini kullanmak için
from django.urls import path #URL desenlerini tanımlamak için kullanılan fonksiyon

urlpatterns = [ #django’nun URL yönlendirme listesi
    path('admin/', admin.site.urls), #URL’sine gelen istekleri Django admin paneline yönlendirir, http://localhost:8000/admin/
    #path('tickets/', include('tickets.urls')),
]                                   
