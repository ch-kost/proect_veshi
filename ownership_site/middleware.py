"""Понятный HTTP-ответ при недоступном JSON-хранилище."""

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from web_data import DataLoadError


class DataErrorMiddleware(MiddlewareMixin):
    """Показать страницу 503 вместо ошибки чтения данных."""

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> HttpResponse | None:
        if isinstance(exception, DataLoadError):
            from homepage.views import service_unavailable

            return service_unavailable(request)
        return None
