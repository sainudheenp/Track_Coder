"""Domain models for daily coding activity."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import date
from numbers import Integral, Real
from typing import Any

from .errors import ValidationError
from .timeutils import format_duration


@dataclass(frozen=True, slots=True)
class DailyMetrics:
    """A normalized daily record.

    Durations are stored as minutes in code and as HH:MM in Excel/CSV. A missing
    WPM observation is represented by ``None``; zero is never used as a fake
    measurement.
    """

    day: date
    focus_minutes: int = 0
    wpm: float | None = None
    code_time_minutes: int = 0
    active_code_time_minutes: int = 0
    html: int = 0
    css: int = 0
    javascript: int = 0
    notes: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.day, date):
            raise ValidationError("DailyMetrics.day must be a date.")
        for name in (
            "focus_minutes",
            "code_time_minutes",
            "active_code_time_minutes",
            "html",
            "css",
            "javascript",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Integral) or value < 0:
                raise ValidationError(f"{name} must be a non-negative integer.")
        if self.wpm is not None:
            if (
                isinstance(self.wpm, bool) or not isinstance(self.wpm, Real)
                or not math.isfinite(float(self.wpm)) or self.wpm < 0
            ):
                raise ValidationError("wpm must be a finite non-negative number or None.")
            object.__setattr__(self, "wpm", float(self.wpm))
        if not isinstance(self.notes, str):
            raise ValidationError("notes must be text.")

    @property
    def total_lines(self) -> int:
        return self.html + self.css + self.javascript

    @property
    def is_active(self) -> bool:
        """A coding day requires coding time or changed lines, not WPM alone."""
        return bool(
            self.focus_minutes
            or self.code_time_minutes
            or self.active_code_time_minutes
            or self.total_lines
        )

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation with explicit minute units."""
        result = asdict(self)
        result["date"] = self.day.isoformat()
        del result["day"]
        result["total_lines"] = self.total_lines
        result["is_active"] = self.is_active
        return result

    def as_csv_row(self) -> dict[str, Any]:
        return {
            "date": self.day.isoformat(),
            "focus": format_duration(self.focus_minutes),
            "wpm": "" if self.wpm is None else self.wpm,
            "code_time": format_duration(self.code_time_minutes),
            "active_code_time": format_duration(self.active_code_time_minutes),
            "html": self.html,
            "css": self.css,
            "javascript": self.javascript,
            "total_lines": self.total_lines,
            "notes": self.notes,
        }
