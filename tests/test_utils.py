import datetime as dt
import os
from unittest.mock import Mock, patch

import pytest
from freezegun import freeze_time

from src.config import TEST_FILE_DIR
from src.utils import (
    RATE_API_KEY,
    STOCK_API_KEY,
    get_exchange_rates,
    select_tx_for_period,
    get_greeting,
    get_period,
    get_stocks_data,
    get_top_tx,
    get_user_settings,
    read_excel_file,
    total_expenses,
    get_begin_date
)


# Тест функции получения строки приветствия в зависимости от времени суток
@pytest.mark.parametrize(
    "now_hour, expected",
    [
        ("2026-01-01 03:00:00", "Доброй ночи!"),
        ("2026-01-01 07:00:00", "Доброе утро!"),
        ("2026-01-01 12:00:00", "Добрый день!"),
        ("2026-01-01 21:00:00", "Добрый вечер!"),
    ],
)
def test_get_greeting(now_hour, expected):
    with freeze_time(now_hour):
        assert get_greeting() == expected


@pytest.mark.parametrize(
    "input_date, expected",
    [
        ("2021-07-27 23:00:00", {"begin": "2021-07-01 00:00:00", "end": "2021-07-27 23:00:00"}),
        ("2025-10-15 14:45:00", {"begin": "2025-10-01 00:00:00", "end": "2025-10-15 14:45:00"}),
        ("2026-01-01 10:08:00", {"begin": "2026-01-01 00:00:00", "end": "2026-01-01 10:08:00"}),
    ],
)
def test_get_period(input_date, expected):
    """Тест функции get_period с корректными входными датами"""
    assert get_period(input_date) == expected


@pytest.mark.parametrize(
    "input_date, expected",
    [
        ("2021-07-35", {}),
        ("2027.18.02", {}),
        ("no_date", {}),
        ("", {}),
    ],
)
def test_get_period_inv_date(input_date, expected):
    """Тест функции get_period с НЕкорректными входными датами"""
    assert get_period(input_date) == expected


def test_read_excel_file():
    """Тест корректного чтения Excel-файла с операциями"""
    test_file_path = os.path.join(TEST_FILE_DIR, "test_operations.xlsx")
    df = read_excel_file(test_file_path)
    assert df.shape == (51, 15)


@pytest.mark.parametrize(
    "inv_file_path",
    [
        ("tx_file.xlsx"),
        ("../test_data/tx.xls"),
        (""),
    ],
)
def test_read_invalid_excel(inv_file_path):
    """Тест открытия несуществующего Excel-файла или путь к файлу некорректный"""
    with pytest.raises(FileNotFoundError) as exc_info:
        read_excel_file(inv_file_path)
    assert str(exc_info.value) == f"Файл с операциями не найден: {inv_file_path}"


def test_read_empty_excel():
    """Тест чтения пустого Excel-файла"""
    test_file_path = os.path.join(TEST_FILE_DIR, "test_empty_tx.xlsx")
    epmty_df = read_excel_file(test_file_path)
    assert epmty_df.shape == (0, 15)


@pytest.mark.parametrize("no_xls_file", [("test_no_csv.txt"), ("test_no_json.json"), ("test_empty.json")])
def test_incorrect_file(no_xls_file):
    """Тест чтения некорректного файла (не Excel)"""
    test_file_path = os.path.join(TEST_FILE_DIR, no_xls_file)
    with pytest.raises(ValueError, match="Ошибка чтения файла с операциями"):
        read_excel_file(test_file_path)


@pytest.mark.parametrize(
    "test_date, expected",
    [
        ("2021-12-20 20:00:00", (0, 15)),
        ("2021-12-23 23:55:00", (3, 15)),
        ("2021-12-27 17:00:00", (25, 15)),
        ("2021-12-31 23:55:00", (50, 15)),
    ],
)
def test_get_filtered_df(test_date, expected):
    """Тест отбора данных из прочитанного Excel-файла и получения DataFrame за период"""
    test_file_path = os.path.join(TEST_FILE_DIR, "test_operations.xlsx")
    df = read_excel_file(test_file_path)
    test_df = select_tx_for_period(df, test_date)
    assert test_df.shape == expected


def test_get_user_settings(test_user_settings_dict):
    """Тест корректного чтения пользовательских настроек из json-файла"""
    test_file_path = os.path.join(TEST_FILE_DIR, "test_user_settings.json")
    assert get_user_settings(test_file_path) == test_user_settings_dict


@pytest.mark.parametrize(
    "test_file_path, expected",
    [
        ("test_bad_settings.json", {}),
    ],
)
def test_incorrect_json(test_file_path, expected):
    """Тест чтения некорректного json-файла с пользовательскими настройками"""
    test_file_path = os.path.join(TEST_FILE_DIR, test_file_path)
    assert get_user_settings(test_file_path) == expected


@pytest.mark.parametrize(
    "test_file_path, expected",
    [
        ("", {}),
        ("   ", {}),
        ("test_file.txt", {}),
    ],
)
def test_no_exist_file(test_file_path, expected):
    """Тест  чтения пользовательских настроек из несуществующего файла"""
    test_file_path = os.path.join(TEST_FILE_DIR, test_file_path.strip())
    with pytest.raises(FileNotFoundError):
        get_user_settings(test_file_path)


