import datetime as dt
import os

from src.config import BASE_DIRECTORY, operations_file
from src.views import get_main_page_data
from src.services import get_profit_categories
from src.reports import spending_by_category
from src.utils import read_excel_file


if __name__ == "__main__":
    # Ввод даты для отображения информации на главной странице. Если дата не введена, используются текущие дата и время
    input_date = input("Введите дату (ГГГГ-ММ-ДД), либо нажмите \"Ввод\", чтобы использовать текущую дату: ")
    date_time_obj = dt.datetime.now()
    current_date = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d %H:%M:%S")
    if input_date:
        try:
            date_time_obj = dt.datetime.strptime(input_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            current_date = dt.datetime.strftime(date_time_obj, "%Y-%m-%d %H:%M:%S")
        except:
            print("Некорректно указана дата.\nБудет использована текущая дата")


    # Получения информации для вывода на странице "Главная"
    main_page_json = get_main_page_data(current_date)

    # Чтение файла с операциями и получение выгодных категорий кешбэка за указанный месяц и год
    main_df = read_excel_file(str(os.path.join(BASE_DIRECTORY, "data", operations_file)))
    profit_categories = get_profit_categories(main_df, date_time_obj.month, date_time_obj.year)


