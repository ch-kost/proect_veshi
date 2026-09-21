"""Класс периода владения предметом."""

from __future__ import annotations

from datetime import date

from .base import Entity
from .item import Item
from .owner import Owner


class OwnershipPeriod(Entity):
    """Связь предмета с владельцем на заданном интервале дат."""

    def __init__(
        self,
        period_id: int,
        item: Item,
        owner: Owner,
        start_date: date,
        end_date: date | None = None,
    ) -> None:
        super().__init__(period_id)
        if end_date is not None and end_date < start_date:
            raise ValueError("Конец периода не может быть раньше начала.")
        self._item = item
        self._owner = owner
        self._start_date = start_date
        self._end_date = end_date

    @property
    def item(self) -> Item:
        """Вернуть предмет периода."""
        return self._item

    @property
    def owner(self) -> Owner:
        """Вернуть владельца периода."""
        return self._owner

    @property
    def start_date(self) -> date:
        """Вернуть начало владения."""
        return self._start_date

    @property
    def end_date(self) -> date | None:
        """Вернуть конец владения или None для текущего периода."""
        return self._end_date

    @property
    def is_active(self) -> bool:
        """Проверить, продолжается ли период."""
        return self.end_date is None

    def close(self, end_date: date) -> None:
        """Завершить период в указанную дату."""
        if end_date < self.start_date:
            raise ValueError("Передача раньше начала текущего владения.")
        if not self.is_active:
            raise ValueError("Период владения уже завершен.")
        self._end_date = end_date

    def reopen(self) -> None:
        """Снова сделать период текущим при отмене передачи."""
        self._end_date = None

    def duration_days(self) -> int | None:
        """Вернуть длину завершенного периода в днях."""
        if self.end_date is None:
            return None
        return (self.end_date - self.start_date).days

    def to_dict(self) -> dict[str, object]:
        """Подготовить период к сохранению в JSON."""
        return {
            "id": self.id,
            "item_id": self.item.id,
            "owner_id": self.owner.id,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat()
            if self.end_date is not None
            else None,
        }

    def __str__(self) -> str:
        end = (
            self.end_date.isoformat()
            if self.end_date
            else "по настоящее время"
        )
        return (
            f"{self.owner.name}: {self.start_date.isoformat()} — {end}"
        )
