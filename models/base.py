"""Общий базовый класс сущностей проекта."""


class Entity:
    """Сущность со стабильным положительным идентификатором."""

    def __init__(self, entity_id: int) -> None:
        if entity_id <= 0:
            raise ValueError("Идентификатор должен быть положительным.")
        self._id = entity_id

    @property
    def id(self) -> int:
        """Вернуть идентификатор сущности."""
        return self._id
