from django.contrib import admin
from django.urls import path, include
from operacional.views import home, cadastros

urlpatterns = [
    path("", home, name="home"),
    path("cadastros/", cadastros, name="cadastros"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("painel/", include("operacional.urls")),
]