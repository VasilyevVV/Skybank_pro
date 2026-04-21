import pytest

from src.utils import get_period

@pytest.mark.parametrize("input_date, expected",
                         [("2021-07-27 23:00:00", {"begin": "2021-07-01 00:00:00", "end": "2021-07-27 23:00:00"}),
                          ("2025-10-15 14:45:00", {"begin": "2025-10-01 00:00:00", "end": "2025-10-15 14:45:00"}),
                          ("2026-01-01 10:08:00", {"begin": "2026-01-01 00:00:00", "end": "2026-01-01 10:08:00"}),
                          ],)
def test_get_period(input_date, expected):
    """Тест функции get_period с корректными входными датами"""
    assert get_period(input_date) == expected


@pytest.mark.parametrize("input_date, expected",
                         [("2021-07-35", {}), ("2027.18.02", {}), ("no_date", {}), ("", {}),
                          ],)
def test_get_period_inv_date(input_date, expected):
    #with pytest.raises(ValueError, match="Некорректно указана дата"):
    #    get_period(input_date)
    assert get_period(input_date) == expected




