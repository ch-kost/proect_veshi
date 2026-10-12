"""Показ истории владения предметами."""

from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.views.decorators.http import require_safe

from homepage.views import page
from web_data import load_project_data


@require_safe
def period_list(request: HttpRequest) -> HttpResponse:
    """Показать все периоды и их состояние."""
    _, _, periods = load_project_data()
    entries = format_html_join(
        "", '<li><a href="{}">{} — {}</a> <strong>{}</strong></li>',
        (
            (reverse("history:detail", args=[period.id]),
             period.item.name, period.owner.name,
             "Текущий" if period.is_active else "Завершен")
            for period in periods
        ),
    )
    return HttpResponse(page("История владения", format_html(
        '<h1>Периоды владения</h1><ul>{}</ul>', entries
    )))


@require_safe
def period_detail(request: HttpRequest, period_id: int) -> HttpResponse:
    """Показать период, предмет, владельца и даты."""
    _, _, periods = load_project_data()
    period = next((entry for entry in periods if entry.id == period_id), None)
    if period is None:
        raise Http404("Период владения не найден.")
    content = format_html(
        '<h1>Период владения №{}</h1><p>Предмет: <a href="{}">{}</a></p>'
        '<p>Владелец: <a href="{}">{}</a></p><p>{}</p>'
        '<p>Состояние: {}</p><a href="{}">К истории</a>',
        period.id, reverse("catalogue:detail", args=[period.item.id]),
        period.item.name, reverse("owners:detail", args=[period.owner.id]),
        period.owner.name, period,
        "Текущий" if period.is_active else "Завершен",
        reverse("history:list"),
    )
    return HttpResponse(page("Период владения", content))
