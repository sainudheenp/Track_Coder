"""Decoder for the TrackMe VS Code extension's local progress file."""

from __future__ import annotations

import base64
import binascii
import json
import math
from datetime import date
from pathlib import Path
from typing import Any

from .errors import CollectionError
from .timeutils import parse_date


def decode_trackme(content: str | bytes) -> dict[str, Any]:
    try:
        decoded = base64.b64decode(content, validate=True).decode("utf-8")
        payload = json.loads(decoded)
    except (ValueError, UnicodeError, binascii.Error, json.JSONDecodeError) as exc:
        raise CollectionError(f"TrackMe progress data is not valid base64-encoded JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise CollectionError("TrackMe progress data must contain a JSON object.")
    return payload


def lines_for_day(payload: dict[str, Any], day: str | date) -> tuple[int, int, int, int]:
    target = parse_date(day).strftime("%m/%d/%Y")
    entry = payload.get(target, {})
    if not isinstance(entry, dict):
        raise CollectionError(f"TrackMe entry for {target} must be an object.")
    lines = entry.get("lines_of_code", {})
    if not isinstance(lines, dict):
        raise CollectionError(f"TrackMe lines_of_code for {target} must be an object.")

    def count(*names: str) -> int:
        total = 0
        for name in names:
            value = lines.get(name, 0)
            if (
                isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0
            ):
                raise CollectionError(f"TrackMe {name} line count for {target} must be finite and non-negative.")
            total += int(value)
        return total

    html = count("html")
    css = count("css")
    javascript = count("javascript", "javascriptreact")
    return html, css, javascript, html + css + javascript


def read_lines(path: str | Path, day: str | date) -> tuple[int, int, int, int]:
    source = Path(path).expanduser()
    if not source.is_file():
        raise CollectionError(
            f"TrackMe progress file not found at {source}. Set TRACKME_PROGRESS_FILE or use --skip-loc."
        )
    try:
        content = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise CollectionError(f"Could not read TrackMe progress file {source}: {exc}") from exc
    return lines_for_day(decode_trackme(content), day)
