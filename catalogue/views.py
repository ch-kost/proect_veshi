"""Показ предметов из существующего JSON-хранилища."""

from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.views.decorators.http import require_safe

from homepage.views import page
from services import find_item_by_id, find_items, sort_items
from web_data import load_project_data


@require_safe
def item_list(request: HttpRequest) -> HttpResponse:
    """Показать предметы с необязательным поиском и сортировкой."""
    items, _, _ = load_project_data()
    query = request.GET.get("q", "").strip()
    if query:
        items = find_items(items, query)
    items = sort_items(items, reverse=request.GET.get("sort") == "desc")
    entries = format_html_join(
        "", '<li class="list-group-item"><a href="{}">{}</a></li>',
        (
            (reverse("catalogue:detail", args=[item.id]), item)
            for item in items
        ),
    )
    content = format_html(
        '<h1>Предметы</h1><p>Всего предметов: {}</p>'
        '<ul class="list-group">{}</ul>', len(items), entries,
    )
    return HttpResponse(page("Предметы", content))


@require_safe
def item_detail(request: HttpRequest, item_id: int) -> HttpResponse:
    """Показать предмет, текущего владельца и историю."""
    items, _, _ = load_project_data()
    try:
        item = find_item_by_id(items, item_id)
    except ValueError as error:
        raise Http404("Предмет не найден.") from error
    entries = format_html_join(
        "", '<li><a href="{}">{}</a></li>',
        (
            (reverse("history:detail", args=[period.id]), period)
            for period in item.history
        ),
    )
    content = format_html(
        '<h1>{}</h1><p>{}</p><p>Текущий владелец: {}</p>'
        '<h2>История владения</h2><ul>{}</ul><a href="{}">К списку</a>',
        item.name, item.description, item.current_owner or "Нет владельца",
        entries, reverse("catalogue:list"),
    )
    return HttpResponse(page(item.name, content))
