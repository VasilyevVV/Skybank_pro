import json
import os

from src.config import BASE_DIRECTORY, operations_file
from src.utils import (get_exchange_rates, get_greeting, get_stocks_data, get_top_tx, get_user_settings,
                       read_excel_file, select_tx_for_period, total_expenses)

# Получение имени файла с пользовательскими списками валют и акций из файла .env
user_settings_file = os.getenv("USER_SETTINGS_JSON_FILE")


def get_main_page_data(input_date: str) -> str:
    """Функция для страницы «Главная». Принимает на вход строку с датой и временем в формате "YYYY-MM-DD HH:MM:SS"
    Отдает JSON-ответ - преобразованный из сформированного словаря
    """
    # Получение строки приветствия в зависимости от текущего времени
    main_page_dict = {"greeting": "", "cards": [], "top_transactions": [], "currency_rates": [], "stock_prices": []}
    main_page_dict["greeting"] = get_greeting()
    # Чтение Excel-файла. Должен находиться в подкаталоге data
    full_data_frame = read_excel_file(str(os.path.join(BASE_DIRECTORY, "data", operations_file)))
    # Если набор данных пустой, расчёты суммы расходов по картам и топ-5 транзакций не производятся
    if full_data_frame.empty:
        main_page_dict["cards"] = []
        main_page_dict["top_transactions"] = []
    else:
        df_by_period = select_tx_for_period(full_data_frame, input_date)
        cards_list = total_expenses(df_by_period)
        main_page_dict["cards"] = cards_list
        main_page_dict["top_transactions"] = get_top_tx(df_by_period)
    # Получение пользовательского списка валют и акций
    settings_file_path = os.path.join(BASE_DIRECTORY, user_settings_file)
    user_settings = get_user_settings(settings_file_path)
    if user_settings != {}:
        # Получение списка валют и определение курса
        user_currencies = user_settings["user_currencies"]
        main_page_dict["currency_rates"] = get_exchange_rates(user_currencies)
        # Получение списка акций и их стоимости
        user_stocks = user_settings["user_stocks"]
        main_page_dict["stock_prices"] = get_stocks_data(user_stocks)
    else:
        main_page_dict["currency_rates"] = []
        main_page_dict["stock_prices"] = []
    json_data = json.dumps(main_page_dict).encode("utf-8", "ignore").decode("unicode-escape")
    return json_data