def test_total_expenses(test_expenses_list):
    """Тест функции расчёта сумм расходов по картам за период"""
    test_file_path = os.path.join(TEST_FILE_DIR, "test_operations.xlsx")
    df = read_excel_file(test_file_path)
    assert total_expenses(df) == test_expenses_list


@pytest.mark.parametrize("test_file_path, expected", [("test_empty_tx.xlsx", [])])
def test_bad_file_expenses(test_file_path, expected):
    """Тест чтения пустого Excel-файла с операциями"""
    test_file = os.path.join(TEST_FILE_DIR, test_file_path.strip())
    df = read_excel_file(test_file)
    assert total_expenses(df) == expected


def test_get_top_tx(test_top_tx):
    """Тест функции получения топ-5 транзакций за период"""
    test_file_path = os.path.join(TEST_FILE_DIR, "test_operations.xlsx")
    df = read_excel_file(test_file_path)
    filtered_df = select_tx_for_period(df, "2021-12-31 23:59:59")
    assert get_top_tx(filtered_df) == test_top_tx
    empty_file_path = os.path.join(TEST_FILE_DIR, "test_empty_tx.xlsx")
    df_empty = read_excel_file(empty_file_path)
    assert get_top_tx(df_empty) == []


@patch("requests.get")
def test_exchange_rates1(mock_get, test_currency_list, test_mock_responses, test_rates):
    """Тест функции get_exchange_rates при успешном обращении к сервису курса валют"""
    mock_get.return_value.json.return_value = test_mock_responses[0]
    mock_get.return_value.status_code = 200
    assert get_exchange_rates([test_currency_list[0]]) == [test_rates[0]]
    mock_get.assert_called_once_with(
        f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={test_currency_list[0]}&amount=1",
        headers={"apikey": RATE_API_KEY},
    )


@patch("requests.get")
def test_exchange_rates2(mock_get, test_currency_list, test_mock_responses, test_rates):
    """Tecт функции get_exchange_rates при успешном обращении к сервису курса валют, mock_responce - фикстура"""
    mock_get.return_value.json.return_value = test_mock_responses[1]
    mock_get.return_value.status_code = 200
    assert get_exchange_rates([test_currency_list[1]]) == [test_rates[1]]
    mock_get.assert_called_once_with(
        f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={test_currency_list[1]}&amount=1",
        headers={"apikey": RATE_API_KEY},
    )


@pytest.mark.parametrize(
    "response_status_code, expected",
    [
        (400, [{"currency": "EUR", "rate": 0.0}]),
        (401, [{"currency": "EUR", "rate": 0.0}]),
        (403, [{"currency": "EUR", "rate": 0.0}]),
        (522, [{"currency": "EUR", "rate": 0.0}]),
    ],
)
@patch("requests.get")
def test_bad_request_exchange_rates(mock_get, response_status_code, expected):
    """Тестирование функции get_exchange_rates при неуспешных запросах к сервису конвертирования"""
    mock_response = Mock()
    mock_response.status_code = response_status_code
    mock_get.return_value = mock_response
    assert get_exchange_rates(["EUR"]) == expected
    mock_get.assert_called_once_with(
        f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from=EUR&amount=1",
        headers={"apikey": RATE_API_KEY},
    )


def test_empty_currency_list():
    """Тест функции get_exchange_rates при пустом списке на входе"""
    assert get_exchange_rates([]) == []


@patch("requests.get")
def test_get_stock_prices(mock_get, test_stock_response, test_stock_list):
    """Тест функции получения стоимости акций"""
    mock_get.return_value.json.return_value = test_stock_response
    mock_get.return_value.status_code = 200
    assert get_stocks_data([test_stock_list[0]])
    mock_get.assert_called_once_with(
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={test_stock_list[0]}&apikey={STOCK_API_KEY}"
    )


@pytest.mark.parametrize(
    "response_status_code, expected",
    [
        (400, [{"stock": "AAPL", "price": "unknown"}]),
        (401, [{"stock": "AAPL", "price": "unknown"}]),
        (403, [{"stock": "AAPL", "price": "unknown"}]),
        (522, [{"stock": "AAPL", "price": "unknown"}]),
    ],
)
@patch("requests.get")
def test_bad_stock_request(mock_get, response_status_code, expected):
    """Тестирование функции get_exchange_rates при неуспешных запросах к сервису конвертирования"""
    mock_response = Mock()
    mock_response.status_code = response_status_code
    mock_get.return_value = mock_response
    assert get_stocks_data(["AAPL"]) == expected
    mock_get.assert_called_once_with(
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey={STOCK_API_KEY}"
    )


def test_empty_stock():
    """Тест функции получения курса акций, если на вход подан пустой список"""
    assert get_stocks_data([]) == []


@pytest.mark.parametrize(
    "test_date, test_month, expected",
    [
        ("2021.12.20", -1, "2021.11.20 23:59:59"),
        ("2024.12.29", 2, "2025.02.28 23:59:59"),
        ("2021.12.27", -3, "2021.09.27 23:59:59"),
        ("2021.12.31", 0, "2021.12.31 23:59:59"),
    ],
)
def test_get_begin_day(test_date, test_month, expected):
    """Тест функции определения"""
    test_day = dt.datetime.strptime(test_date, "%Y.%m.%d").replace(hour=23,minute=59,second=59)
    assert get_begin_date(test_day, test_month) == expected
