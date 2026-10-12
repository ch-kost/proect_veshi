"""Шаблонные страницы владельцев."""

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from web_data import load_project_data


@require_safe
def owner_list(request: HttpRequest) -> HttpResponse:
    """Показать список существующих владельцев."""
    _, owners, _ = load_project_data()
    return render(request, "owners/owner_list.html", {"owners": owners})


@require_safe
def owner_detail(request: HttpRequest, owner_id: int) -> HttpResponse:
    """Показать текущие предметы владельца и все его периоды."""
    items, owners, periods = load_project_data()
    owner = next((entry for entry in owners if entry.id == owner_id), None)
    if owner is None:
        raise Http404("Владелец не найден.")
    context = {
        "owner": owner,
        "items": [
            item for item in items
            if item.current_owner is not None
            and item.current_owner.id == owner_id
        ],
        "periods": [
            period for period in periods if period.owner.id == owner_id
        ],
    }
    return render(request, "owners/owner_detail.html", context)
