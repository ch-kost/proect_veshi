"""Функции безопасного ввода данных."""

from datetime import date, datetime


def parse_date(value: str) -> date:
    """Распознать дату в формате ДД.ММ.ГГГГ или ГГГГ-ММ-ДД."""
    clean_value = value.strip()
    for date_format in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(clean_value, date_format).date()
        except ValueError:
            continue
    raise ValueError("Введите дату как ДД.ММ.ГГГГ или ГГГГ-ММ-ДД.")


def input_date(prompt: str) -> date:
    """Запросить календарную дату с понятной подсказкой."""
    return parse_date(input(f"{prompt} (ДД.ММ.ГГГГ): "))


def input_int(prompt: str, minimum: int | None = None) -> int:
    """Запросить целое число и проверить нижнюю границу."""
    try:
        value = int(input(prompt))
    except ValueError as error:
        raise ValueError("Необходимо ввести целое число.") from error
    if minimum is not None and value < minimum:
        raise ValueError(f"Число должно быть не меньше {minimum}.")
    return value
