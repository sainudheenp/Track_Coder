"""Compatibility wrapper around the safe workbook repository."""

from __future__ import annotations

from trackcoder.config import Settings
from trackcoder.models import DailyMetrics
from trackcoder.storage import WorkbookStore
from trackcoder.timeutils import parse_date, parse_duration


def xl_rw(Focus, Wpm, CT, ACT, HTML, CSS, JS, TOTAL, yesterday):
    settings = Settings.from_env()
    wpm = None if Wpm is None or Wpm == "" else float(Wpm)
    record = DailyMetrics(
        day=parse_date(yesterday),
        focus_minutes=parse_duration(Focus, field="Focus"),
        wpm=wpm,
        code_time_minutes=parse_duration(CT, field="CT"),
        active_code_time_minutes=parse_duration(ACT, field="ACT"),
        html=int(HTML), css=int(CSS), javascript=int(JS),
    )
    store = WorkbookStore(settings.workbook_path, backups=settings.backups)
    _, _, days, _ = store.upsert(record)
    return days
