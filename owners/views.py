"""Показ владельцев и связанных с ними предметов."""

from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.views.decorators.http import require_safe

from homepage.views import page
from web_data import load_project_data


@require_safe
def owner_list(request: HttpRequest) -> HttpResponse:
    """Показать список владельцев."""
    _, owners, _ = load_project_data()
    entries = format_html_join(
        "", '<li><a href="{}">{}</a></li>',
        (
            (reverse("owners:detail", args=[owner.id]), owner.name)
            for owner in owners
        ),
    )
    return HttpResponse(page(
        "Владельцы", format_html('<h1>Владельцы</h1><ul>{}</ul>', entries)
    ))


@require_safe
def owner_detail(request: HttpRequest, owner_id: int) -> HttpResponse:
    """Показать владельца и его периоды владения."""
    _, owners, periods = load_project_data()
    owner = next((owner for owner in owners if owner.id == owner_id), None)
    if owner is None:
        raise Http404("Владелец не найден.")
    entries = format_html_join(
        "", '<li><a href="{}">{}</a> — {}</li>',
        (
            (reverse("catalogue:detail", args=[period.item.id]),
             period.item.name, period)
            for period in periods if period.owner.id == owner_id
        ),
    )
    content = format_html(
        '<h1>{}</h1><h2>Периоды владения</h2><ul>{}</ul>'
        '<a href="{}">К владельцам</a>',
        owner.name, entries, reverse("owners:list"),
    )
    return HttpResponse(page(owner.name, content))
