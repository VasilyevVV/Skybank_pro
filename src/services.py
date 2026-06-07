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
        services_dict = sum_by_categories.to_dict(orient="records")
        sorted_transaction = sorted(services_dict, key=lambda x: x.get("Бонусы (включая кэшбэк)"), reverse=True)
        output_dict = sorted_transaction[0:4]
        out_d = {}
        for cat in output_dict:
            out_d[cat["Категория"]] = str(cat["Бонусы (включая кэшбэк)"])
        json_data = json.dumps(out_d).encode("utf-8", "ignore").decode("unicode-escape")
        return json_data


full_data = read_excel_file(str(os.path.join(BASE_DIRECTORY, "data", operations_file)))
res = profit_categories(full_data, 10, 2021)
print(res)