"""Загрузка и сохранение коллекций проекта в JSON."""

import json
from pathlib import Path


def load_json(path: Path) -> list[dict[str, object]]:
    """Загрузить список словарей; отсутствующий файл считать пустым."""
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(f"Некорректный JSON в файле {path.name}.") from error
    if not isinstance(data, list):
        raise ValueError(f"В файле {path.name} должен находиться список.")
    return data


def save_json(path: Path, data: list[dict[str, object]]) -> None:
    """Сохранить список словарей в JSON с отступами."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def load_data(
    data_dir: Path,
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    """Загрузить предметы, владельцев и периоды владения."""
    return (
        load_json(data_dir / "items.json"),
        load_json(data_dir / "owners.json"),
        load_json(data_dir / "ownership_periods.json"),
    )


def save_data(
    data_dir: Path,
    items: list[dict[str, object]],
    owners: list[dict[str, object]],
    periods: list[dict[str, object]],
) -> None:
    """Сохранить все коллекции проекта."""
    save_json(data_dir / "items.json", items)
    save_json(data_dir / "owners.json", owners)
    save_json(data_dir / "ownership_periods.json", periods)
