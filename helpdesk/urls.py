#urls.py, gelen isteğin hangi view’a veya uygulamaya gideceğini belirleyen yönlendirme haritasıdır

from django.contrib import admin #django’nun admin panelini kullanmak için
from django.urls import include, path #URL desenlerini tanımlamak için kullanılan fonksiyon
from django.views.generic import TemplateView

urlpatterns = [ #django’nun URL yönlendirme listesi
    path('admin/', admin.site.urls), #URL’sine gelen istekleri Django admin paneline yönlendirir, http://localhost:8000/admin/
    path('', TemplateView.as_view(template_name='tickets/home.html'), name='home'),
    path('tickets/', include('tickets.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]                                   
