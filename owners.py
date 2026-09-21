"""Функции работы с коллекцией владельцев."""


def find_owner_by_name(
    owners: list[dict[str, object]], name: str
) -> dict[str, object] | None:
    """Найти владельца по полному имени без учета регистра."""
    normalized = name.strip().casefold()
    return next(
        (
            owner
            for owner in owners
            if str(owner["name"]).casefold() == normalized
        ),
        None,
    )


def add_owner(
    owners: list[dict[str, object]], name: str
) -> dict[str, object]:
    """Создать владельца либо вернуть запись с тем же именем."""
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Имя владельца не должно быть пустым.")
    existing = find_owner_by_name(owners, clean_name)
    if existing is not None:
        return existing
    owner_id = max((int(owner["id"]) for owner in owners), default=0) + 1
    owner: dict[str, object] = {"id": owner_id, "name": clean_name}
    owners.append(owner)
    return owner
