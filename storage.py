"""Преобразование объектов проекта в JSON и обратно."""

import json
from datetime import date
from pathlib import Path

from models import Item, Owner, OwnershipPeriod


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
) -> tuple[list[Item], list[Owner], list[OwnershipPeriod]]:
    """Загрузить JSON, создать объекты и восстановить связи между ними."""
    items = [
        Item.from_dict(data) for data in load_json(data_dir / "items.json")
    ]
    owners = [
        Owner.from_dict(data) for data in load_json(data_dir / "owners.json")
    ]
    items_by_id = {item.id: item for item in items}
    owners_by_id = {owner.id: owner for owner in owners}
    periods: list[OwnershipPeriod] = []

    for data in load_json(data_dir / "ownership_periods.json"):
        try:
            item = items_by_id[int(data["item_id"])]
            owner = owners_by_id[int(data["owner_id"])]
        except KeyError as error:
            message = "Период ссылается на неизвестный объект."
            raise ValueError(message) from error
        end_value = data.get("end_date")
        period = OwnershipPeriod(
            period_id=int(data["id"]),
            item=item,
            owner=owner,
            start_date=date.fromisoformat(str(data["start_date"])),
            end_date=(
                date.fromisoformat(str(end_value))
                if end_value is not None
                else None
            ),
        )
        item.add_period(period)
        periods.append(period)
    return items, owners, periods


def save_data(
    data_dir: Path,
    items: list[Item],
    owners: list[Owner],
    periods: list[OwnershipPeriod],
) -> None:
    """Преобразовать объекты в словари и сохранить все коллекции."""
    save_json(data_dir / "items.json", [item.to_dict() for item in items])
    save_json(data_dir / "owners.json", [owner.to_dict() for owner in owners])
    save_json(
        data_dir / "ownership_periods.json",
        [period.to_dict() for period in periods],
    )
