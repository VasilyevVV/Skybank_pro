import calendar
import json
import re

import pandas as pd

from src.utils import read_excel_file, select_tx_for_period


def get_last_day_of_month(month: int, year: int) -> int:
    """Функция определения последнего дня месяца. Возвращает кортеж (день недели 1-го дня, количество дней).
    Если значение месяца не равно значению от 1 до 12, возвращает 0.
    """
    if 1 <= month <= 12:
        day_of_week, num_days = calendar.monthrange(year, month)
        return num_days
    else:
        return 0


def profit_categories(input_df: pd.DataFrame, calc_month: int, calc_year: int) -> str:
    """Функцию для анализа выгодности категорий повышенного кешбэка.
    На вход поступают данные для анализа, год и месяц.
    На выходе — JSON с анализом, сколько на каждой категории можно заработать кешбэка в указанном месяце года.
    """
    # Если входной набор данных - пустой, возвращается пустой словарь
    if input_df.empty:
        return "{}"
    else:
        # Определение последнего дня месяца. Если месяц задан некорректно, end_day = 0, возвращается пустой словарь {}
        end_day = get_last_day_of_month(calc_month, calc_year)
        if end_day == 0:
            return "{}"
        else:
            # Если корректно определен последний день месяца (не равен 0)
            work_date = f"{calc_year}-{calc_month}-{end_day} 23:59:59"
            # Отбор данных за месяц
            filtered_df = select_tx_for_period(input_df, work_date)
            # Отбор только успешных операций, со статусом, не равным FAILED, и только платежей (операция меньше 0)
            filtered_df = filtered_df[(filtered_df["Статус"] != "FAILED") & (filtered_df["Сумма платежа"] < 0.0)]
            # Группировка по категориям кешбэка (суммирование)
            sum_by_categories = (
                filtered_df.groupby(by=["Категория"], sort=False)["Бонусы (включая кэшбэк)"].sum().reset_index()
            )
            # Сортировка по столбцу "Бонусы" в порядке убывания
            sorted_df = sum_by_categories.sort_values(by=["Бонусы (включая кэшбэк)"], ascending=False)
            # Отбор строк только со значениями в столбце Бонус > 0 и выбор первых 3 строк
            sorted_df = sorted_df[(sorted_df["Бонусы (включая кэшбэк)"]) > 0.0].iloc[0:3]
            # Преобразование отсортированного набора DanaFrame в список словарей
            services_dict = sorted_df.to_dict(orient="records")
            # Составление выходного словаря для преобразования в json
            out_dict = {}
            # Для каждого словаря из списка словарей составляем словарь для преобразования в json
            # Ключ - название категории из поля "Категория", значение - значение из поля "Бонусы"
            for category in services_dict:
                out_dict[category["Категория"]] = category["Бонусы (включая кэшбэк)"]
            json_data = json.dumps(out_dict).encode("utf-8", "ignore").decode("unicode-escape")
            return json_data


def get_tx_list(file_path: str) -> list[dict]:
    """Функция получения списка операций из Excel-файла в виде списка словарей"""
    # получение датафрейма из Excel
    tx_list = []
    excel_df = read_excel_file(file_path)
    # Если набор не пустой - преобразование его в список словарей
    if not excel_df.empty:
        tx_list = excel_df.to_dict(orient="records")
    return tx_list


def simple_search(search_str: str, input_tx: list[dict]) -> str:
    """Функция поиска транзакций, содержащих строку для поиска в описании или в категории.
    Возвращает JSON-ответ с транзакциями
    """
    if input_tx:
        # Если набор данных на входе не пустой, ищем строку поиска в столбцах "Категория" и "Описание"
        result = [
            operation
            for operation in input_tx
            if (
                isinstance(operation.get("Категория", ""), str)
                and re.search(search_str, operation["Категория"], flags=re.IGNORECASE)
            )
            or (
                isinstance(operation.get("Описание", ""), str)
                and re.search(search_str, operation["Описание"], flags=re.IGNORECASE)
            )
        ]
    else:
        # Если входной набор данных пустой, возвращается пустой список
        result = []
    return json.dumps(result, ensure_ascii=False)  # , indent=4)
