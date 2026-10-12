"""Пользовательские проверки шаблонов и статики ПР6."""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.contrib.staticfiles import finders
from django.test import Client

from services import add_item
from storage import load_data, save_data


STATIC_FILES = (
    "homepage/css/style.css",
    "homepage/js/main.js",
    "homepage/img/logo.svg",
)
PAGE_URLS = (
    "/", "/items/", "/items/1/", "/owners/", "/owners/1/",
    "/history/", "/history/1/",
)


class Document(HTMLParser):
    """Извлечь видимый текст, ссылки и структуру обычного HTML."""

    def __init__(self, content: str) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.links: set[str] = set()
        self.assets: set[str] = set()
        self.nav_count = 0
        self.doctype_count = 0
        self.feed(content)

    def handle_decl(self, decl: str) -> None:
        if decl.casefold() == "doctype html":
            self.doctype_count += 1

    def handle_starttag(self, tag: str, attrs: list[tuple]) -> None:
        attributes = dict(attrs)
        if tag == "nav":
            self.nav_count += 1
        if tag == "a" and attributes.get("href"):
            self.links.add(attributes["href"])
        if tag in ("link", "script", "img"):
            path = attributes.get("href") or attributes.get("src")
            if path:
                self.assets.add(path)

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    @property
    def text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def get_document(client: Client, url: str) -> Document:
    """Прочитать результат успешного HTTP-запроса."""
    response = client.get(url)
    assert response.status_code == 200
    return Document(response.content.decode("utf-8"))


@pytest.mark.parametrize("url", PAGE_URLS)
def test_pages_share_one_document_and_navigation(
    web_client: Client, url: str
) -> None:
    document = get_document(web_client, url)
    assert document.doctype_count == 1
    assert document.nav_count == 1
    assert {"/", "/items/", "/owners/", "/history/"} <= document.links
    for path in STATIC_FILES:
        assert f"/static/{path}" in document.assets


@pytest.mark.parametrize("path", STATIC_FILES)
def test_static_assets_are_discoverable(path: str) -> None:
    found = finders.find(path)
    assert found is not None
    assert Path(found).stat().st_size > 0


def test_completed_period_has_dates_and_actual_duration(
    web_client: Client,
) -> None:
    document = get_document(web_client, "/history/1/")
    assert "10.01.2026" in document.text
    assert "12.01.2026" in document.text
    assert re.search(r"Продолжительность 2 (?:дней|дня|дн\.)", document.text)
    assert "Период завершён" in document.text


@pytest.mark.parametrize("url", ("/history/2/", "/history/", "/items/1/"))
def test_active_period_does_not_show_uncomputed_duration(
    web_client: Client, url: str
) -> None:
    document = get_document(web_client, url)
    assert "None дней" not in document.text
    assert "None дн." not in document.text
    assert "рассчитывается до текущей даты" not in document.text
    if url == "/history/2/":
        assert "Период продолжается" in document.text
        assert "12.01.2026" in document.text


@pytest.mark.parametrize(
    "url, heading, count",
    [
        ("/items/", "Все предметы", 2),
        ("/owners/", "Все владельцы", 2),
        ("/history/", "Все периоды", 3),
    ],
)
def test_collection_pages_show_real_counts(
    web_client: Client, url: str, heading: str, count: int
) -> None:
    document = get_document(web_client, url)
    assert f"{heading} {count}" in document.text


def test_homepage_shows_actual_statistics(web_client: Client) -> None:
    document = get_document(web_client, "/")
    assert "Предметов 2" in document.text
    assert "Владельцев 2" in document.text
    assert "Передач 1" in document.text
    assert "Без владельца 0" in document.text


def test_empty_collections_have_helpful_messages(
    web_client: Client, web_data: Path
) -> None:
    save_data(web_data, [], [], [])
    cases = (
        ("/", "Здесь появятся ваши вещи"),
        ("/items/", "Реестр пока пуст"),
        ("/owners/", "Владельцев пока нет"),
        ("/history/", "Периодов пока нет"),
    )
    for url, message in cases:
        assert message in get_document(web_client, url).text


def test_missing_description_owner_and_history_have_defaults(
    web_client: Client, web_data: Path
) -> None:
    items, owners, periods = load_data(web_data)
    item = add_item(items, "Новый предмет")
    save_data(web_data, items, owners, periods)
    document = get_document(web_client, f"/items/{item.id}/")
    assert "Описание пока не добавлено." in document.text
    assert "Владелец ещё не назначен." in document.text
    assert "История ещё не началась" in document.text


@pytest.mark.parametrize(
    "url, links",
    [
        ("/items/1/", ("/owners/2/", "/history/1/", "/history/2/")),
        ("/history/1/", ("/items/1/", "/owners/1/")),
        ("/owners/1/", ("/items/1/", "/items/2/", "/history/1/")),
    ],
)
def test_domain_links_open_related_objects(
    web_client: Client, url: str, links: tuple[str, ...]
) -> None:
    document = get_document(web_client, url)
    for link in links:
        assert link in document.links
        assert web_client.get(link).status_code == 200


def test_catalogue_search_is_case_insensitive(web_client: Client) -> None:
    document = get_document(web_client, "/items/?q=ГИТ")
    assert "Гитара" in document.text
    assert "Фотоаппарат" not in document.text
    assert "Результаты поиска 1" in document.text


@pytest.mark.parametrize(
    "sort, first, second",
    [
        ("name", "Гитара", "Фотоаппарат"),
        ("desc", "Фотоаппарат", "Гитара"),
        ("id", "Фотоаппарат", "Гитара"),
    ],
)
def test_catalogue_order_matches_selected_sort(
    web_client: Client, sort: str, first: str, second: str
) -> None:
    document = get_document(web_client, f"/items/?sort={sort}")
    assert document.text.index(first) < document.text.index(second)


def test_search_without_matches_is_explicit(web_client: Client) -> None:
    document = get_document(web_client, "/items/?q=несуществующаявещь")
    assert "Ничего не найдено" in document.text
    assert "Результаты поиска 0" in document.text
    assert "Сбросить" in document.text
