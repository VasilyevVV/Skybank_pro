import datetime as dt
import json
import os
import time
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

# Загрузка переменных из .env-файла
load_dotenv()
# Получение API-ключей из файла .env
RATE_API_KEY = os.getenv("RATE_API_KEY")
STOCK_API_KEY = os.getenv("STOCK_API_KEY")


def get_greeting() -> str:
    """Функция приветствия. Выдаёт соответствующую строку в зависимости от текущего времени"""
    current_hour = dt.datetime.now().hour
    if 0 <= current_hour < 6:
        return "Доброй ночи!"
    elif 6 <= current_hour < 10:
        return "Доброе утро!"
    elif 10 <= current_hour < 18:
        return "Добрый день!"
    else:
        return "Добрый вечер!"


def get_period(current_date: str) -> dict:
    """Функция определения периода: с начала месяца по заданную дату.
    Принимает на вход дату в виде строки, возвращает словарь в формате:
    {"begin": "2025-05-01 00:00:00', 'end': '2025-05-12 10:00:00'}.
    Если дата задана некорректно, возвращает пустой словарь {}.
    """
    period = {}
    try:
        start_date = dt.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S").replace(day=1)
        period["begin"] = dt.datetime.strftime(start_date, "%Y-%m-%d 00:00:00")
        period["end"] = current_date
    except:
        return {}
        # raise ValueError("Некорректно указана дата")
    return period


def read_excel_file(file_path: str) -> pd.DataFrame | None:
    """Чтение Excel-файла с операциями"""
    if os.path.exists(file_path):
        # Если файл существует, попытка прочитать Excel-файл
        try:
            operations_df = pd.read_excel(file_path, parse_dates=False, na_filter=False)
        except ValueError:
            raise ValueError("Ошибка чтения файла с операциями")
        else:
            return operations_df
    else:
        # Если файл по указанному пути не найден
        raise FileNotFoundError(f"Файл с операциями не найден: {file_path}")


def select_tx_for_period(input_df: pd.DataFrame, current_date: str) -> pd.DataFrame | None:
    """Функция отбора данных из DataFrame за период.
    Принимает на вход полный набор данных и дату в формате ГГГГ-ММ-ДД ЧЧ:мм:сс.
    Выводит данные за период с начало месяца по указанную дату.
    """
    # Получение периода: с 1-го числа месяца по текущую дату
    period = get_period(current_date)
    if period != {}:
        begin_day = dt.datetime.strptime(period["begin"], "%Y-%m-%d %H:%M:%S")
        end_day = dt.datetime.strptime(period["end"], "%Y-%m-%d %H:%M:%S")
        # Преобразование столбца "Дата платежа" в формат datetime
        input_df["Дата платежа"] = pd.to_datetime(input_df["Дата платежа"], format="%d.%m.%Y", errors="coerce")
        # Отбор в результирующий DataFrame только операций за период: с 1 числа месяца по дату, переданную на вход
        filtered_df = input_df[(input_df["Дата платежа"] >= begin_day) & (input_df["Дата платежа"] <= end_day)]
        return filtered_df
    else:
        return None


def total_expenses(df_excel: pd.DataFrame) -> list[dict]:
    """Функция расчёта суммы операций по каждой карте за период"""
    if df_excel is None:
        return []
    elif df_excel.empty:
        return []
    else:
        # Отбор успешных операций: статус не равен FAILED, только траты по картам: Сумма < 0 и "Номер карты" не пустой
        filtered_df = df_excel[
            (df_excel["Статус"] != "FAILED") & (df_excel["Сумма платежа"] < 0.0) & (df_excel["Номер карты"] != "")
        ]
        # Группировка по номерам карт и получение сумм
        sum_by_cards = filtered_df.groupby(by=["Номер карты"], sort=False)["Сумма операции"].sum().reset_index()
        # Переименование столбцов, для вывода словаря
        sum_by_cards.rename(columns={"Номер карты": "last_digits", "Сумма операции": "total_spent"}, inplace=True)
        # Изменение суммы трат по картам на положительное число
        sum_by_cards["total_spent"] = round((sum_by_cards["total_spent"] * (-1)), 2)
        # Добавление столбца cashback по формуле (сумма платежей * 0.01)
        sum_by_cards["cashback"] = round((sum_by_cards["total_spent"] * 0.01), 2)
        return sum_by_cards.to_dict(orient="records")


