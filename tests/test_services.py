import os
import pytest
from src.config import TEST_FILE_DIR
from src.services import get_last_day_of_month, profit_categories, get_tx_list, simple_search
from src.utils import read_excel_file

TEST_FILE_PATH = str(os.path.join(TEST_FILE_DIR, "test_operations.xlsx"))


@pytest.mark.parametrize(
    "month, year, expected",
    [(1, 2025, 31), (2, 2025, 28), (6, 2024, 30), (8, 2024, 31), (-5, 2025, 0), (15, 2023, 0)],
)
def test_get_last_day(month, year, expected):
    """Тест функции определения последнего дня в месяце"""
    assert get_last_day_of_month(month, year) == expected


def test_profit_categories(test_profit_json):
    """Тест функции определения выгодных категорий кешбэка"""
    df = read_excel_file(TEST_FILE_PATH)
    res = profit_categories(df, 12, 2021)
    assert res == test_profit_json


def test_profit_categories_bad_month():
    """Тест функции определения выгодных категорий кешбэка при некорректном задании месяца"""
    df = read_excel_file(TEST_FILE_PATH)
    res = profit_categories(df, 20, 2021)
    assert res == {}


def test_profit_categories_empty_df():
    """Тест функции определения выгодных категорий кешбэка, если набор данных пустой"""
    test_file_path = os.path.join(TEST_FILE_DIR, "test_empty_tx.xlsx")
    df = read_excel_file(test_file_path)
    res = profit_categories(df, 1, 2020)
    assert (res) == {}


def test_get_tx_list():
    result = get_tx_list(TEST_FILE_PATH)
    assert len(result) == 51


def test_simple_search(test_entertainments, test_flowers):
    """ Тест функции поиска операций по описанию или категории"""
    test_input_list = get_tx_list(TEST_FILE_PATH)
    result1 = simple_search("развлечения", test_input_list)
    assert result1 == test_entertainments.replace("\n", "")
    result2 = simple_search("цветы", test_input_list)
    assert result2 == test_flowers.replace("\n", "")


def test_empty_search():
    """ Тест функции поиска с пустым списком операций """
    assert simple_search("перевод", []) == "[]"