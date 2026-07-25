import datetime as dt
import json
import os
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

from src.config import BASE_DIRECTORY
from src.utils import get_begin_date


def to_json_decorator() -> Any:
    """Декоратор для сохранения результатов расчёта из DataFrame в JSON-файлы. Имя файла генерируется в функции"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapped(*args, **kwargs) -> Any:
            # Попытка вызвать функцию и получить результат
            result = func(*args, **kwargs)
            # Сохранение результата (DataFrame) в словарь
            if not result.empty:
                json_data = result.to_dict(orient="index")
                # Формирование имени файла
                file_name = f'report_{func.__name__}_{dt.datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.json'
                # Путь к каталогу logs, в котором сохраняется файл
                jf_path = os.path.join(BASE_DIRECTORY, "logs", file_name)
                # Запись результата в JSON-файл
                with open(jf_path, "w", encoding="utf-8") as jf:
                    # Запись в файл первого (и единственного) элемента словаря
                    json.dump(json_data[0], jf, ensure_ascii=False, indent=2)

            return result

        return wrapped

    return decorator


def multi_line_decorator() -> Any:
    """Декоратор для сохранения результатов расчёта из DataFrame в JSON-файлы, для многострочных объектов DataFrame.
    Имя файла генерируется в функции
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapped(*args, **kwargs) -> Any:
            # Попытка вызвать функцию и получить результат
            result = func(*args, **kwargs)
            # Сохранение результата (DataFrame) в словарь
            if not result.empty:
                json_data = result.to_dict(orient="records")
                # Формирование имени файла
                file_name = f'report_{func.__name__}_{dt.datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.json'
                # Путь к каталогу logs, в котором сохраняется файл
                json_path = os.path.join(BASE_DIRECTORY, "logs", file_name)
                # Словарь для заполнения и последующей записи в JSON-файл
                out_dict = {}
                # Получение списка названий столбцов в полученном DataFrame -
                column_list = result.columns.tolist()
                # Ключом в словаре будет название 1-го столбца, значение - из столбца "Сумма"
                for item in json_data:
                    # Ключ - название
                    out_dict[item[column_list[0]]] = round(item["Сумма"], 2)
                # Запись заполненного словаря в JSON-файл
                with open(json_path, "w", encoding="utf-8") as jf:
                    json.dump(out_dict, jf, ensure_ascii=False, indent=2)
            return result

        return wrapped

    return decorator


# @to_json_decorator()
@multi_line_decorator()
def spending_by_category(
    transactions: pd.DataFrame, category: str, input_date: Optional[str] = None
) -> pd.DataFrame | None:
    """Функция создаёт отчет "Траты по категори". Принимает на вход DataFrame, название категории, опциональную дату.
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
        end_day = dt.datetime.strptime(input_date, "%Y.%m.%d").replace(hour=23, minute=59, second=59)
    # Получение начала отчетного периода - минус три месяца от заданной даты
    begin_period = get_begin_date(end_day, -3)
    end_period = dt.datetime.strftime(end_day, "%Y.%m.%d %H:%M:%S")
    # Преобразование столбца "Дата платежа" в формат datetime
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y", errors="coerce")
    # Отбор трат (сумма платежа < 0) по заданной категории за период
    filtered_df = transactions[
        (transactions["Дата платежа"] >= begin_period)
        & (transactions["Дата платежа"] <= end_period)
        & (transactions["Сумма платежа"] <= 0)
        & (transactions["Категория"] == category)
    ]
    # Расчёт суммы трат по категории и переименование столбца
    summed_df = filtered_df.groupby(by=["Категория"], sort=False)["Сумма платежа"].sum().reset_index(name="Сумма")
    return summed_df
