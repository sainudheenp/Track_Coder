"""Safe, idempotent Excel persistence for daily metrics."""

from __future__ import annotations

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .errors import StorageError, ValidationError
from .models import DailyMetrics
from .timeutils import format_duration, parse_date, parse_duration

BASE_HEADERS = ["Date", "Focus", "Wpm", "CT", "ACT", "HTML", "CSS", "JS", "Total", "Days"]
HEADERS = [*BASE_HEADERS, "Notes"]
REQUIRED_HEADERS = set(BASE_HEADERS) - {"Days"}


class WorkbookStore:
    """Read and update the original workbook format without external services.

    Writes are atomic, existing files are backed up by default, and writing an
    existing date updates it instead of creating a duplicate. No corrupt source
    workbook is ever deleted automatically.
    """

    def __init__(self, path: str | Path, *, backups: bool = True) -> None:
        self.path = Path(path).expanduser().resolve()
        self.backups = backups

    def _load(self):
        try:
            if self.path.exists():
                workbook = openpyxl.load_workbook(self.path)
                sheet = workbook.active
            else:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.title = "Daily Metrics"
                sheet.append(HEADERS)
        except Exception as exc:
            raise StorageError(
                f"Cannot open workbook {self.path}: {exc}. The original file was left unchanged."
            ) from exc

        headers = [sheet.cell(1, column).value for column in range(1, sheet.max_column + 1)]
        if not any(headers):
            sheet.delete_rows(1, max(1, sheet.max_row))
            sheet.append(HEADERS)
            headers = HEADERS.copy()
        missing = REQUIRED_HEADERS - {str(value) for value in headers if value is not None}
        if missing:
            workbook.close()
            raise StorageError(
                f"Workbook {self.path} is missing required columns: {', '.join(sorted(missing))}."
            )
        if "Days" not in headers:
            headers.append("Days")
            sheet.cell(1, len(headers), "Days")
        if "Notes" not in headers:
            headers.append("Notes")
            sheet.cell(1, len(headers), "Notes")
        self._style(sheet, len(headers))
        return workbook, sheet, {str(name): index + 1 for index, name in enumerate(headers)}

    @staticmethod
    def _style(sheet, column_count: int) -> None:
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = f"A1:{get_column_letter(column_count)}{max(sheet.max_row, 1)}"
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="172554")
            cell.alignment = Alignment(horizontal="center")
        widths = {"A": 13, "B": 11, "C": 9, "D": 11, "E": 11, "J": 9, "K": 42}
        for column, width in widths.items():
            sheet.column_dimensions[column].width = width

    @staticmethod
    def _day_from_row(sheet, row: int, columns: dict[str, int]):
        raw = sheet.cell(row, columns["Date"]).value
        if raw is None or raw == "":
            return None
        try:
            return parse_date(raw, field=f"Date at row {row}")
        except ValidationError as exc:
            raise StorageError(f"Invalid workbook data in {sheet.title}: {exc}") from exc

    @staticmethod
    def _record_from_row(sheet, row: int, columns: dict[str, int]) -> DailyMetrics | None:
        day = WorkbookStore._day_from_row(sheet, row, columns)
        if day is None:
            return None

        def raw(name: str, default: Any = 0) -> Any:
            value = sheet.cell(row, columns[name]).value
            return default if value is None or value == "" else value

        try:
            wpm_value = raw("Wpm", None)
            wpm = None if wpm_value is None else float(wpm_value)
            return DailyMetrics(
                day=day,
                focus_minutes=parse_duration(raw("Focus"), field=f"Focus at row {row}"),
                wpm=wpm,
                code_time_minutes=parse_duration(raw("CT"), field=f"CT at row {row}"),
                active_code_time_minutes=parse_duration(raw("ACT"), field=f"ACT at row {row}"),
                html=int(raw("HTML")),
                css=int(raw("CSS")),
                javascript=int(raw("JS")),
                notes=str(raw("Notes", "")),
            )
        except (ValueError, TypeError, ValidationError) as exc:
            raise StorageError(f"Invalid workbook data at row {row}: {exc}") from exc

    def all(self) -> list[DailyMetrics]:
        """Return records sorted by date, with the last duplicate taking precedence."""
        workbook, sheet, columns = self._load()
        try:
            by_date = {}
            for row in range(2, sheet.max_row + 1):
                record = self._record_from_row(sheet, row, columns)
                if record is not None:
                    by_date[record.day] = record
            return [by_date[key] for key in sorted(by_date)]
        finally:
            workbook.close()

    def get(self, day) -> DailyMetrics | None:
        target = parse_date(day)
        workbook, sheet, columns = self._load()
        try:
            found = None
            for row in range(2, sheet.max_row + 1):
                if self._day_from_row(sheet, row, columns) == target:
                    found = self._record_from_row(sheet, row, columns)
            return found
        finally:
            workbook.close()

    def _write_record(self, sheet, row: int, columns: dict[str, int], record: DailyMetrics) -> None:
        values = {
            "Date": record.day.isoformat(),
            "Focus": format_duration(record.focus_minutes),
            "Wpm": record.wpm,
            "CT": format_duration(record.code_time_minutes),
            "ACT": format_duration(record.active_code_time_minutes),
            "HTML": record.html,
            "CSS": record.css,
            "JS": record.javascript,
            "Total": record.total_lines,
            "Notes": record.notes,
        }
        for name, value in values.items():
            # openpyxl's cell(..., value=None) does not clear an existing cell.
            cell = sheet.cell(row, columns[name])
            cell.value = value
            if name == "Notes" and isinstance(value, str):
                # Notes are data, never executable Excel formulas.
                cell.data_type = "s"

    def _backup(self) -> Path | None:
        if not self.backups or not self.path.exists():
            return None
        backup_dir = self.path.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        destination = backup_dir / f"{self.path.stem}-{timestamp}{self.path.suffix}"
        shutil.copy2(self.path, destination)
        return destination

    def _save_atomic(self, workbook) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=f".{self.path.stem}-", suffix=self.path.suffix or ".xlsx",
                dir=self.path.parent, delete=False,
            ) as temporary:
                temporary_name = temporary.name
            workbook.save(temporary_name)
            os.replace(temporary_name, self.path)
        except Exception as exc:
            if temporary_name and os.path.exists(temporary_name):
                os.unlink(temporary_name)
            raise StorageError(f"Could not save workbook {self.path}: {exc}") from exc

    def upsert(self, record: DailyMetrics) -> tuple[DailyMetrics, bool, int, Path | None]:
        """Insert or update a record.

        Returns ``(record, created, cumulative_logged_days, backup_path)``.
        """
        workbook, sheet, columns = self._load()
        temporary_backup = None
        try:
            matching_rows = [
                row for row in range(2, sheet.max_row + 1)
                if self._day_from_row(sheet, row, columns) == record.day
            ]
            created = not matching_rows
            row = matching_rows[-1] if matching_rows else sheet.max_row + 1
            self._write_record(sheet, row, columns, record)
            for duplicate in reversed(matching_rows[:-1]):
                sheet.delete_rows(duplicate, 1)

            # Keep the original cumulative Days column meaningful after backfills.
            dated_rows = []
            for candidate in range(2, sheet.max_row + 1):
                day = self._day_from_row(sheet, candidate, columns)
                if day is not None:
                    dated_rows.append((day, candidate))
            day_numbers = {
                candidate: index
                for index, (_, candidate) in enumerate(sorted(dated_rows), start=1)
            }
            for candidate, number in day_numbers.items():
                sheet.cell(candidate, columns["Days"], number)
            current_row = next(
                candidate for candidate, number in day_numbers.items()
                if sheet.cell(candidate, columns["Date"]).value == record.day.isoformat()
                or self._day_from_row(sheet, candidate, columns) == record.day
            )
            self._style(sheet, len(columns))
            temporary_backup = self._backup()
            self._save_atomic(workbook)
            return record, created, day_numbers[current_row], temporary_backup
        finally:
            workbook.close()
