from datetime import date


def show_item(item_name, owner_name, acquired_on):
    """Показать карточку предмета и начало текущего периода владения."""
    print(f"Предмет: {item_name}")
    print(f"Текущий владелец: {owner_name}")
    print(f"Начало владения: {acquired_on.isoformat()}")


def ownership_days(acquired_on, end_on):
    """Число дней в периоде [начало, конец); отрицательный период запрещен."""
    if end_on < acquired_on:
        raise ValueError("Конец периода не может быть раньше начала.")
    return (end_on - acquired_on).days


def can_transfer(current_owner, new_owner, acquired_on, transfer_on, today):
    """Проверить получателя и дату; вернуть разрешение или отказ."""
    if not new_owner.strip():
        print("Отказ: имя нового владельца не должно быть пустым.")
        return False
    if current_owner.strip().casefold() == new_owner.strip().casefold():
        print("Отказ: предмет уже принадлежит этому владельцу.")
        return False
    if transfer_on < acquired_on:
        print("Отказ: передача не может быть раньше начала владения.")
        return False
    if transfer_on > today:
        print("Отказ: будущую передачу пока нельзя зарегистрировать.")
        return False
    return True


def main():
    """Показать предмет, проверить ввод и вывести результат передачи."""
    item_name = "Фотоаппарат Зенит-Е"
    current_owner = "Анна Иванова"
    acquired_on = date(2026, 1, 10)
    today = date.today()

    print("Система учета истории владения предметами — ПР1")
    print("Демонстрационные данные. Изменения действуют до конца запуска.\n")
    show_item(item_name, current_owner, acquired_on)
    if today < acquired_on:
        print("Дата компьютера раньше начала владения. Проверьте дату.")
        return
    print(f"Срок владения на сегодня: {ownership_days(acquired_on, today)} дн.")

    choice = input("\nПередать предмет? 1 — да, 0 — выход: ").strip()
    if choice == "0":
        print("Передача отменена. Владелец не изменен.")
        return
    if choice != "1":
        print("Неизвестная команда. Запустите программу и введите 1 или 0.")
        return

    new_owner = input("Имя нового владельца: ").strip()
    print("Дата передачи (год, месяц, день вводятся отдельно):")
    try:
        year = int(input("Год: "))
        month = int(input("Месяц: "))
        day = int(input("День: "))
        transfer_on = date(year, month, day)
    except ValueError:
        print("Ошибка даты: нужны целые числа и существующая календарная дата.")
        return

    is_allowed = can_transfer(
        current_owner, new_owner, acquired_on, transfer_on, today
    )
    if not is_allowed:
        print("Передача не выполнена. Владелец не изменен.")
        return

    period_days = ownership_days(acquired_on, transfer_on)
    previous_owner = current_owner
    current_owner = new_owner
    print("\nПередача зарегистрирована в текущем запуске.")
    print(f"Предмет: {item_name}")
    print(f"Передача: {previous_owner} → {current_owner}")
    print(f"Дата передачи: {transfer_on.isoformat()}")
    print(
        f"Завершенный период: {acquired_on.isoformat()} — "
        f"{transfer_on.isoformat()}, {period_days} дн."
    )
    acquired_on = transfer_on
    print("\nОбновленная карточка:")
    show_item(item_name, current_owner, acquired_on)


if __name__ == "__main__":
    main()
