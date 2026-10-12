"""Адреса списка и карточки владельца."""

from django.urls import path

from . import views

app_name = "owners"
urlpatterns = [
    path("", views.owner_list, name="list"),
    path("<int:owner_id>/", views.owner_detail, name="detail"),
]
