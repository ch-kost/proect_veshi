"""Функции работы с коллекциями объектов предметной области."""

from datetime import date

from models import Item, Owner, OwnershipPeriod


def add_item(items: list[Item], name: str, description: str = "") -> Item:
    """Создать предмет и добавить его в коллекцию."""
    item_id = max((item.id for item in items), default=0) + 1
    item = Item(item_id, name, description)
    items.append(item)
    return item


def find_item_by_id(items: list[Item], item_id: int) -> Item:
    """Найти предмет по идентификатору или сообщить об ошибке."""
    item = next((entry for entry in items if entry.id == item_id), None)
    if item is None:
        raise ValueError("Предмет с таким номером не найден.")
    return item


def find_items(items: list[Item], query: str) -> list[Item]:
    """Найти предметы по части названия без учета регистра."""
    normalized = query.strip().casefold()
    return [item for item in items if normalized in item.name.casefold()]


def sort_items(items: list[Item], reverse: bool = False) -> list[Item]:
    """Вернуть предметы, отсортированные по названию."""
    return sorted(
        items,
        key=lambda item: item.name.casefold(),
        reverse=reverse,
    )


def find_owner_by_name(owners: list[Owner], name: str) -> Owner | None:
    """Найти владельца по имени без учета регистра."""
    normalized = name.strip().casefold()
    return next(
        (owner for owner in owners if owner.name.casefold() == normalized),
        None,
    )


def add_owner(owners: list[Owner], name: str) -> Owner:
    """Создать владельца или вернуть существующего с тем же именем."""
    existing = find_owner_by_name(owners, name)
    if existing is not None:
        return existing
    owner_id = max((owner.id for owner in owners), default=0) + 1
    owner = Owner(owner_id, name)
    owners.append(owner)
    return owner


def transfer_item(
    item: Item,
    owner: Owner,
    periods: list[OwnershipPeriod],
    transfer_on: date,
    today: date | None = None,
) -> OwnershipPeriod:
    """Передать предмет и добавить созданный период в коллекцию."""
    period_id = max((period.id for period in periods), default=0) + 1
    period = item.transfer_to(owner, transfer_on, period_id, today)
    periods.append(period)
    return period


def cancel_last_transfer(
    item: Item, periods: list[OwnershipPeriod]
) -> OwnershipPeriod:
    """Отменить последнюю передачу и удалить период из коллекции."""
    removed = item.cancel_last_transfer()
    periods.remove(removed)
    return removed


def ownership_statistics(
    items: list[Item], owners: list[Owner]
) -> dict[str, int]:
    """Собрать статистику по коллекциям объектов."""
    return {
        "items": len(items),
        "owners": len(owners),
        "transfers": sum(max(len(item.history) - 1, 0) for item in items),
        "without_owner": sum(item.current_owner is None for item in items),
    }
