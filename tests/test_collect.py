from datetime import date

from trackcoder.cli import main
from trackcoder.models import DailyMetrics
from trackcoder.storage import WorkbookStore


def test_partial_collection_preserves_failed_provider_values(tmp_path, monkeypatch, capsys):
    workbook = tmp_path / "metrics.xlsx"
    original = DailyMetrics(
        date(2026, 1, 2), focus_minutes=50, code_time_minutes=40,
        active_code_time_minutes=25, wpm=40, notes="keep me",
    )
    WorkbookStore(workbook, backups=False).upsert(original)

    import utils.code_time
    import utils.typing_wpm
    monkeypatch.setattr(utils.typing_wpm, "get_wpm", lambda **kwargs: 65)
    monkeypatch.setattr(
        utils.code_time, "get_code_time",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("site unavailable")),
    )
    monkeypatch.setattr("trackcoder.cli.read_lines", lambda path, day: (3, 2, 5, 10))

    result = main([
        "collect", "--date", "2026-01-02", "--non-interactive",
        "--workbook", str(workbook), "--no-backup",
    ])
    assert result == 2
    record = WorkbookStore(workbook, backups=False).get("2026-01-02")
    assert record.wpm == 65
    assert (record.html, record.css, record.javascript) == (3, 2, 5)
    assert record.focus_minutes == 50
    assert record.code_time_minutes == 40
    assert record.active_code_time_minutes == 25
    assert record.notes == "keep me"
    assert "Completed partially" in capsys.readouterr().err


def test_strict_collection_does_not_save_partial_data(tmp_path, monkeypatch):
    workbook = tmp_path / "metrics.xlsx"
    import utils.code_time
    import utils.typing_wpm
    monkeypatch.setattr(utils.typing_wpm, "get_wpm", lambda **kwargs: 65)
    monkeypatch.setattr(
        utils.code_time, "get_code_time",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("site unavailable")),
    )
    result = main([
        "collect", "--date", "2026-01-02", "--skip-loc", "--strict",
        "--non-interactive", "--workbook", str(workbook),
    ])
    assert result == 1
    assert not workbook.exists()


def test_successful_collection_can_be_dry_run(tmp_path, monkeypatch, capsys):
    workbook = tmp_path / "metrics.xlsx"
    import utils.code_time
    import utils.typing_wpm
    monkeypatch.setattr(utils.typing_wpm, "get_wpm", lambda **kwargs: 55)
    monkeypatch.setattr(
        utils.code_time, "get_code_time", lambda *args, **kwargs: ("02:00", "00:45", "01:30"),
    )
    monkeypatch.setattr("trackcoder.cli.read_lines", lambda path, day: (1, 2, 3, 6))
    result = main([
        "collect", "--date", "2026-01-02", "--non-interactive", "--dry-run",
        "--workbook", str(workbook),
    ])
    assert result == 0
    assert not workbook.exists()
    assert "workbook not changed" in capsys.readouterr().out
