"""HTML-каркас и главная страница на этапе ПР5."""

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.http import require_safe

from services import ownership_statistics
from web_data import load_project_data


def page(title: str, content: str) -> str:
    """Собрать общий HTML-документ с Bootstrap и навигацией."""
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return format_html(
        '<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>{}</title><link rel="stylesheet" href="{}">'
        '<style>body{{background:#f7f6f2;color:#18343d}}'
        'main{{padding-top:2rem}}nav{{padding:1rem;gap:1rem}}'
        '.card{{margin:1rem 0}}a{{color:#087e80}}</style></head><body>'
        '<nav class="nav container" aria-label="Основная навигация">'
        '<a href="{}">Главная</a><a href="{}">Предметы</a>'
        '<a href="{}">Владельцы</a><a href="{}">История</a></nav>'
        '<main class="container">{}</main></body></html>',
        title,
        bootstrap,
        reverse("homepage:index"),
        reverse("catalogue:list"),
        reverse("owners:list"),
        reverse("history:list"),
        content,
    )


@require_safe
def index(request: HttpRequest) -> HttpResponse:
    """Показать описание проекта и актуальную статистику."""
    items, owners, _ = load_project_data()
    stats = ownership_statistics(items, owners)
    content = format_html(
        '<h1>История владения предметами</h1><p class="lead">'
        'У каждого предмета своя история. Узнайте, кто владеет им сейчас '
        'и кому он принадлежал раньше.</p>'
        '<p>Предметов: {} · Владельцев: {} · Передач: {}</p>'
        '<a class="btn btn-primary" href="{}">Открыть предметы</a>',
        stats["items"], stats["owners"], stats["transfers"],
        reverse("catalogue:list"),
    )
    return HttpResponse(page("История владения", content))


def not_found(
    request: HttpRequest, exception: Exception | None = None
) -> HttpResponse:
    """Показать собственную страницу HTTP 404."""
    content = format_html(
        '<h1>Страница не найдена</h1><p>Проверьте адрес или '
        'вернитесь на <a href="{}">главную страницу</a>.</p>',
        reverse("homepage:index"),
    )
    return HttpResponse(page("Страница не найдена", content), status=404)


def service_unavailable(request: HttpRequest) -> HttpResponse:
    """Объяснить проблему чтения JSON без вывода служебных деталей."""
    content = format_html(
        '<h1>Данные временно недоступны</h1><p>Не удалось прочитать '
        'JSON-файлы. Проверьте данные проекта и обновите страницу.</p>'
        '<a href="{}">На главную</a>', reverse("homepage:index"),
    )
    return HttpResponse(page("Данные недоступны", content), status=503)
