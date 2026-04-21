import datetime
import json
import pprint
import os
from dotenv import load_dotenv

from utils import get_greeting, read_excel_file, total_expenses, get_top_tx, get_user_settings, get_exchange_rates, get_stocks_data
from src.config import BASE_DIRECTORY

load_dotenv()
# Получение имени файла с операциями из файла .env
file_operations = os.getenv("OPERATIONS_FILE_NAME")
# Получение имени файла с пользовательскими списками валют и акций из файла .env
user_settings_file = os.getenv("USER_SETTINGS_JSON_FILE")


def get_main_page_data(working_date: str) -> json:
    """Функция для страницы «Главная». Принимает на вход строку с датой и временем в формате "YYYY-MM-DD HH:MM:SS"
       Отдает JSON-ответ - ???
    """
    main_page_dict = {"greeting": "", "cards": [], "top_transactions": [], "currency_rates": [], "stock_prices": []}
    main_page_dict["greeting"] = get_greeting()
    file_path = os.path.join(BASE_DIRECTORY, "data", file_operations)
    main_data_frame = read_excel_file(file_path, working_date)
    cards_list = total_expenses(main_data_frame)
    main_page_dict["cards"] = cards_list
    main_page_dict["top_transactions"] = get_top_tx(main_data_frame)
    # Получение пользовательского списка валют и акций
    file_path = os.path.join(BASE_DIRECTORY, user_settings_file)
    user_settings = get_user_settings(file_path)
    if user_settings != {}:
        # Получение списка валют и определение курса
        user_currencies = user_settings["user_currencies"]
        #main_page_dict["currency_rates"] = get_exchange_rates(user_currencies)
        # Получение списка акций и их стоимости
        user_stocks = user_settings["user_stocks"]
        #main_page_dict["stock_prices"] = get_stocks_data(user_stocks)
    else:
        main_page_dict["currency_rates"] = []
        main_page_dict["stock_prices"] = []
    json_data = json.dumps(main_page_dict).encode('utf-8', 'ignore').decode('unicode-escape')
    return json_data
    #return main_page_dict

res = get_main_page_data("2020-03-31 23:55:55")
#pprint.pprint(res, sort_dicts=False)
print(res)

# with open('output_f.json', 'w') as f:
#     json.dump(res, f, ensure_ascii=True)


