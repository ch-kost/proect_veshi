"""Маршруты проекта и подключение приложений."""

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("items/", include("catalogue.urls")),
    path("owners/", include("owners.urls")),
    path("history/", include("history.urls")),
]

handler404 = "homepage.views.not_found"
