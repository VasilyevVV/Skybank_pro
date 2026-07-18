import pytest


@pytest.fixture
def test_user_settings_dict():
    return {"user_currencies": ["INR", "RUB"], "user_stocks": ["ST1", "ST2", "ST3"]}


@pytest.fixture
def test_expenses_list():
    return [
        {"last_digits": "*7197", "total_spent": 9762.62, "cashback": 97.63},
        {"last_digits": "*5091", "total_spent": 2112.67, "cashback": 21.13},
        {"last_digits": "*4556", "total_spent": 2822.8, "cashback": 28.23},
    ]


@pytest.fixture
def test_top_tx():
    return [
        {
            "date": "30.12.2021",
            "amount": 174000.0,
            "category": "Пополнения",
            "description": "Пополнение через Газпромбанк",
        },
        {"date": "31.12.2021", "amount": -20000.0, "category": "Переводы", "description": "Константин Л."},
        {"date": "23.12.2021", "amount": 20000.0, "category": "Другое", "description": "Иван С."},
        {
            "date": "30.12.2021",
            "amount": 5046.0,
            "category": "Пополнения",
            "description": "Пополнение через Газпромбанк",
        },
        {"date": "25.12.2021", "amount": -3400.0, "category": "Развлечения", "description": "sevs.eduerp.ru"},
    ]


# Фикстура - список валют для тестирования функции определения курса
@pytest.fixture
def test_currency_list():
    return ["USD", "EUR"]


# Фикстура - результат успешного запроса к сервису курса валют
@pytest.fixture
def test_mock_responses():
    return [
        {
            "success": True,
            "query": {"from": "USD", "to": "RUB", "amount": 1},
            "info": {"timestamp": 1780415047, "rate": 71.551257},
            "date": "2026-06-02",
            "result": 71.551257,
        },
        {
            "success": True,
            "query": {"from": "EUR", "to": "RUB", "amount": 1},
            "info": {"timestamp": 1780415047, "rate": 84.841723},
            "date": "2026-06-02",
            "result": 84.841723,
        },
    ]


# Фикстура - результат определения курса валют
@pytest.fixture
def test_rates():
    return [{"currency": "USD", "rate": 71.55}, {"currency": "EUR", "rate": 84.84}]


# Фикстура - ответ сервиса курса акций
@pytest.fixture
def test_stock_response():
    return {
        "Meta Data": {
            "1. Information": "Daily Prices (open, high, low, close) and Volumes",
            "2. Symbol": "AAPL",
            "3. Last Refreshed": "2026-06-02",
            "4. Output Size": "Compact",
            "5. Time Zone": "US/Eastern",
        },
        "Time Series (Daily)": {
            "2026-06-02": {
                "1. open": "307.4600",
                "2. high": "315.4500",
                "3. low": "306.6850",
                "4. close": "315.2000",
                "5. volume": "44534716",
            },
            "2026-06-01": {
                "1. open": "309.6250",
                "2. high": "310.9400",
                "3. low": "305.0200",
                "4. close": "306.3100",
                "5. volume": "48849933",
            },
        },
    }


# Фикстура - список акций для тестирования функции определения курса акций
@pytest.fixture
def test_stock_list():
    return ["AAPL", "AMZN", "MSFT", "TSLA"]


# Фикстура для тестирования функции определения выгодных категорий повышенного кешбэка
@pytest.fixture
def test_profit_json():
    return '{"Ж/д билеты": 140, "Развлечения": 68, "Каршеринг": 54}'


# Фикстура для тестирования функции поиска транзакций, содержащих строку для поиска
@pytest.fixture
def test_entertainments():
    return """
[{"Дата операции": "25.12.2021 13:04:15", "Дата платежа": "25.12.2021", "Номер карты": "*7197",
 "Статус": "OK", "Сумма операции": -3400.0, "Валюта операции": "RUB", "Сумма платежа": -3400.0,
 "Валюта платежа": "RUB", "Кэшбэк": "", "Категория": "Развлечения", "MCC": 7941, "Описание": "sevs.eduerp.ru",
 "Бонусы (включая кэшбэк)": 68, "Округление на инвесткопилку": 0, "Сумма операции с округлением": 3400.0}]
"""


@pytest.fixture
def test_flowers():
    return """
[{"Дата операции": "26.12.2021 13:50:58", "Дата платежа": "26.12.2021", "Номер карты": "*7197", "Статус": "OK",
 "Сумма операции": -600.0, "Валюта операции": "RUB", "Сумма платежа": -600.0, "Валюта платежа": "RUB", "Кэшбэк": "",
 "Категория": "Цветы", "MCC": 5992, "Описание": "IP Isaeva O.N.", "Бонусы (включая кэшбэк)": 12,
 "Округление на инвесткопилку": 0, "Сумма операции с округлением": 600.0}]
"""
