from datetime import date

import openpyxl
import pytest

from trackcoder.errors import StorageError
from trackcoder.models import DailyMetrics
from trackcoder.storage import HEADERS, WorkbookStore


def test_empty_store_does_not_create_file(tmp_path):
    path = tmp_path / "metrics.xlsx"
    store = WorkbookStore(path)
    assert store.all() == []
    assert not path.exists()


def test_upsert_updates_existing_date_and_creates_backup(tmp_path):
    path = tmp_path / "metrics.xlsx"
    store = WorkbookStore(path)
    original = DailyMetrics(date(2026, 1, 1), focus_minutes=30, wpm=50, html=10)
    _, created, days, backup = store.upsert(original)
    assert created is True
    assert days == 1
    assert backup is None

    updated = DailyMetrics(date(2026, 1, 1), focus_minutes=90, wpm=None, css=7)
    _, created, days, backup = store.upsert(updated)
    assert created is False
    assert days == 1
    assert backup is not None and backup.exists()
    assert store.all() == [updated]
    assert len(store.all()) == 1

    workbook = openpyxl.load_workbook(path, data_only=True)
    rows = list(workbook.active.iter_rows(min_row=2, values_only=True))
    assert len(rows) == 1
    assert rows[0][1] == "01:30"
    assert rows[0][2] is None
    assert rows[0][8] == 7
    workbook.close()


def test_notes_are_literal_text_not_excel_formulas(tmp_path):
    path = tmp_path / "metrics.xlsx"
    store = WorkbookStore(path, backups=False)
    store.upsert(DailyMetrics(date(2026, 1, 1), notes="=HYPERLINK(\"https://example.test\")"))
    workbook = openpyxl.load_workbook(path, data_only=False)
    note_cell = workbook.active["K2"]
    assert note_cell.value.startswith("=HYPERLINK")
    assert note_cell.data_type == "s"
    workbook.close()


def test_backfill_recalculates_cumulative_day_numbers(tmp_path):
    path = tmp_path / "metrics.xlsx"
    store = WorkbookStore(path, backups=False)
    store.upsert(DailyMetrics(date(2026, 1, 3), html=3))
    store.upsert(DailyMetrics(date(2026, 1, 1), html=1))
    _, _, days, _ = store.upsert(DailyMetrics(date(2026, 1, 2), html=2))
    assert days == 2

    workbook = openpyxl.load_workbook(path, data_only=True)
    values = {
        row[0]: row[9]
        for row in workbook.active.iter_rows(min_row=2, values_only=True)
    }
    assert values == {"2026-01-03": 3, "2026-01-01": 1, "2026-01-02": 2}
    # Days follows chronological log position, not physical row position.
    assert sorted(values, key=values.get) == ["2026-01-01", "2026-01-02", "2026-01-03"]
    workbook.close()


def test_upsert_consolidates_legacy_duplicate_rows(tmp_path):
    path = tmp_path / "metrics.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(HEADERS)
    sheet.append(["2026-01-01", "00:10", 50, "00:10", "00:05", 1, 0, 0, 1, 1, "old"])
    sheet.append(["2026-01-01", "00:20", 51, "00:20", "00:10", 2, 0, 0, 2, 1, "new"])
    workbook.save(path)
    workbook.close()

    store = WorkbookStore(path, backups=False)
    assert store.get("2026-01-01").notes == "new"
    _, created, days, _ = store.upsert(DailyMetrics(date(2026, 1, 1), focus_minutes=60))
    assert created is False
    assert days == 1
    assert len(store.all()) == 1


def test_corrupt_workbook_is_never_deleted(tmp_path):
    path = tmp_path / "metrics.xlsx"
    path.write_bytes(b"not an excel file")
    with pytest.raises(StorageError, match="left unchanged"):
        WorkbookStore(path).all()
    assert path.read_bytes() == b"not an excel file"


def test_missing_required_columns_are_reported(tmp_path):
    path = tmp_path / "metrics.xlsx"
    workbook = openpyxl.Workbook()
    workbook.active.append(["Date", "Something"])
    workbook.save(path)
    workbook.close()
    with pytest.raises(StorageError, match="missing required columns"):
        WorkbookStore(path).all()
