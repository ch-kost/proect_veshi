"""Адаптер существующих JSON-данных для веб-представлений."""

from pathlib import Path

from django.conf import settings

from models import Item, Owner, OwnershipPeriod
from storage import load_data


class DataLoadError(Exception):
    """Хранилище не удалось прочитать или восстановить."""


def load_project_data() -> tuple[
    list[Item], list[Owner], list[OwnershipPeriod]
]:
    """Прочитать текущие данные через объектную модель ПР3."""
    try:
        return load_data(Path(settings.DATA_DIR))
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise DataLoadError("Не удалось загрузить данные проекта.") from error
