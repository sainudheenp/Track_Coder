from datetime import date

import pytest

from trackcoder.cli import main, normalize_argv
from trackcoder.models import DailyMetrics
from trackcoder.storage import WorkbookStore


def test_manual_log_update_preserves_unspecified_fields(tmp_path, capsys):
    workbook = tmp_path / "metrics.xlsx"
    assert main([
        "log", "--date", "2026-01-02", "--focus", "1h 30m", "--ct", "01:10",
        "--act", "45m", "--wpm", "58", "--html", "12", "--js", "8",
        "--workbook", str(workbook), "--no-backup",
    ]) == 0
    assert main([
        "log", "--date", "2026-01-02", "--css", "4", "--notes", "deep work",
        "--workbook", str(workbook), "--no-backup",
    ]) == 0

    records = WorkbookStore(workbook, backups=False).all()
    assert len(records) == 1
    record = records[0]
    assert record.focus_minutes == 90
    assert record.code_time_minutes == 70
    assert record.active_code_time_minutes == 45
    assert record.wpm == 58
    assert (record.html, record.css, record.javascript) == (12, 4, 8)
    assert record.notes == "deep work"
    assert "Updated 2026-01-02" in capsys.readouterr().out


def test_dry_run_does_not_create_workbook(tmp_path, capsys):
    workbook = tmp_path / "metrics.xlsx"
    result = main([
        "log", "--date", "2026-01-02", "--focus", "20m", "--dry-run",
        "--workbook", str(workbook),
    ])
    assert result == 0
    assert not workbook.exists()
    assert "workbook not changed" in capsys.readouterr().out


def test_report_and_export_work_without_browser(tmp_path, capsys):
    workbook = tmp_path / "metrics.xlsx"
    store = WorkbookStore(workbook, backups=False)
    store.upsert(DailyMetrics(date(2026, 1, 2), code_time_minutes=60, html=10))
    dashboard = tmp_path / "report.html"
    exported = tmp_path / "report.json"
    assert main([
        "report", "--end", "2026-01-02", "--days", "2", "--html", str(dashboard),
        "--workbook", str(workbook),
    ]) == 0
    assert dashboard.exists()
    assert main([
        "export", "--output", str(exported), "--days", "2", "--end", "2026-01-02",
        "--workbook", str(workbook),
    ]) == 0
    assert exported.exists()
    assert "TRACK CODER" in capsys.readouterr().out


def test_help_and_legacy_argument_normalization_do_not_launch_chrome(capsys):
    assert normalize_argv([]) == ["collect"]
    assert normalize_argv(["-date", "2026-01-01"]) == ["collect", "-date", "2026-01-01"]
    assert normalize_argv(["-scrxl", "2026-01-01", "2026-01-07"]) == [
        "screenshots", "2026-01-01", "2026-01-07"
    ]
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert "2.0.0" in capsys.readouterr().out


def test_disabled_collection_fails_cleanly_without_browser(tmp_path, capsys):
    result = main([
        "collect", "--skip-wpm", "--skip-code-time", "--skip-loc",
        "--workbook", str(tmp_path / "metrics.xlsx"),
    ])
    assert result == 1
    assert "All providers are disabled" in capsys.readouterr().err


def test_sheets_dry_run_needs_no_google_configuration(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("GOOGLE_SHEET_ID", raising=False)
    monkeypatch.delenv("GOOGLE_SHEETS_CREDENTIALS_FILE", raising=False)
    workbook = tmp_path / "metrics.xlsx"
    WorkbookStore(workbook, backups=False).upsert(DailyMetrics(date(2026, 1, 2), html=2))
    assert main([
        "sync", "sheets", "--dry-run", "--workbook", str(workbook)
    ]) == 0
    assert "1 records" in capsys.readouterr().out
