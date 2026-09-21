"""Консольный интерфейс объектной системы учета владения."""

from pathlib import Path

from models import Entity, Item, Owner, OwnershipPeriod
from services import (
    add_item,
    add_owner,
    cancel_last_transfer,
    find_item_by_id,
    find_items,
    find_owner_by_name,
    ownership_statistics,
    sort_items,
    transfer_item,
)
from storage import load_data, save_data
from utils import input_date, input_int


DATA_DIR = Path(__file__).parent / "data"


def show_entities(entities: list[Entity]) -> None:
    """Полиморфно вывести коллекцию сущностей через их __str__."""
    if not entities:
        print("Ничего не найдено.")
    for entity in entities:
        print(entity)


def show_items(items: list[Item]) -> None:
    """Вывести предметы и даты начала текущего владения."""
    for item in items:
        current = item.current_period
        since = current.start_date.isoformat() if current else "—"
        print(f"{item}; владеет с {since}")


def show_history(item: Item) -> None:
    """Вывести хронологию владения предметом."""
    print(f"\nИстория: {item.name}")
    for period in item.history:
        duration = period.duration_days()
        suffix = "текущий период" if duration is None else f"{duration} дн."
        print(f"- {period} ({suffix})")


def choose_item(items: list[Item]) -> Item:
    """Запросить существующий предмет."""
    return find_item_by_id(
        items, input_int("Номер предмета: ", minimum=1)
    )


def choose_owner(owners: list[Owner]) -> Owner:
    """Найти существующего владельца или создать нового."""
    name = input("Имя нового владельца: ").strip()
    return find_owner_by_name(owners, name) or add_owner(owners, name)


def print_statistics(items: list[Item], owners: list[Owner]) -> None:
    """Вывести сводные показатели проекта."""
    stats = ownership_statistics(items, owners)
    print(f'Предметов: {stats["items"]}')
    print(f'Владельцев: {stats["owners"]}')
    print(f'Зарегистрированных передач: {stats["transfers"]}')
    print(f'Предметов без текущего владельца: {stats["without_owner"]}')


def print_menu() -> None:
    """Вывести команды приложения."""
    print(
        "\n=== История владения предметами — ПР3 ===\n"
        "1. Показать предметы\n"
        "2. Найти предмет\n"
        "3. Добавить предмет\n"
        "4. Показать владельцев\n"
        "5. Показать историю владения\n"
        "6. Передать предмет\n"
        "7. Отменить последнюю передачу\n"
        "8. Показать статистику\n"
        "9. Показать предметы по алфавиту\n"
        "0. Сохранить и выйти"
    )


def execute_command(
    command: str,
    items: list[Item],
    owners: list[Owner],
    periods: list[OwnershipPeriod],
) -> bool:
    """Выполнить выбранную команду; вернуть False для выхода."""
    if command == "0":
        save_data(DATA_DIR, items, owners, periods)
        print("Данные сохранены. Работа завершена.")
        return False
    if command == "1":
        show_items(items)
    elif command == "2":
        show_entities(find_items(items, input("Часть названия: ")))
    elif command == "3":
        item = add_item(
            items,
            input("Название предмета: "),
            input("Описание: "),
        )
        print(f"Добавлен предмет: {item}")
    elif command == "4":
        show_entities(owners)
    elif command == "5":
        show_history(choose_item(items))
    elif command == "6":
        transfer_item(
            choose_item(items),
            choose_owner(owners),
            periods,
            input_date("Дата передачи"),
        )
        save_data(DATA_DIR, items, owners, periods)
        print("Передача зарегистрирована.")
    elif command == "7":
        removed = cancel_last_transfer(choose_item(items), periods)
        save_data(DATA_DIR, items, owners, periods)
        print(f"Передача №{removed.id} отменена.")
    elif command == "8":
        print_statistics(items, owners)
    elif command == "9":
        show_items(sort_items(items))
    else:
        print("Неизвестная команда.")
    return True


def main() -> None:
    """Загрузить объекты и выполнять команды до выхода пользователя."""
    try:
        items, owners, periods = load_data(DATA_DIR)
    except (OSError, ValueError) as error:
        print(f"Ошибка загрузки данных: {error}")
        return

    running = True
    while running:
        print_menu()
        try:
            running = execute_command(
                input("Выберите действие: ").strip(),
                items,
                owners,
                periods,
            )
        except (OSError, ValueError) as error:
            print(f"Операция не выполнена: {error}")


if __name__ == "__main__":
    main()
