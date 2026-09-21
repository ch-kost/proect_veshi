"""Тесты функций обработки коллекций объектов."""

from datetime import date

from models import Item, Owner, OwnershipPeriod
from services import (
    add_item,
    add_owner,
    cancel_last_transfer,
    find_items,
    ownership_statistics,
    sort_items,
    transfer_item,
)


def test_add_find_and_sort_items() -> None:
    items = [Item(1, "Часы")]
    created = add_item(items, "Альбом")
    assert created.id == 2
    assert find_items(items, "АЛЬ") == [created]
    assert sort_items(items) == [created, items[0]]


def test_add_owner_reuses_same_name() -> None:
    owners = [Owner(1, "Анна Иванова")]
    assert add_owner(owners, " анна иванова ") is owners[0]
    assert len(owners) == 1


def test_transfer_and_cancel_update_both_collections() -> None:
    item = Item(1, "Фотоаппарат")
    old_owner = Owner(1, "Анна")
    new_owner = Owner(2, "Борис")
    old_period = OwnershipPeriod(1, item, old_owner, date(2026, 1, 10))
    item.add_period(old_period)
    periods = [old_period]
    created = transfer_item(
        item,
        new_owner,
        periods,
        date(2026, 9, 14),
        today=date(2026, 9, 21),
    )
    assert created in periods
    assert cancel_last_transfer(item, periods) is created
    assert periods == [old_period]


def test_statistics_count_transfers() -> None:
    item = Item(1, "Фотоаппарат")
    first = Owner(1, "Анна")
    second = Owner(2, "Борис")
    period = OwnershipPeriod(1, item, first, date(2026, 1, 10))
    item.add_period(period)
    item.transfer_to(
        second,
        date(2026, 9, 14),
        period_id=2,
        today=date(2026, 9, 21),
    )
    assert ownership_statistics([item], [first, second]) == {
        "items": 1,
        "owners": 2,
        "transfers": 1,
        "without_owner": 0,
    }
