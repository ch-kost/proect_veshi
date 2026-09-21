"""Функции учета периодов владения и передач предметов."""

from datetime import date


def _period_date(period: dict[str, object], field: str) -> date:
    """Преобразовать строковое поле периода в дату."""
    return date.fromisoformat(str(period[field]))


def get_item_history(
    periods: list[dict[str, object]], item_id: int
) -> list[dict[str, object]]:
    """Вернуть периоды предмета в хронологическом порядке."""
    history = (period for period in periods if period["item_id"] == item_id)
    return sorted(history, key=lambda period: str(period["start_date"]))


def get_current_period(
    periods: list[dict[str, object]], item_id: int
) -> dict[str, object] | None:
    """Вернуть незавершенный период владения предметом."""
    current = [
        period
        for period in periods
        if period["item_id"] == item_id and period["end_date"] is None
    ]
    if len(current) > 1:
        raise ValueError("У предмета обнаружено несколько текущих владельцев.")
    return current[0] if current else None


def ownership_days(period: dict[str, object]) -> int | None:
    """Рассчитать длительность завершенного периода в днях."""
    if period["end_date"] is None:
        return None
    return (_period_date(period, "end_date") - _period_date(
        period, "start_date"
    )).days


def transfer_item(
    periods: list[dict[str, object]],
    item_id: int,
    new_owner_id: int,
    transfer_on: date,
    today: date | None = None,
) -> dict[str, object]:
    """Завершить текущий период и зарегистрировать нового владельца."""
    today = today or date.today()
    if transfer_on > today:
        raise ValueError("Нельзя зарегистрировать передачу в будущем.")
    current = get_current_period(periods, item_id)
    if current is not None:
        if current["owner_id"] == new_owner_id:
            raise ValueError("Предмет уже принадлежит этому владельцу.")
        if transfer_on < _period_date(current, "start_date"):
            raise ValueError("Передача раньше начала текущего владения.")
        current["end_date"] = transfer_on.isoformat()
    period_id = max((int(period["id"]) for period in periods), default=0) + 1
    new_period: dict[str, object] = {
        "id": period_id,
        "item_id": item_id,
        "owner_id": new_owner_id,
        "start_date": transfer_on.isoformat(),
        "end_date": None,
    }
    periods.append(new_period)
    return new_period


def cancel_last_transfer(
    periods: list[dict[str, object]], item_id: int
) -> dict[str, object]:
    """Удалить последний период и снова открыть предыдущий."""
    history = get_item_history(periods, item_id)
    if len(history) < 2:
        raise ValueError("У предмета нет передачи, которую можно отменить.")
    current = history[-1]
    if current["end_date"] is not None:
        raise ValueError("В истории отсутствует текущий период владения.")
    previous = history[-2]
    periods.remove(current)
    previous["end_date"] = None
    return current


def ownership_statistics(
    items: list[dict[str, object]],
    owners: list[dict[str, object]],
    periods: list[dict[str, object]],
) -> dict[str, int]:
    """Собрать статистику по коллекциям проекта."""
    active_item_ids = {
        int(period["item_id"])
        for period in periods
        if period["end_date"] is None
    }
    transfers = sum(
        max(len(get_item_history(periods, int(item["id"]))) - 1, 0)
        for item in items
    )
    return {
        "items": len(items),
        "owners": len(owners),
        "transfers": transfers,
        "without_owner": len(items) - len(active_item_ids),
    }
