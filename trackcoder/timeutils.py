"""Strict date and duration parsing shared by every input/output format."""

from __future__ import annotations

import math
import re
from datetime import date, datetime, time, timedelta
from numbers import Real
from typing import Any

from .errors import ValidationError

_DURATION_RE = re.compile(
    r"^\s*(?:(?P<hours>\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours))?"
    r"\s*(?:(?P<minutes>\d+(?:\.\d+)?)\s*(?:m|min|mins|minute|minutes))?\s*$",
    re.IGNORECASE,
)


def parse_date(value: str | date | datetime, *, field: str = "date") -> date:
    """Return a date, rejecting ambiguous formats instead of guessing."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValidationError(f"{field} must use YYYY-MM-DD format.")
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValidationError(
            f"Invalid {field} {value!r}; expected a real date in YYYY-MM-DD format."
        ) from exc


def parse_duration(value: Any, *, field: str = "duration") -> int:
    """Parse a duration into whole minutes.

    Accepted text forms include ``HH:MM``, ``HH:MM:SS``, ``2h 15m`` and
    ``90m``. Numeric values are interpreted as minutes. Seconds are rounded to
    the nearest minute, matching the precision of the Excel workbook.
    """
    if value is None or isinstance(value, bool):
        raise ValidationError(f"{field} is required and cannot be negative.")
    if isinstance(value, timedelta):
        seconds = value.total_seconds()
        if seconds < 0:
            raise ValidationError(f"{field} cannot be negative.")
        return round(seconds / 60)
    if isinstance(value, time):
        return value.hour * 60 + value.minute
    if isinstance(value, Real):
        minutes = float(value)
        if not math.isfinite(minutes):
            raise ValidationError(f"{field} must be a finite number.")
        if minutes < 0:
            raise ValidationError(f"{field} cannot be negative.")
        return round(minutes)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} is required and cannot be blank.")

    text = value.strip()
    if ":" in text:
        parts = text.split(":")
        if len(parts) not in (2, 3):
            raise ValidationError(f"Invalid {field} {value!r}; use HH:MM or HH:MM:SS.")
        try:
            numbers = [float(part) for part in parts]
        except ValueError as exc:
            raise ValidationError(f"Invalid {field} {value!r}; use HH:MM or HH:MM:SS.") from exc
        hours, minutes = numbers[:2]
        seconds = numbers[2] if len(numbers) == 3 else 0
        if not all(math.isfinite(number) for number in numbers):
            raise ValidationError(f"{field} must contain only finite numbers.")
        if hours < 0 or not 0 <= minutes < 60 or not 0 <= seconds < 60:
            raise ValidationError(
                f"Invalid {field} {value!r}; minutes and seconds must be between 0 and 59."
            )
        return round(hours * 60 + minutes + seconds / 60)

    match = _DURATION_RE.fullmatch(text)
    if match and (match.group("hours") is not None or match.group("minutes") is not None):
        hours = float(match.group("hours") or 0)
        minutes = float(match.group("minutes") or 0)
        total = hours * 60 + minutes
        if not math.isfinite(total):
            raise ValidationError(f"{field} must be a finite duration.")
        return round(total)

    try:
        minutes = float(text)
    except ValueError as exc:
        raise ValidationError(
            f"Invalid {field} {value!r}; try '02:30', '2h 30m', or '150m'."
        ) from exc
    if not math.isfinite(minutes):
        raise ValidationError(f"{field} must be a finite number.")
    if minutes < 0:
        raise ValidationError(f"{field} cannot be negative.")
    return round(minutes)


def format_duration(minutes: int) -> str:
    """Format minutes without wrapping after 24 hours."""
    minutes = parse_duration(minutes)
    hours, remainder = divmod(minutes, 60)
    return f"{hours:02d}:{remainder:02d}"


def human_duration(minutes: int) -> str:
    """Format a compact duration for reports."""
    minutes = parse_duration(minutes)
    hours, remainder = divmod(minutes, 60)
    if hours and remainder:
        return f"{hours}h {remainder:02d}m"
    if hours:
        return f"{hours}h"
    return f"{remainder}m"


def percent_change(current: float, previous: float) -> float | None:
    """Return percentage change, or None when the baseline has no meaning."""
    if previous == 0:
        return None
    return (current - previous) / abs(previous) * 100
