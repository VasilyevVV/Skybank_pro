import datetime as dt
import os
from typing import Optional

import pandas as pd

from config import BASE_DIRECTORY, operations_file
from utils import read_excel_file


def spending_by_category(
    transactions: pd.DataFrame, category: str, start_date: Optional[str] = None
) -> pd.DataFrame | None:
    """Функция создаёт отчет "Траты по категориям". Принимает на вход DataFrame, название категории, опциональную дату.
    Если дата не передана, то берется текущая дата.
    Возвращает траты по заданной категории за последние три месяца (от переданной даты).
    От даты отсчитывается 3-месячный период. Выводит JSON-ответ.
    """
    if start_date is None:
        start_date = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d %H:%M:%S")
    print(start_date)
    # begin_date =  start_date - три месяца


if __name__ == "__main__":
    tx = read_excel_file(str(os.path.join(BASE_DIRECTORY, "data", operations_file)))
    spending_by_category(tx, "снятие наличных", "2025-06-02")
