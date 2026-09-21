"""Консольный интерфейс системы учета истории владения."""

from pathlib import Path

from items import add_item, find_items, sort_items
from owners import add_owner, find_owner_by_name
from ownership import (
    cancel_last_transfer,
    get_current_period,
    get_item_history,
    ownership_days,
    ownership_statistics,
    transfer_item,
)
from storage import load_data, save_data
from utils import input_date, input_int


DATA_DIR = Path(__file__).parent / "data"


def show_items(
    items: list[dict[str, object]],
    owners: list[dict[str, object]],
    periods: list[dict[str, object]],
) -> None:
    """Вывести предметы и их текущих владельцев."""
    owner_names = {int(owner["id"]): str(owner["name"]) for owner in owners}
    for item in items:
        current = get_current_period(periods, int(item["id"]))
        owner = "нет владельца"
        since = "—"
        if current is not None:
            owner = owner_names.get(int(current["owner_id"]), "неизвестен")
            since = str(current["start_date"])
        print(
            f'{item["id"]}. {item["name"]} — {owner}, '
            f"владеет с {since}"
        )


def show_history(
    item_id: int,
    items: list[dict[str, object]],
    owners: list[dict[str, object]],
    periods: list[dict[str, object]],
) -> None:
    """Вывести хронологию владения выбранным предметом."""
    item = next((item for item in items if item["id"] == item_id), None)
    if item is None:
        print("Предмет с таким номером не найден.")
        return
    owner_names = {int(owner["id"]): str(owner["name"]) for owner in owners}
    print(f'\nИстория: {item["name"]}')
    for period in get_item_history(periods, item_id):
        owner = owner_names.get(int(period["owner_id"]), "неизвестен")
        end_date = period["end_date"]
        duration = ownership_days(period)
        duration_text = (
            "текущий период" if duration is None else f"{duration} дн."
        )
        print(
            f'- {owner}: {period["start_date"]} — '
            f'{end_date or "по настоящее время"} ({duration_text})'
        )


def choose_item(items: list[dict[str, object]]) -> int:
    """Запросить существующий идентификатор предмета."""
    item_id = input_int("Номер предмета: ", minimum=1)
    if not any(item["id"] == item_id for item in items):
        raise ValueError("Предмет с таким номером не найден.")
    return item_id


def choose_owner(owners: list[dict[str, object]]) -> int:
    """Найти существующего владельца или создать нового."""
    name = input("Имя нового владельца: ").strip()
    existing = find_owner_by_name(owners, name)
    if existing is not None:
        return int(existing["id"])
    owner = add_owner(owners, name)
    return int(owner["id"])


def print_statistics(
    items: list[dict[str, object]],
    owners: list[dict[str, object]],
    periods: list[dict[str, object]],
) -> None:
    """Вывести сводные показатели проекта."""
    stats = ownership_statistics(items, owners, periods)
    print(f'Предметов: {stats["items"]}')
    print(f'Владельцев: {stats["owners"]}')
    print(f'Зарегистрированных передач: {stats["transfers"]}')
    print(f'Предметов без текущего владельца: {stats["without_owner"]}')


def print_menu() -> None:
    """Вывести команды приложения."""
    print(
        "\n=== История владения предметами — ПР2 ===\n"
        "1. Показать предметы\n"
        "2. Найти предмет\n"
        "3. Добавить предмет\n"
        "4. Показать историю владения\n"
        "5. Передать предмет\n"
        "6. Отменить последнюю передачу\n"
        "7. Показать статистику\n"
        "8. Показать предметы по алфавиту\n"
        "0. Сохранить и выйти"
    )


def main() -> None:
    """Загрузить данные и выполнять команды до выхода пользователя."""
    try:
        items, owners, periods = load_data(DATA_DIR)
    except ValueError as error:
        print(f"Ошибка загрузки данных: {error}")
        return

    while True:
        print_menu()
        command = input("Выберите действие: ").strip()
        try:
            if command == "0":
                save_data(DATA_DIR, items, owners, periods)
                print("Данные сохранены. Работа завершена.")
                break
            if command == "1":
                show_items(items, owners, periods)
            elif command == "2":
                query = input("Часть названия: ")
                show_items(find_items(items, query), owners, periods)
            elif command == "3":
                name = input("Название предмета: ")
                description = input("Описание: ")
                item = add_item(items, name, description)
                print(f'Добавлен предмет №{item["id"]}.')
            elif command == "4":
                show_history(choose_item(items), items, owners, periods)
            elif command == "5":
                item_id = choose_item(items)
                owner_id = choose_owner(owners)
                transfer_on = input_date("Дата передачи: ")
                transfer_item(periods, item_id, owner_id, transfer_on)
                save_data(DATA_DIR, items, owners, periods)
                print("Передача зарегистрирована.")
            elif command == "6":
                removed = cancel_last_transfer(periods, choose_item(items))
                save_data(DATA_DIR, items, owners, periods)
                print(f'Передача №{removed["id"]} отменена.')
            elif command == "7":
                print_statistics(items, owners, periods)
            elif command == "8":
                show_items(sort_items(items), owners, periods)
            else:
                print("Неизвестная команда.")
        except (OSError, ValueError) as error:
            print(f"Операция не выполнена: {error}")


if __name__ == "__main__":
    main()
