"""Optional Google Sheets destination backed by a service account."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from .errors import ConfigurationError, StorageError
from .models import DailyMetrics
from .timeutils import format_duration

SHEET_HEADERS = [
    "Date", "Focus", "WPM", "Code Time", "Active Code Time",
    "HTML", "CSS", "JavaScript", "Total Lines", "Active Day", "Notes",
]


def sheet_rows(records: Iterable[DailyMetrics]) -> list[list[object]]:
    rows: list[list[object]] = [SHEET_HEADERS]
    for record in sorted(records, key=lambda item: item.day):
        rows.append([
            record.day.isoformat(),
            format_duration(record.focus_minutes),
            "" if record.wpm is None else record.wpm,
            format_duration(record.code_time_minutes),
            format_duration(record.active_code_time_minutes),
            record.html,
            record.css,
            record.javascript,
            record.total_lines,
            "Yes" if record.is_active else "No",
            record.notes,
        ])
    return rows


def sync_to_google_sheets(
    records: Iterable[DailyMetrics], *, spreadsheet_id: str | None = None,
    credentials_file: str | Path | None = None, worksheet_name: str | None = None,
    dry_run: bool = False,
) -> str:
    """Replace a dedicated worksheet in one batch, avoiding row-by-row quota use."""
    sheet_id = spreadsheet_id or os.getenv("GOOGLE_SHEET_ID")
    credentials = credentials_file or os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
    worksheet = worksheet_name or os.getenv("GOOGLE_SHEETS_WORKSHEET", "Track Coder")
    if dry_run:
        rows = sheet_rows(records)
        return f"Dry run: {len(rows) - 1} records ready for worksheet '{worksheet}'."
    if not sheet_id:
        raise ConfigurationError("Set GOOGLE_SHEET_ID or pass --spreadsheet-id.")
    if not credentials:
        raise ConfigurationError(
            "Set GOOGLE_SHEETS_CREDENTIALS_FILE or pass --credentials-file."
        )
    credential_path = Path(credentials).expanduser()
    if not credential_path.is_file():
        raise ConfigurationError(f"Google service-account file not found: {credential_path}")
    rows = sheet_rows(records)

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError as exc:
        raise ConfigurationError(
            "Google Sheets support is optional. Install it with 'pip install -e .[sheets]'."
        ) from exc

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ]
    try:
        account = Credentials.from_service_account_file(str(credential_path), scopes=scopes)
        client = gspread.authorize(account)
        spreadsheet = client.open_by_key(sheet_id)
        try:
            target = spreadsheet.worksheet(worksheet)
        except gspread.WorksheetNotFound:
            target = spreadsheet.add_worksheet(
                title=worksheet, rows=max(len(rows) + 20, 100), cols=len(SHEET_HEADERS),
            )
        target.clear()
        target.update(range_name="A1", values=rows)
        target.freeze(rows=1)
        return f"Synced {len(rows) - 1} records to '{spreadsheet.title}' / '{worksheet}'."
    except Exception as exc:
        raise StorageError(f"Google Sheets sync failed: {exc}") from exc
