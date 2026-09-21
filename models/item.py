"""Класс предмета и операции с его историей владения."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from .base import Entity

if TYPE_CHECKING:
    from .owner import Owner
    from .ownership_period import OwnershipPeriod


class Item(Entity):
    """Предмет с описанием и упорядоченной историей владения."""

    def __init__(
        self, item_id: int, name: str, description: str = ""
    ) -> None:
        super().__init__(item_id)
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Название предмета не должно быть пустым.")
        self._name = clean_name
        self._description = description.strip()
        self._history: list[OwnershipPeriod] = []

    @property
    def name(self) -> str:
        """Вернуть название предмета."""
        return self._name

    @property
    def description(self) -> str:
        """Вернуть описание предмета."""
        return self._description

    @property
    def history(self) -> tuple[OwnershipPeriod, ...]:
        """Вернуть неизменяемое представление истории владения."""
        return tuple(self._history)

    @property
    def current_period(self) -> OwnershipPeriod | None:
        """Вернуть активный период владения."""
        active = [period for period in self._history if period.is_active]
        if len(active) > 1:
            raise ValueError("У предмета обнаружено несколько владельцев.")
        return active[0] if active else None

    @property
    def current_owner(self) -> Owner | None:
        """Вернуть текущего владельца предмета."""
        period = self.current_period
        return period.owner if period is not None else None

    def add_period(self, period: OwnershipPeriod) -> None:
        """Добавить загруженный период и проверить целостность истории."""
        if period.item is not self:
            raise ValueError("Период относится к другому предмету.")
        self._history.append(period)
        self._history.sort(key=lambda entry: entry.start_date)
        self.current_period

    def transfer_to(
        self,
        owner: Owner,
        transfer_on: date,
        period_id: int,
        today: date | None = None,
    ) -> OwnershipPeriod:
        """Закрыть текущий период и передать предмет владельцу."""
        from .ownership_period import OwnershipPeriod

        today = today or date.today()
        if transfer_on > today:
            raise ValueError("Нельзя зарегистрировать передачу в будущем.")
        current = self.current_period
        if current is not None:
            if current.owner.id == owner.id:
                raise ValueError("Предмет уже принадлежит этому владельцу.")
            current.close(transfer_on)
        period = OwnershipPeriod(
            period_id=period_id,
            item=self,
            owner=owner,
            start_date=transfer_on,
        )
        self.add_period(period)
        return period

    def cancel_last_transfer(self) -> OwnershipPeriod:
        """Удалить последний период и возобновить предыдущий."""
        if len(self._history) < 2:
            message = "У предмета нет передачи, которую можно отменить."
            raise ValueError(message)
        current = self._history[-1]
        if not current.is_active:
            raise ValueError("В истории отсутствует текущий период владения.")
        removed = self._history.pop()
        self._history[-1].reopen()
        return removed

    def to_dict(self) -> dict[str, object]:
        """Подготовить предмет к сохранению в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Item:
        """Создать объект из словаря JSON."""
        return cls(
            item_id=int(data["id"]),
            name=str(data["name"]),
            description=str(data.get("description", "")),
        )

    def __str__(self) -> str:
        owner = self.current_owner
        owner_name = owner.name if owner is not None else "нет владельца"
        return f"{self.id}. {self.name} — {owner_name}"
