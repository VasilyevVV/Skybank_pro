import datetime as dt
import json
import os
import pandas as pd
import requests
import time

from dotenv import load_dotenv


# Загрузка переменных из .env-файла
load_dotenv()
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
        return {}
        # raise ValueError("Некорректно указана дата")
    return period


def read_excel_file(file_path: str) -> pd.DataFrame | None:
    """Чтение Excel-файла с операциями"""
    if os.path.exists(file_path):
        # Если файл существует, попытка прочитать Excel-файл
        try:
            operations_df = pd.read_excel(file_path, parse_dates=False)
        except ValueError:
            raise ValueError(f"Ошибка чтения файла с операциями: {file_path}")
        else:
            return operations_df
    else:
        # Если файл по указанному пути не найден
        raise FileNotFoundError(f"Файл с операциями не найден: {file_path}")


def get_filtered_df(input_df:pd.DataFrame, current_date: str) -> pd.DataFrame | None:
    """Функция отбора данных из DataFrame за период. Принимает на вход полный набор данных и дату.
    Выводит данные за период с начало месяца по указанную дату."""
    # Получение периода: с 1-го числа месяца по текущую дату
    period = get_period(current_date)
    if period != {}:
        begin_day = dt.datetime.strptime(period["begin"], "%Y-%m-%d %H:%M:%S")
        end_day = dt.datetime.strptime(period["end"], "%Y-%m-%d %H:%M:%S")
        # Преобразование столбца "Дата платежа" в формат datetime
        input_df["Дата платежа"] = pd.to_datetime(input_df["Дата платежа"], format="%d.%m.%Y",
                                                       errors="coerce")
        # Отбор в результирующий DataFrame только операций за период: с 1 числа месяца по дату, переданную на вход
        filtered_df = input_df[(input_df["Дата платежа"] >= begin_day)
                                      & (input_df["Дата платежа"] <= end_day)]
        return filtered_df
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
    Функция для получения текущих курсов валют.
    Принимает на вход список кодов валют (н-р, [EUR, USD]), и обращается к сервису
    Exchange Rates Data API: https://apilayer.com/exchangerates_data-api
    """
    if currency_list != []:
        # Валюта, относительно которой определяется курс (RUB)
        convert_to = "RUB"
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
        try:
            for company in company_list:
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={company}&apikey={STOCK_API_KEY}"
                response = requests.get(url)
                response.raise_for_status()
                status_code = response.status_code
                result = response.json()
                if status_code == 200:
                    # Код для получения цены акции
                    latest_date = result["Meta Data"]["3. Last Refreshed"]
                    closing_price = result["Time Series (Daily)"][latest_date]["4. close"]
                    stock_dict = {"stock": company, "price": round(float(closing_price), 2)}
                    output_list.append(stock_dict)
                    time.sleep(1.5)
                else:
                    stock_dict = {"stock": company, "price": "unknown"}
                    output_list.append(stock_dict)
            return output_list
        except requests.exceptions.HTTPError:
            return output_list
        except:
            raise ConnectionError("Не удалось подключиться к сервису")
    else:
        return []
