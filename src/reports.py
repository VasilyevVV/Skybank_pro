import datetime as dt


from functools import wraps
from time import localtime, strftime, time
from typing import Any, Callable, Optional

import pandas as pd


from src.utils import read_excel_file, get_begin_date


# def log(filename=None) -> Any:
#     """Функция-декоратор: автоматически логирует начало и конец выполнения функции, а также ее результаты
#     или возникшие ошибки. Необязательный аргумент filename определяет, куда будут записываться логи:
#     - если filename задан, логи записываются в указанный файл
#     - если filename не задан, логи выводятся в консоль.
#     """
#
#     def decorator(func: Callable) -> Callable:
#         @wraps(func)
#         def wrapped(*args, **kwargs) -> Any:
#             start_time = time()
#             # Попытка вызвать функцию и получить результат, с фиксацией времени начала и окончания
#             try:
#                 result = func(*args, **kwargs)
#                 end_time = time()
#                 # Формирование строки об успешном завершении
#                 log_string = (
#                     f"Функция: {func.__name__}: OK. "
#                     f"Старт: {strftime('%Y-%m-%d %H:%M:%S', localtime(start_time))} "
#                     f"Стоп: {strftime('%Y-%m-%d %H:%M:%S', localtime(end_time))}."
#                 )
#             except Exception as exc:
#                 result = "ERROR"
#                 # Формирование сообщения об ошибке
#                 log_string = f"{func.__name__}: {result}: {str(exc)}. Inputs: {args}, {kwargs}."
#             # Если имя лог-файла указано, открываем его в режиме добавления записей
#             if filename:
#                 with open(filename, "a+t", encoding="utf-8") as log_file:
#                     print(log_string, file=log_file)
#             else:
#                 # Если имя лог-файла не задано - вывод в консоль
#                 print(log_string)
#             return result
#
#         return wrapped
#
#     return decorator


def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         input_date: Optional[str] = None) -> pd.DataFrame | None:
    """Функция создаёт отчет "Траты по категориям". Принимает на вход DataFrame, название категории, опциональную дату.
       Если дата не передана, то берется текущая дата.
       Возвращает траты по заданной категории за последние три месяца (от переданной даты).
       От даты отсчитывается 3-месячный период. Выводит JSON-ответ.
    """
    # Определение конечной даты для отчётного периода
    # Если дата не передана, то берется текущая дата
    if input_date is None:
        end_day = dt.datetime.now()
    else:
        # если дата передана в формате ГГГГ.ММ.ДД, то она преобразуется в формат даты
        # с добавлением часов, минут и секунд на конец дня
        end_day = dt.datetime.strptime(input_date, "%Y.%m.%d").replace(hour=23,minute=59,second=59)
    # Получение начала отчетного периода - минус три месяца от заданной даты
    begin_period = get_begin_date(end_day, -3)
    end_period = dt.datetime.strftime(end_day, "%Y.%m.%d %H:%M:%S" )
    # Преобразование столбца "Дата платежа" в формат datetime
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y", errors="coerce")
    # Отбор трат (сумма платежа < 0) по заданной категории за период
    filtered_df = transactions[(transactions["Дата платежа"] >= begin_period) &
                               (transactions["Дата платежа"] <= end_period) &
                               (transactions["Сумма платежа"] <= 0) &
                               (transactions["Категория"] == category)]
    return filtered_df

