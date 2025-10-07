#django.contrib.auth.urls sayesinde login/ logout/ password view'ları hazır kullanılır.
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="tickets/home.html"), name="home"),
    path("tickets/", include("tickets.urls")),
    path("accounts/", include("django.contrib.auth.urls")),  # login/logout hazır view'lar
]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path("create/", views.ticket_create, name="ticket_create"),
    path("<int:pk>/", views.ticket_detail, name="ticket_detail"),
]
