import csv
import json
from datetime import date

from trackcoder.analytics import build_report
from trackcoder.exporters import export_records
from trackcoder.models import DailyMetrics
from trackcoder.reporting import daily_text, write_html_report
from trackcoder.sheets import sheet_rows, sync_to_google_sheets


def sample_records():
    return [
        DailyMetrics(date(2026, 1, 1), focus_minutes=60, code_time_minutes=45, wpm=None, html=5),
        DailyMetrics(date(2026, 1, 2), focus_minutes=90, code_time_minutes=75, wpm=62.5,
                     javascript=20, notes="<script>alert('private')</script>"),
    ]


def test_csv_and_json_exports_round_trip_schema(tmp_path):
    csv_path = export_records(sample_records(), tmp_path / "metrics.csv")
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["wpm"] == ""
    assert rows[1]["total_lines"] == "20"

    json_path = export_records(sample_records(), tmp_path / "metrics.json")
    payload = json.loads(json_path.read_text())
    assert payload["schema_version"] == 1
    assert payload["records"][0]["wpm"] is None
    assert payload["records"][1]["date"] == "2026-01-02"


def test_html_dashboard_is_self_contained_and_escapes_notes(tmp_path):
    report = build_report(sample_records(), end=date(2026, 1, 7), days=7)
    output = write_html_report(report, tmp_path / "dashboard.html")
    content = output.read_text()
    assert "Daily code time" in content
    assert "Goal" in content
    assert "<script>alert('private')</script>" not in content
    assert "&lt;script&gt;alert(&#x27;private&#x27;)&lt;/script&gt;" in content
    assert "https://" not in content
    assert "cdn" not in content.lower()


def test_daily_text_distinguishes_missing_wpm():
    text = daily_text(sample_records()[0])
    assert "not collected" in text
    assert "0 wpm" not in text


def test_google_sheet_rows_and_dry_run_require_no_credentials(monkeypatch):
    monkeypatch.delenv("GOOGLE_SHEET_ID", raising=False)
    monkeypatch.delenv("GOOGLE_SHEETS_CREDENTIALS_FILE", raising=False)
    rows = sheet_rows(sample_records())
    assert rows[0][0] == "Date"
    assert rows[1][2] == ""
    assert rows[2][9] == "Yes"
    message = sync_to_google_sheets(sample_records(), dry_run=True)
    assert "2 records" in message
