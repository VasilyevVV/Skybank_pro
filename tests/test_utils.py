import os
import pytest
from freezegun import freeze_time
from unittest.mock import Mock, patch

from src.config import TEST_FILE_DIR
from src.utils import get_greeting, get_period, read_excel_file


# Тест функции получения строки приветствия в зависимости от времени суток
@pytest.mark.parametrize("now_hour, expected", [("2026-01-01 03:00:00", "Доброй ночи!"),
                                                ("2026-01-01 07:00:00", "Доброе утро!"),
                                                ("2026-01-01 12:00:00", "Добрый день!"),
                                                ("2026-01-01 21:00:00", "Добрый вечер!"),
                                                ])
def test_get_greeting(now_hour, expected):
    with freeze_time(now_hour):
        assert get_greeting() == expected


@pytest.mark.parametrize("input_date, expected",
                         [("2021-07-27 23:00:00", {"begin": "2021-07-01 00:00:00", "end": "2021-07-27 23:00:00"}),
                          ("2025-10-15 14:45:00", {"begin": "2025-10-01 00:00:00", "end": "2025-10-15 14:45:00"}),
                          ("2026-01-01 10:08:00", {"begin": "2026-01-01 00:00:00", "end": "2026-01-01 10:08:00"}),
                          ], )
def test_get_period(input_date, expected):
    """Тест функции get_period с корректными входными датами"""
    assert get_period(input_date) == expected


@pytest.mark.parametrize("input_date, expected",
                         [("2021-07-35", {}), ("2027.18.02", {}), ("no_date", {}), ("", {}),
                          ], )
def test_get_period_inv_date(input_date, expected):
    # with pytest.raises(ValueError, match="Некорректно указана дата"):
    #    get_period(input_date)
    assert get_period(input_date) == expected


# Тест корректного чтения Excel-файла
def test_read_excel_file():
    test_file_path = os.path.join(TEST_FILE_DIR, "test_operations.xlsx")
    df = read_excel_file(test_file_path)
    assert df.shape == (50, 15)


# Тест открытия несуществующего Excel-файла или при некорректном пути к файлу
@pytest.mark.parametrize(
    "inv_file_path",
    [
        ("tx_file.xlsx"),
        ("../test_data/tx.xls"),
        (""),
    ],
)
def test_read_invalid_excel(inv_file_path):
    with pytest.raises(FileNotFoundError) as exc_info:
        read_excel_file(inv_file_path)
    assert str(exc_info.value) == f"Файл с операциями не найден: {inv_file_path}"


# Тест чтения пустого Excel-файла
def test_read_empty_excel():
    test_file_path = os.path.join(TEST_FILE_DIR, "test_empty_tx.xlsx")
    epmty_df = read_excel_file(test_file_path)
    assert epmty_df.shape == (0,15)


# Тест чтения некорректного Excel-файла
@pytest.mark.parametrize("no_xls_file", [("test_no_csv.txt"), ("test_no_json.json"), ("test_empty.json")])
def test_incorrect_file(no_xls_file):
    test_file_path = os.path.join(TEST_FILE_DIR, no_xls_file)
    with pytest.raises(ValueError) as err_info:
        read_excel_file(test_file_path)
    assert str(err_info.value) == f"Ошибка чтения файла с операциями: {test_file_path}"
