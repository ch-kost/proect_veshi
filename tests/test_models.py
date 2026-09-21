"""Тесты классов предметной области."""

from datetime import date

import pytest

from models import Entity, Item, Owner, OwnershipPeriod


def build_item() -> tuple[Item, Owner, OwnershipPeriod]:
    """Создать предмет с одним текущим периодом."""
    item = Item(1, "Фотоаппарат", "Пленочный")
    owner = Owner(1, "Анна Иванова")
    period = OwnershipPeriod(1, item, owner, date(2026, 1, 10))
    item.add_period(period)
    return item, owner, period


def test_item_and_owner_inherit_entity() -> None:
    item, owner, _ = build_item()
    assert isinstance(item, Entity)
    assert isinstance(owner, Entity)


def test_str_is_polymorphic() -> None:
    item, owner, _ = build_item()
    labels = [str(entity) for entity in (item, owner)]
    assert labels == ["1. Фотоаппарат — Анна Иванова", "1. Анна Иванова"]


def test_transfer_connects_three_objects() -> None:
    item, _, old_period = build_item()
    new_owner = Owner(2, "Борис Петров")
    new_period = item.transfer_to(
        new_owner,
        date(2026, 9, 14),
        period_id=2,
        today=date(2026, 9, 21),
    )
    assert old_period.end_date == date(2026, 9, 14)
    assert new_period.item is item
    assert new_period.owner is new_owner
    assert item.current_owner is new_owner


def test_same_owner_transfer_is_forbidden() -> None:
    item, owner, _ = build_item()
    with pytest.raises(ValueError, match="уже принадлежит"):
        item.transfer_to(
            owner,
            date(2026, 2, 1),
            period_id=2,
            today=date(2026, 9, 21),
        )


def test_cancel_transfer_restores_previous_owner() -> None:
    item, owner, _ = build_item()
    new_owner = Owner(2, "Борис Петров")
    created = item.transfer_to(
        new_owner,
        date(2026, 9, 14),
        period_id=2,
        today=date(2026, 9, 21),
    )
    assert item.cancel_last_transfer() is created
    assert item.current_owner is owner


def test_duration_uses_half_open_interval() -> None:
    _, _, period = build_item()
    period.close(date(2026, 9, 14))
    assert period.duration_days() == 247
