import calendar
import json
import os
import pandas as pd
import pprint

from pandas import DataFrame
from config import BASE_DIRECTORY, operations_file
from utils import read_excel_file, get_filtered_df


def get_last_day_of_month(month: int, year: int) -> int:
    """Функция определения последнего дня месяца. Возвращает кортеж (день недели 1-го дня, количество дней)"""
    day_of_week, num_days = calendar.monthrange(year, month)
    return num_days


def profit_categories(data: pd.DataFrame, work_month: int, work_year: int) -> json:
    """Функцию для анализа выгодности категорий повышенного кешбэка.
       На вход поступают данные для анализа, год и месяц.
       На выходе — JSON с анализом, сколько на каждой категории можно заработать кешбэка в указанном месяце года.
    """
    services_dict = {}
    if data.empty:
        return services_dict
    else:
        end_day = get_last_day_of_month(work_month, work_year)
        work_date = f"{work_year}-{work_month}-{end_day} 23:59:59"
        # Отбор данных за месяу
        filtered_df = get_filtered_df(data, work_date)
        # Отбор только успешных операций, со статусом, на равным FAILED, и только платежей (операция < 0)
        filtered_df = filtered_df[(filtered_df["Статус"] != "FAILED") & (filtered_df["Сумма платежа"] < 0.0)]
        # Группировка по категориям кешбэка (суммирование)
        sum_by_categories = filtered_df.groupby(by=["Категория"], sort=False)["Бонусы (включая кэшбэк)"].sum().reset_index()
        # Сортировка по столбцу "Бонусы" в порядке убывания
        sorted_df = sum_by_categories.sort_values(by=["Бонусы (включая кэшбэк)"], ascending=False)
        # Обор строк только со значениями в столбце Бонус > 0 и выбор первых 3 строу
        sorted_df = sorted_df[(sorted_df["Бонусы (включая кэшбэк)"]) > 0.0].iloc[0:3]
        # Преобразование DanaFrame в список словарей - составления словаря в формате:
        services_dict = sorted_df.to_dict(orient="records")
        # Составление выходного словаря для преобразования в json
        out_dict = {}
        # Для каждого словаря из списка словарей составляем словарь для преобразования в json
        # Ключ - название категории из поля "Категория", значение - значение из поля "Бонусы"
        for category in services_dict:
            out_dict[category["Категория"]] = category["Бонусы (включая кэшбэк)"]
        json_data = json.dumps(out_dict).encode("utf-8", "ignore").decode("unicode-escape")
        return json_data


full_data = read_excel_file(str(os.path.join(BASE_DIRECTORY, "data", operations_file)))
res = profit_categories(full_data, 3, 2021)
print(res)