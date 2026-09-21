"""Тесты JSON-хранилища."""

from pathlib import Path

import pytest

from storage import load_json, save_json


def test_json_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "items.json"
    source = [{"id": 1, "name": "Фотоаппарат"}]
    save_json(path, source)
    assert load_json(path) == source


def test_invalid_json_has_clear_error(tmp_path: Path) -> None:
    path = tmp_path / "items.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="Некорректный JSON"):
        load_json(path)
