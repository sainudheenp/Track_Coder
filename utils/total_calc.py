"""All-time totals using normalized workbook records (no pandas required)."""

from trackcoder.config import Settings
from trackcoder.storage import WorkbookStore
from trackcoder.timeutils import format_duration, parse_duration


def time_to_mins(time_string):
    if time_string is None or time_string == "":
        return 0
    return parse_duration(time_string)


def minutes_time(total_time):
    return format_duration(total_time)


def total_calc():
    settings = Settings.from_env()
    records = WorkbookStore(settings.workbook_path, backups=False).all()
    html = sum(record.html for record in records)
    css = sum(record.css for record in records)
    javascript = sum(record.javascript for record in records)
    code = format_duration(sum(record.code_time_minutes for record in records))
    active = format_duration(sum(record.active_code_time_minutes for record in records))
    focus = format_duration(sum(record.focus_minutes for record in records))
    return html, css, javascript, code, active, focus, html + css + javascript
