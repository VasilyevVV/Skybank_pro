import datetime as dt
import pprint
from views import get_main_page_data


if __name__ == '__main__':
    # current_date = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d %H:%M:%S")
    # res = get_main_page_data(current_date)
    res = get_main_page_data("2021-12-30 23:00:00")
    print(res)
