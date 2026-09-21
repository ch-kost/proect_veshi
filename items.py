"""Функции работы с коллекцией предметов."""


def add_item(
    items: list[dict[str, object]], name: str, description: str = ""
) -> dict[str, object]:
    """Создать предмет и добавить его в коллекцию."""
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Название предмета не должно быть пустым.")
    item_id = max((int(item["id"]) for item in items), default=0) + 1
    item: dict[str, object] = {
        "id": item_id,
        "name": clean_name,
        "description": description.strip(),
    }
    items.append(item)
    return item


def find_items(
    items: list[dict[str, object]], query: str
) -> list[dict[str, object]]:
    """Найти предметы по части названия без учета регистра."""
    normalized = query.strip().casefold()
    return [
        item
        for item in items
        if normalized in str(item["name"]).casefold()
    ]


def sort_items(
    items: list[dict[str, object]], reverse: bool = False
) -> list[dict[str, object]]:
    """Вернуть новый список предметов, отсортированный по названию."""
    return sorted(
        items,
        key=lambda item: str(item["name"]).casefold(),
        reverse=reverse,
    )
