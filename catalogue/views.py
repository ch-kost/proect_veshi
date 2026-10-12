"""Шаблонные страницы каталога предметов."""

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from services import find_item_by_id, find_items, sort_items
from web_data import load_project_data


@require_safe
def item_list(request: HttpRequest) -> HttpResponse:
    """Подготовить коллекцию для поиска и сортировки в каталоге."""
    items, _, _ = load_project_data()
    query = request.GET.get("q", "").strip()[:200]
    sort = request.GET.get("sort", "name")
    if sort not in ("id", "name", "desc"):
        sort = "name"
    if query:
        items = find_items(items, query)
    items = (
        sorted(items, key=lambda item: item.id)
        if sort == "id"
        else sort_items(items, reverse=sort == "desc")
    )
    context = {"items": items, "q": query, "sort": sort}
    return render(request, "catalogue/item_list.html", context)


@require_safe
def item_detail(request: HttpRequest, item_id: int) -> HttpResponse:
    """Передать предмет с историей и владельцем в шаблон карточки."""
    items, _, _ = load_project_data()
    try:
        item = find_item_by_id(items, item_id)
    except ValueError as error:
        raise Http404("Предмет не найден.") from error
    return render(request, "catalogue/item_detail.html", {"item": item})
