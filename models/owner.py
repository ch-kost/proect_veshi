"""Класс владельца предмета."""

from __future__ import annotations

from .base import Entity


class Owner(Entity):
    """Человек, которому принадлежит один или несколько предметов."""

    def __init__(self, owner_id: int, name: str) -> None:
        super().__init__(owner_id)
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Имя владельца не должно быть пустым.")
        self._name = clean_name

    @property
    def name(self) -> str:
        """Вернуть имя владельца."""
        return self._name

    def to_dict(self) -> dict[str, object]:
        """Подготовить владельца к сохранению в JSON."""
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Owner:
        """Создать объект из словаря JSON."""
        return cls(owner_id=int(data["id"]), name=str(data["name"]))

    def __str__(self) -> str:
        return f"{self.id}. {self.name}"
