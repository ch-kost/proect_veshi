"""Подготовка Django и изолированных данных для веб-тестов."""

import os
from datetime import date
from pathlib import Path

import django
import pytest
from django.test import Client, override_settings

from models import Item, Owner, OwnershipPeriod
from storage import save_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ownership_site.settings")
django.setup()


@pytest.fixture
def web_data(tmp_path: Path) -> Path:
    """Создать отдельные JSON, не затрагивая пользовательские данные."""
    camera = Item(1, "Фотоаппарат", "Пленочный фотоаппарат")
    guitar = Item(2, "Гитара", "Акустическая гитара")
    anna = Owner(1, "Анна Иванова")
    boris = Owner(2, "Борис Петров")
    periods = [
        OwnershipPeriod(
            1, camera, anna, date(2026, 1, 10), date(2026, 1, 12)
        ),
        OwnershipPeriod(2, camera, boris, date(2026, 1, 12)),
        OwnershipPeriod(3, guitar, anna, date(2026, 1, 15)),
    ]
    for period in periods:
        period.item.add_period(period)
    save_data(tmp_path, [camera, guitar], [anna, boris], periods)
    return tmp_path


@pytest.fixture
def web_client(web_data: Path):
    """Использовать временную папку данных и пользовательскую 404."""
    with override_settings(
        DATA_DIR=web_data,
        DEBUG=False,
        ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
    ):
        yield Client()
