from datetime import date, timedelta

from trackcoder.analytics import build_report, current_streak, longest_streak
from trackcoder.config import Goals
from trackcoder.models import DailyMetrics


def record(day, *, code=0, focus=0, lines=0, wpm=None):
    return DailyMetrics(
        day=day, code_time_minutes=code, focus_minutes=focus,
        html=lines, wpm=wpm,
    )


def test_streaks_count_only_consecutive_active_days():
    records = [
        record(date(2026, 1, 1), code=30),
        record(date(2026, 1, 2), lines=10),
        record(date(2026, 1, 3), wpm=80),  # WPM alone is not a coding day.
        record(date(2026, 1, 4), focus=45),
    ]
    assert longest_streak(records).length == 2
    current = current_streak(records, as_of=date(2026, 1, 5))
    assert current.length == 1
    assert current.start == date(2026, 1, 4)
    assert current_streak(records, as_of=date(2026, 1, 6)).length == 0


def test_empty_streak_has_no_dates():
    streak = longest_streak([record(date(2026, 1, 1))])
    assert streak.length == 0
    assert streak.start is None


def test_period_report_compares_previous_equal_period_and_ignores_missing_wpm():
    end = date(2026, 2, 10)
    records = [
        record(end - timedelta(days=1), code=120, focus=100, lines=100, wpm=50),
        record(end, code=60, focus=50, lines=50, wpm=70),
        record(end - timedelta(days=5), code=60, focus=50, lines=25),
        record(end - timedelta(days=4), code=60, focus=50, lines=25),
    ]
    report = build_report(
        records, end=end, days=3,
        goals=Goals(daily_focus_minutes=50, weekly_code_time_minutes=70, weekly_lines=70),
    )
    assert report.period.code_time_minutes == 180
    assert report.previous.code_time_minutes == 120
    assert report.change("code_time_minutes") == 50
    assert report.period.total_lines == 150
    assert report.period.average_wpm == 60
    assert report.period.active_days == 2
    assert report.goals[0].target == 150
    assert report.goals[1].target == 30
    assert report.goals[2].target == 30
    assert report.insights


def test_empty_period_has_helpful_insight():
    report = build_report([], end=date(2026, 1, 1), days=7)
    assert report.period.records == ()
    assert "trackcoder log" in report.insights[0]
