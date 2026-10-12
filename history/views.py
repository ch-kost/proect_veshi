"""Шаблонные страницы истории владения."""

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from web_data import load_project_data


@require_safe
def period_list(request: HttpRequest) -> HttpResponse:
    """Передать упорядоченную историю владения в шаблон списка."""
    _, _, periods = load_project_data()
    periods = sorted(
        periods,
        key=lambda period: (period.start_date, period.id),
        reverse=True,
    )
    return render(request, "history/period_list.html", {"periods": periods})


@require_safe
def period_detail(request: HttpRequest, period_id: int) -> HttpResponse:
    """Передать период со связанными объектами в шаблон."""
    _, _, periods = load_project_data()
    period = next((entry for entry in periods if entry.id == period_id), None)
    if period is None:
        raise Http404("Период владения не найден.")
    return render(request, "history/period_detail.html", {"period": period})
