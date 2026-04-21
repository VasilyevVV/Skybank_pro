import pytest
from freezegun import freeze_time
from unittest.mock import Mock, patch

from src.utils import get_greeting, get_period


# Тест функции получения строки приветствия в зависимости от времени суток
@pytest.mark.parametrize("now_hour, expected", [("2026-01-01 03:00:00", "Доброй ночи!"),
                                                ("2026-01-01 07:00:00", "Доброе утро!"),
                                                ("2026-01-01 12:00:00", "Добрый день!"),
                                                ("2026-01-01 21:00:00", "Добрый вечер!"),
                                                ])
def test_get_greeting(now_hour, expected):
    with freeze_time(now_hour):
        assert get_greeting() == expected


@pytest.mark.parametrize("input_date, expected",
                         [("2021-07-27 23:00:00", {"begin": "2021-07-01 00:00:00", "end": "2021-07-27 23:00:00"}),
                          ("2025-10-15 14:45:00", {"begin": "2025-10-01 00:00:00", "end": "2025-10-15 14:45:00"}),
                          ("2026-01-01 10:08:00", {"begin": "2026-01-01 00:00:00", "end": "2026-01-01 10:08:00"}),
                          ], )
def test_get_period(input_date, expected):
    """Тест функции get_period с корректными входными датами"""
    assert get_period(input_date) == expected


@pytest.mark.parametrize("input_date, expected",
                         [("2021-07-35", {}), ("2027.18.02", {}), ("no_date", {}), ("", {}),
                          ], )
def test_get_period_inv_date(input_date, expected):
    # with pytest.raises(ValueError, match="Некорректно указана дата"):
    #    get_period(input_date)
    assert get_period(input_date) == expected
