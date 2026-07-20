import os
import pytest
from numpy.ma.core import shape

from src.config import TEST_FILE_DIR
from src.utils import read_excel_file
from src.reports import spending_by_category

# Путь к тестовому Excel-файлу с операциями, для использования в нескольких тестовых функциях
TEST_FILE_PATH = str(os.path.join(TEST_FILE_DIR, "test_operations.xlsx"))


@pytest.mark.parametrize(
    "test_categories, expected",
    [
        ("Переводы", (4, 15)),
        ("Супермаркеты", (7, 15)),
        ("Госуслуги", (2, 15)),
        ("Пополнения", (0, 15)),
        ("WSZ", (0, 15)),
    ],
)
def test_spending_by_category(test_categories, expected):
    """Тест функции отбора операций по категориям """
    df = read_excel_file(TEST_FILE_PATH)
    result = spending_by_category(df, test_categories, "2021.12.31")
    assert shape(result) == expected


def test_spending_by_category_no_date():
    df = read_excel_file(TEST_FILE_PATH)
    result = spending_by_category(df, "Переводы")
    assert shape(result) == (0, 15)
