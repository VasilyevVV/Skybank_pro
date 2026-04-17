import datetime as dt
import pprint
import json
import os
import pandas as pd
import requests
import time

from dotenv import load_dotenv

from src.config import BASE_DIRECTORY
# Загрузка переменных из .env-файла
load_dotenv()
# получение имени файла с операциями из файла .env
#file_operations = os.getenv("OPERATIONS_FILE_NAME")
# Получение имени файла с пользовательскими списками валют и акций из файла .env
#user_sett_file = os.getenv("USER_SETTINGS_JSON_FILE")
# Получение API-ключей из файла .env
RATE_API_KEY = os.getenv("RATE_API_KEY")
STOCK_API_KEY = os.getenv("STOCK_API_KEY")

def get_greeting() -> str:
    """Приветствие"""
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
    """ Функция определения периода: с начала месяца по заданную дату.
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
        #raise ValueError("Некорректно указана дата")
        pass
    return period


def read_excel_file(file_path: str, work_date: str) -> pd.DataFrame | None:
    """Чтение Excel-файла с операциями"""
    period = get_period(work_date)
    if period != {}:
        begin_day = dt.datetime.strptime(period["begin"], "%Y-%m-%d %H:%M:%S")
        end_day = dt.datetime.strptime(period["end"], "%Y-%m-%d %H:%M:%S")
        operations_df = pd.read_excel(file_path, parse_dates=False)
        # Преобразование столбца "Дата платежа" в формат datetime
        operations_df["Дата платежа"] = pd.to_datetime(operations_df["Дата платежа"], format="%d.%m.%Y", errors="coerce")
        # Отбор в результирующий DataFrame только операций за период: с 1 числа месяца по дату, переданную на вход
        operations_df = operations_df[(operations_df["Дата платежа"] >= begin_day)
                                      & (operations_df["Дата платежа"] <= end_day)]
        return operations_df
    else:
        return None


def total_expenses(df_excel: pd.DataFrame) -> list[dict]:
    """Функция расчёта суммы операций по картам за период """
    if df_excel is None:
        return []
    elif df_excel.empty:
        return []
    else:
        # Отбор только успешных операций, со статусом, на равным FAILED
        filtered_df = df_excel[(df_excel["Статус"] != "FAILED") & (df_excel["Сумма платежа"] < 0.0)]
        print(filtered_df.shape)
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
    """Топ-5 транзакций за период"""
    if input_df is None:
        return []
    elif input_df.empty:
        return []
    else:
        # Отбор проведённых транзакций - со статусом "ОК"
        filtered_df = input_df[(input_df["Статус"] != "FAILED")]
        tx_sorted = (filtered_df[["Дата платежа",
                                  "Сумма платежа",
                                  "Категория",
                                  "Описание",
                                  "Сумма операции с округлением"]].sort_values(by=["Сумма операции с округлением"],
                                                                               ascending=False))
        top_5_tx = tx_sorted.nlargest(5, "Сумма операции с округлением")
        top_5_tx = top_5_tx[["Дата платежа", "Сумма платежа", "Категория", "Описание"]]
        top_5_tx.rename(columns={"Дата платежа": "date", "Сумма платежа": "amount", "Категория": "category",
                              "Описание": "description"}, inplace=True)
        top_5_tx["date"] = top_5_tx["date"].dt.strftime("%d.%m.%Y")
        top_5_tx["description"] = top_5_tx["description"].str.replace("\"", "'").astype(str)
        return top_5_tx.to_dict(orient="records")


def get_user_settings(json_fila_path: str) -> dict:
    """Функция чтения файла с пользовательскими списками валют и акций из JSON-файла"""
    try:
        with open(json_fila_path, "r", encoding="utf-8") as settings_file:
            try:
                settings_data = json.load(settings_file)
                return settings_data
            except json.JSONDecodeError:
                return {}
    except FileNotFoundError("Файл не найден"):
        return {}


def get_exchange_rates(currency_list: list) -> list[dict]:
    """
    Функция для получения текущих курсов валют по отношению к рублю.
    Принимает на вход список кодов валют (н-р, [EUR, USD]), и обращается к сервису
    Exchange Rates Data API: https://apilayer.com/exchangerates_data-api
    """
    # Валюта, относительно которой определяется курс (RUB)
    convert_to = "RUB"
    if currency_list != []:
        output_list = []
        request_header = {"apikey": RATE_API_KEY}
        for currency in currency_list:
            # Формирование url, headers (API-ключ)
            url_str = f"https://api.apilayer.com/exchangerates_data/convert?to={convert_to}&from={currency}&amount=1"
            # Запрос курса с помощью сервиса api.apilayer.com/exchangerates_data/convert
            response = requests.get(url_str, headers=request_header)
            status_code = response.status_code
            reason = response.reason
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
        return output_list
    else:
        return []


def get_stocks_data(company_list: list) -> list[dict]:
    """Функция получения стоимости акций"""
    if company_list != []:
        output_list = []
        # try
        for company in company_list:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={company}&apikey={STOCK_API_KEY}"
            response = requests.get(url)
            #response.raise_for_status()
            result = response.json()
            # Код для получения цены акции.
            latest_date = result["Meta Data"]["3. Last Refreshed"]
            closing_price = result["Time Series (Daily)"][latest_date]["4. close"]
            stock_dict = {"stock": company, "price": round(float(closing_price), 2)}
            output_list.append(stock_dict)
            time.sleep(1.5)
        return output_list
    else:
        return []
