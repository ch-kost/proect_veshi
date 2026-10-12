"""Адреса списка и карточки периода."""

from django.urls import path

from . import views

app_name = "history"
urlpatterns = [
    path("", views.period_list, name="list"),
    path("<int:period_id>/", views.period_detail, name="detail"),
]
