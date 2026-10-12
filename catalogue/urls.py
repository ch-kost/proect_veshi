"""Адреса списка и карточки предмета."""

from django.urls import path

from . import views

app_name = "catalogue"
urlpatterns = [
    path("", views.item_list, name="list"),
    path("<int:item_id>/", views.item_detail, name="detail"),
]
