"""Dependency-free analytics for periods, trends, goals, and streaks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from statistics import mean
from typing import Iterable

from .config import Goals
from .models import DailyMetrics
from .timeutils import human_duration, percent_change


@dataclass(frozen=True, slots=True)
class Streak:
    length: int
    start: date | None = None
    end: date | None = None


@dataclass(frozen=True, slots=True)
class PeriodSummary:
    start: date
    end: date
    records: tuple[DailyMetrics, ...]
    focus_minutes: int
    code_time_minutes: int
    active_code_time_minutes: int
    html: int
    css: int
    javascript: int
    total_lines: int
    active_days: int
    average_wpm: float | None

    @property
    def elapsed_days(self) -> int:
        return (self.end - self.start).days + 1

    @property
    def consistency(self) -> float:
        return self.active_days / self.elapsed_days * 100 if self.elapsed_days else 0


@dataclass(frozen=True, slots=True)
class GoalProgress:
    name: str
    actual: int
    target: int
    kind: str

    @property
    def percentage(self) -> float:
        return self.actual / self.target * 100 if self.target else 0

    @property
    def remaining(self) -> int:
        return max(self.target - self.actual, 0)

    def format_actual(self) -> str:
        return f"{self.actual:,}" if self.kind == "lines" else human_duration(self.actual)

    def format_target(self) -> str:
        return f"{self.target:,}" if self.kind == "lines" else human_duration(self.target)


@dataclass(frozen=True, slots=True)
class AnalyticsReport:
    period: PeriodSummary
    previous: PeriodSummary
    current_streak: Streak
    best_streak: Streak
    goals: tuple[GoalProgress, ...]
    insights: tuple[str, ...]

    def change(self, metric: str) -> float | None:
        return percent_change(getattr(self.period, metric), getattr(self.previous, metric))


def _summarize(records: Iterable[DailyMetrics], start: date, end: date) -> PeriodSummary:
    selected = tuple(sorted((r for r in records if start <= r.day <= end), key=lambda r: r.day))
    wpm_values = [r.wpm for r in selected if r.wpm is not None]
    return PeriodSummary(
        start=start,
        end=end,
        records=selected,
        focus_minutes=sum(r.focus_minutes for r in selected),
        code_time_minutes=sum(r.code_time_minutes for r in selected),
        active_code_time_minutes=sum(r.active_code_time_minutes for r in selected),
        html=sum(r.html for r in selected),
        css=sum(r.css for r in selected),
        javascript=sum(r.javascript for r in selected),
        total_lines=sum(r.total_lines for r in selected),
        active_days=sum(r.is_active for r in selected),
        average_wpm=mean(wpm_values) if wpm_values else None,
    )


def longest_streak(records: Iterable[DailyMetrics]) -> Streak:
    days = sorted({r.day for r in records if r.is_active})
    if not days:
        return Streak(0)
    best = current = Streak(1, days[0], days[0])
    for day in days[1:]:
        if current.end is not None and day == current.end + timedelta(days=1):
            current = Streak(current.length + 1, current.start, day)
        else:
            current = Streak(1, day, day)
        if current.length > best.length:
            best = current
    return best


def current_streak(records: Iterable[DailyMetrics], *, as_of: date) -> Streak:
    """Calculate a streak with one grace day for an unfinished current day."""
    active = {r.day for r in records if r.is_active}
    cursor = as_of
    if cursor not in active:
        cursor -= timedelta(days=1)
    if cursor not in active:
        return Streak(0)
    end = cursor
    while cursor in active:
        cursor -= timedelta(days=1)
    start = cursor + timedelta(days=1)
    return Streak((end - start).days + 1, start, end)


def _goals(period: PeriodSummary, goals: Goals) -> tuple[GoalProgress, ...]:
    weeks = period.elapsed_days / 7
    return (
        GoalProgress(
            "Focus", period.focus_minutes,
            round(goals.daily_focus_minutes * period.elapsed_days), "time",
        ),
        GoalProgress(
            "Code time", period.code_time_minutes,
            round(goals.weekly_code_time_minutes * weeks), "time",
        ),
        GoalProgress(
            "Lines of code", period.total_lines,
            round(goals.weekly_lines * weeks), "lines",
        ),
    )


def _insights(report: AnalyticsReport) -> tuple[str, ...]:
    period = report.period
    if not period.records:
        return ("No entries in this period yet. Use 'trackcoder log' to add one without a browser.",)

    insights: list[str] = []
    code_change = report.change("code_time_minutes")
    if code_change is not None:
        direction = "up" if code_change >= 0 else "down"
        insights.append(f"Code time is {direction} {abs(code_change):.0f}% versus the previous {period.elapsed_days} days.")
    elif period.code_time_minutes:
        insights.append("Code time has a new baseline; the previous period had no recorded code time.")

    if period.records:
        best_day = max(period.records, key=lambda r: (r.focus_minutes, r.total_lines))
        if best_day.is_active:
            insights.append(
                f"Strongest focus day: {best_day.day.isoformat()} ({human_duration(best_day.focus_minutes)})."
            )

    languages = {"JavaScript/JSX": period.javascript, "HTML": period.html, "CSS": period.css}
    dominant = max(languages, key=languages.get)
    if languages[dominant] > 0:
        share = languages[dominant] / period.total_lines * 100
        insights.append(f"{dominant} accounts for {share:.0f}% of tracked lines in this period.")

    unfinished = [goal for goal in report.goals if goal.remaining > 0]
    if unfinished:
        goal = min(unfinished, key=lambda item: item.percentage)
        remaining = (
            f"{goal.remaining:,} lines" if goal.kind == "lines"
            else human_duration(goal.remaining)
        )
        insights.append(
            f"Next milestone: {goal.name.lower()} needs {remaining} to reach its prorated goal."
        )
    else:
        insights.append("All prorated goals are complete. Consider raising one target for the next period.")
    return tuple(insights)


def build_report(
    records: Iterable[DailyMetrics], *, end: date, days: int = 30, goals: Goals = Goals(),
) -> AnalyticsReport:
    if days <= 0:
        raise ValueError("days must be greater than zero")
    materialized = tuple(records)
    start = end - timedelta(days=days - 1)
    period = _summarize(materialized, start, end)
    previous = _summarize(materialized, start - timedelta(days=days), start - timedelta(days=1))
    # Build once without insights, then attach derived observations.
    partial = AnalyticsReport(
        period=period,
        previous=previous,
        current_streak=current_streak(materialized, as_of=end),
        best_streak=longest_streak(materialized),
        goals=_goals(period, goals),
        insights=(),
    )
    return AnalyticsReport(
        period=partial.period,
        previous=partial.previous,
        current_streak=partial.current_streak,
        best_streak=partial.best_streak,
        goals=partial.goals,
        insights=_insights(partial),
    )