def get_top_tx(input_df: pd.DataFrame) -> list[dict]:
    """Топ-5 транзакций за период. Принимает на вход DataFrame,"""
    if input_df is None:
        return []
    elif input_df.empty:
        return []
    else:
        # Отбор проведённых транзакций - со статусом "ОК"
        filtered_df = input_df[(input_df["Статус"] != "FAILED")]
        tx_sorted = filtered_df[
            ["Дата платежа", "Сумма платежа", "Категория", "Описание", "Сумма операции с округлением"]
        ].sort_values(by=["Сумма операции с округлением"], ascending=False)
        top_5_tx = tx_sorted.nlargest(5, "Сумма операции с округлением")
        top_5_tx = top_5_tx[["Дата платежа", "Сумма платежа", "Категория", "Описание"]]
        top_5_tx.rename(
            columns={
                "Дата платежа": "date",
                "Сумма платежа": "amount",
                "Категория": "category",
                "Описание": "description",
            },
            inplace=True,
        )
        top_5_tx["date"] = top_5_tx["date"].dt.strftime("%d.%m.%Y")
        top_5_tx["description"] = top_5_tx["description"].str.replace('"', "'").astype(str)
        return top_5_tx.to_dict(orient="records")


def get_user_settings(json_file_path: str) -> dict | Any:
    """Функция чтения JSON-файла user_settings.json с пользовательскими настройками - списками валют и акций"""
    if os.path.exists(json_file_path):
        with open(json_file_path, "r", encoding="utf-8") as settings_file:
            try:
                settings_data = json.load(settings_file)
                return settings_data
            except:  # json.JSONDecodeError("Ошибка чтения файла", doc="", pos=0):
                return {}
    else:
        raise FileNotFoundError("Файл не найден")


def get_exchange_rates(currency_list: list) -> list[dict]:
    """
    Функция для получения текущих курсов валют.
    Принимает на вход список кодов валют (н-р, [EUR, USD]), и обращается к сервису
    Exchange Rates Data API: https://apilayer.com/exchangerates_data-api
    """
    if currency_list != []:
        # Валюта, относительно которой определяется курс (RUB)
        convert_to = "RUB"
        request_header = {"apikey": RATE_API_KEY}
        output_list = []
        try:
            for currency in currency_list:
                # Формирование url, headers (API-ключ)
                url_str = (
                    f"https://api.apilayer.com/exchangerates_data/convert?to={convert_to}&from={currency}&amount=1"
                )
                # Запрос курса с помощью сервиса api.apilayer.com/exchangerates_data/convert
                response = requests.get(url_str, headers=request_header)
                status_code = response.status_code
                # Проверка успешности запроса (статус-код = 200)
                if status_code == 200:
                    # Десериализация результата запроса из JSON-формата в объект Python (словарь)
                    response_data = response.json()
                    # result = response_data["result"]
                    # Округление и вывод результата
                    curr_rate = round(float(response_data["result"]), 2)
                else:
                    curr_rate = 0.0
                currency_dict = {"currency": currency, "rate": curr_rate}
                output_list.append(currency_dict)
        except:
            output_list = []
    else:
        output_list = []
    return output_list


def get_stocks_data(company_list: list) -> list[dict]:
    """Функция получения стоимости акций"""
    output_list = []
    if company_list != []:
        for company in company_list:
            # Код для получения стоимости акции
            stock_dict = {"stock": company, "price": "unknown"}
            try:
                url_str = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={company}&apikey={STOCK_API_KEY}"
                response = requests.get(url_str)
                response.raise_for_status()
                status_code = response.status_code
                # если запрос успешен (код 200)
                if status_code == 200:
                    result = response.json()
                    # Определение даты крайнего обновления цены - значения в ключе "3. Last Refreshed"
                    latest_date = result["Meta Data"]["3. Last Refreshed"]
                    # Определение цены по ключу - дате и значению на момент закрытия ("4. close")
                    closing_price = result["Time Series (Daily)"][latest_date]["4. close"]
                    current_price = str(round(float(closing_price), 2))
                else:
                    current_price = "unknown"
                stock_dict = {"stock": company, "price": current_price}
                output_list.append(stock_dict)
                time.sleep(1.5)
            except:
                output_list.append(stock_dict)
                continue
    return output_list
    # raise ConnectionError("Не удалось подключиться к сервису")


def get_begin_date(months_number: int) -> str:
    """Функци определения даты, предшествующей заданному количеству месяцев"""
    return ""
