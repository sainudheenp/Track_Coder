"""Pure parsing and calculation helpers for Software.com graph labels."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import CollectionError


@dataclass(frozen=True, slots=True)
class SoftwareMetrics:
    focus_minutes: int
    active_code_time_minutes: int
    code_time_minutes: int


def minutes_from_aria(label: str | None) -> int:
    """Extract minutes from labels such as ``Mon, 90. Active Code Time``."""
    if not label:
        raise CollectionError("Software.com graph returned an empty accessibility label.")
    parts = label.split(",")
    if len(parts) < 2:
        raise CollectionError(f"Unrecognized Software.com graph label: {label!r}")
    match = re.search(r"\d+(?:\.\d+)?", parts[1])
    if not match:
        raise CollectionError(f"Software.com graph label contains no duration: {label!r}")
    return round(float(match.group()))


def calculate_software_metrics(
    active_minutes: int, code_minutes: int, *, focus_override: int | None = None,
) -> SoftwareMetrics:
    """Preserve the project's established CT and estimated-focus definitions.

    CT is active code time plus non-active code time. The historical focus
    estimate adds one hour when CT is non-zero; users can and should override
    that estimate with an observed focus duration when available.
    """
    if min(active_minutes, code_minutes) < 0:
        raise CollectionError("Software.com durations cannot be negative.")
    total_code = active_minutes + code_minutes
    focus = focus_override
    if focus is None:
        focus = total_code + 60 if total_code else 0
    if focus < 0:
        raise CollectionError("Focus duration cannot be negative.")
    return SoftwareMetrics(focus, active_minutes, total_code)
