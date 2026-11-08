from datetime import date, datetime, time, timedelta

import pytest

from trackcoder.errors import ValidationError
from trackcoder.timeutils import (
    format_duration,
    human_duration,
    parse_date,
    parse_duration,
    percent_change,
)


@pytest.mark.parametrize("value,expected", [
    ("02:30", 150),
    ("2:03:30", 124),
    ("2h 15m", 135),
    ("2 hours 5 minutes", 125),
    ("90m", 90),
    ("90", 90),
    (90.4, 90),
    (timedelta(minutes=42), 42),
    (time(hour=3, minute=4), 184),
])
def test_parse_duration(value, expected):
    assert parse_duration(value) == expected


@pytest.mark.parametrize("value", [
    "", "abc", "1:70", "1:20:99", "-1m", -2, None, True,
    float("nan"), float("inf"), "nan", "1:nan",
])
def test_invalid_duration_is_actionable(value):
    with pytest.raises(ValidationError):
        parse_duration(value)


def test_duration_format_does_not_wrap_after_24_hours():
    assert format_duration(1500) == "25:00"
    assert human_duration(1500) == "25h"
    assert human_duration(150) == "2h 30m"


def test_date_parser_is_strict():
    assert parse_date("2026-01-02") == date(2026, 1, 2)
    assert parse_date(datetime(2026, 1, 2, 4)) == date(2026, 1, 2)
    with pytest.raises(ValidationError, match="YYYY-MM-DD"):
        parse_date("01/02/2026")
    with pytest.raises(ValidationError):
        parse_date("2026-02-30")


def test_percent_change_handles_zero_baseline():
    assert percent_change(150, 100) == 50
    assert percent_change(50, 100) == -50
    assert percent_change(10, 0) is None
