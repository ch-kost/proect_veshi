"""Тесты функций работы с предметами."""

from items import add_item, find_items, sort_items


def test_add_item_assigns_next_id() -> None:
    items = [{"id": 3, "name": "Часы", "description": ""}]
    created = add_item(items, "  Фотоаппарат  ", "Пленочный")
    assert created["id"] == 4
    assert created["name"] == "Фотоаппарат"


def test_find_items_ignores_case() -> None:
    items = [
        {"id": 1, "name": "Фотоаппарат", "description": ""},
        {"id": 2, "name": "Гитара", "description": ""},
    ]
    assert find_items(items, "ФОТО") == [items[0]]


def test_sort_items_does_not_change_source() -> None:
    items = [
        {"id": 2, "name": "Часы", "description": ""},
        {"id": 1, "name": "Альбом", "description": ""},
    ]
    result = sort_items(items)
    assert [item["id"] for item in result] == [1, 2]
    assert [item["id"] for item in items] == [2, 1]
