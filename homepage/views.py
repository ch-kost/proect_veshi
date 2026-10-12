"""Главная страница и шаблоны ошибок на этапе ПР6."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from services import ownership_statistics, sort_items
from web_data import load_project_data


@require_safe
def index(request: HttpRequest) -> HttpResponse:
    """Передать статистику и предметы в шаблон главной страницы."""
    items, owners, _ = load_project_data()
    context = {
        "stats": ownership_statistics(items, owners),
        "items": sort_items(items)[:3],
    }
    return render(request, "homepage/index.html", context)


def not_found(
    request: HttpRequest, exception: Exception | None = None
) -> HttpResponse:
    """Показать собственную страницу HTTP 404."""
    return render(request, "404.html", status=404)


def service_unavailable(request: HttpRequest) -> HttpResponse:
    """Показать понятное сообщение об ошибке чтения JSON."""
    context = {
        "message": "Не удалось прочитать JSON-файлы. "
        "Проверьте данные проекта и обновите страницу.",
    }
    return render(request, "503.html", context, status=503)
