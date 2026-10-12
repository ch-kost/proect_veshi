"""Проверки веб-страниц без зависимости от pytest-django."""

from pathlib import Path

import pytest
from django.test import Client
from django.urls import reverse

from services import add_item, add_owner
from storage import load_data, save_data


PAGE_CASES = [
    ("/", ("владения",)),
    ("/items/", ("Фотоаппарат", "Гитара")),
    ("/items/1/", ("Фотоаппарат", "Борис Петров")),
    ("/owners/", ("Анна Иванова", "Борис Петров")),
    ("/owners/1/", ("Анна Иванова",)),
    ("/history/", ("Фотоаппарат", "Анна Иванова", "Борис Петров")),
    ("/history/1/", ("Фотоаппарат", "Анна Иванова")),
]


@pytest.mark.parametrize("url, expected", PAGE_CASES)
def test_pages_show_project_data(
    web_client: Client, url: str, expected: tuple[str, ...]
) -> None:
    response = web_client.get(url)
    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]
    content = response.content.decode("utf-8")
    for value in expected:
        assert value in content


@pytest.mark.parametrize(
    "name, kwargs, expected",
    [
        ("homepage:index", {}, "/"),
        ("catalogue:list", {}, "/items/"),
        ("catalogue:detail", {"item_id": 1}, "/items/1/"),
        ("owners:list", {}, "/owners/"),
        ("owners:detail", {"owner_id": 1}, "/owners/1/"),
        ("history:list", {}, "/history/"),
        ("history:detail", {"period_id": 1}, "/history/1/"),
    ],
)
def test_named_routes(name: str, kwargs: dict, expected: str) -> None:
    assert reverse(name, kwargs=kwargs) == expected


@pytest.mark.parametrize(
    "url",
    ["/items/999/", "/owners/999/", "/history/999/", "/missing-page/"],
)
def test_unknown_objects_and_routes_use_custom_404(
    web_client: Client, url: str
) -> None:
    response = web_client.get(url)
    assert response.status_code == 404
    content = response.content.decode("utf-8").casefold()
    assert "не найдена" in content
    assert "traceback" not in content


@pytest.mark.parametrize("url, expected", PAGE_CASES)
def test_pages_reject_post(
    web_client: Client, url: str, expected: tuple[str, ...]
) -> None:
    response = web_client.post(url, {"name": "Новый предмет"})
    assert response.status_code == 405
    assert "GET" in response.headers["Allow"]
    assert "HEAD" in response.headers["Allow"]


def test_get_requests_do_not_change_json(
    web_client: Client, web_data: Path
) -> None:
    before = {path.name: path.read_bytes() for path in web_data.glob("*.json")}
    for url, _ in PAGE_CASES:
        assert web_client.get(url).status_code == 200
    after = {path.name: path.read_bytes() for path in web_data.glob("*.json")}
    assert after == before


def test_empty_collections_are_displayed(
    web_client: Client, web_data: Path
) -> None:
    save_data(web_data, [], [], [])
    for url in ("/", "/items/", "/owners/", "/history/"):
        assert web_client.get(url).status_code == 200
    for url in ("/items/1/", "/owners/1/", "/history/1/"):
        assert web_client.get(url).status_code == 404


def test_user_text_is_html_escaped(
    web_client: Client, web_data: Path
) -> None:
    items, owners, periods = load_data(web_data)
    unsafe = "<script>alert(1)</script>"
    item = add_item(items, unsafe, unsafe)
    owner = add_owner(owners, unsafe)
    save_data(web_data, items, owners, periods)

    for url in (f"/items/{item.id}/", f"/owners/{owner.id}/"):
        response = web_client.get(url)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert unsafe not in content
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in content


def test_bad_json_has_friendly_service_unavailable_page(
    web_client: Client, web_data: Path
) -> None:
    (web_data / "items.json").write_text("{", encoding="utf-8")
    response = web_client.get("/items/")
    assert response.status_code == 503
    content = response.content.decode("utf-8").casefold()
    assert "данн" in content
    assert "traceback" not in content
