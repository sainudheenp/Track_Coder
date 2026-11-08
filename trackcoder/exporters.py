"""Portable JSON and CSV exports with stable, documented schemas."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable

from .errors import ValidationError
from .models import DailyMetrics

CSV_FIELDS = [
    "date", "focus", "wpm", "code_time", "active_code_time",
    "html", "css", "javascript", "total_lines", "notes",
]


def export_records(
    records: Iterable[DailyMetrics], destination: str | Path, *, file_format: str | None = None,
) -> Path:
    path = Path(destination).expanduser().resolve()
    selected_format = (file_format or path.suffix.lstrip(".")).lower()
    if selected_format not in {"csv", "json"}:
        raise ValidationError("Export format must be csv or json (or use a .csv/.json filename).")
    rows = sorted(records, key=lambda record: record.day)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", prefix=f".{path.name}-",
            dir=path.parent, delete=False,
        ) as temporary:
            temporary_name = temporary.name
            if selected_format == "csv":
                writer = csv.DictWriter(temporary, fieldnames=CSV_FIELDS)
                writer.writeheader()
                writer.writerows(record.as_csv_row() for record in rows)
            else:
                payload = {
                    "schema_version": 1,
                    "records": [record.as_dict() for record in rows],
                }
                json.dump(payload, temporary, indent=2, ensure_ascii=False)
                temporary.write("\n")
        os.replace(temporary_name, path)
    except Exception:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)
        raise
    return path
