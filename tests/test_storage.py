"""Тесты преобразования JSON в связанные объекты."""

from datetime import date
from pathlib import Path

import pytest

from models import Item, Owner, OwnershipPeriod
from storage import load_data, load_json, save_data


def test_object_json_round_trip(tmp_path: Path) -> None:
    item = Item(1, "Фотоаппарат")
    owner = Owner(1, "Анна")
    period = OwnershipPeriod(1, item, owner, date(2026, 1, 10))
    item.add_period(period)
    save_data(tmp_path, [item], [owner], [period])
    items, owners, periods = load_data(tmp_path)
    assert items[0].current_owner is owners[0]
    assert periods[0].item is items[0]
    assert periods[0].start_date == date(2026, 1, 10)


def test_invalid_json_has_clear_error(tmp_path: Path) -> None:
    path = tmp_path / "items.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="Некорректный JSON"):
        load_json(path)


def test_unknown_reference_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "items.json").write_text("[]", encoding="utf-8")
    (tmp_path / "owners.json").write_text("[]", encoding="utf-8")
    (tmp_path / "ownership_periods.json").write_text(
        '[{"id": 1, "item_id": 9, "owner_id": 8, '
        '"start_date": "2026-01-10", "end_date": null}]',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="неизвестный объект"):
        load_data(tmp_path)
