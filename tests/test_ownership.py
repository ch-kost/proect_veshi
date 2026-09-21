"""Тесты передачи предметов и истории владения."""

from datetime import date

import pytest

from ownership import (
    cancel_last_transfer,
    get_current_period,
    ownership_days,
    transfer_item,
)


def period() -> dict[str, object]:
    """Вернуть один текущий период для теста."""
    return {
        "id": 1,
        "item_id": 1,
        "owner_id": 1,
        "start_date": "2026-01-10",
        "end_date": None,
    }


def test_transfer_closes_previous_period() -> None:
    periods = [period()]
    created = transfer_item(
        periods,
        1,
        2,
        date(2026, 9, 14),
        today=date(2026, 9, 21),
    )
    assert periods[0]["end_date"] == "2026-09-14"
    assert created["owner_id"] == 2
    assert get_current_period(periods, 1) == created


def test_transfer_to_same_owner_is_forbidden() -> None:
    with pytest.raises(ValueError, match="уже принадлежит"):
        transfer_item(
            [period()],
            1,
            1,
            date(2026, 2, 1),
            today=date(2026, 9, 21),
        )


def test_future_transfer_is_forbidden() -> None:
    with pytest.raises(ValueError, match="будущем"):
        transfer_item(
            [period()],
            1,
            2,
            date(2026, 9, 22),
            today=date(2026, 9, 21),
        )


def test_cancel_transfer_reopens_previous_period() -> None:
    periods = [period()]
    created = transfer_item(
        periods,
        1,
        2,
        date(2026, 9, 14),
        today=date(2026, 9, 21),
    )
    removed = cancel_last_transfer(periods, 1)
    assert removed == created
    assert periods == [period()]


def test_ownership_days_uses_half_open_interval() -> None:
    completed = period()
    completed["end_date"] = "2026-09-14"
    assert ownership_days(completed) == 247
