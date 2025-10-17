"""
urls.py
Gelen HTTP isteklerinin hangi view veya uygulamaya yönlendirileceğini belirler.
Proje genelinde URL haritası burada tanımlanır.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [

    # Django yönetim paneli

    path('admin/', admin.site.urls),

    # Ana sayfa yönlendirmesi (şu an sabit bir template gösteriyor)

    path('', TemplateView.as_view(template_name='tickets/home.html'), name='home'),

    # Tickets uygulamasına ait URL’ler

    path('tickets/', include('tickets.urls')),

    # Django’nun yerleşik kimlik doğrulama URL’leri (login, logout, password_reset vb.)

    path('accounts/', include('django.contrib.auth.urls')),
]