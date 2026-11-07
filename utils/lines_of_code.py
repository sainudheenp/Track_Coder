"""Backward-compatible TrackMe lines-of-code provider."""

from __future__ import annotations

from trackcoder.config import Settings
from trackcoder.trackme import read_lines


def loc(yesterday: str, file_path=None):
    path = file_path or Settings.from_env().trackme_path
    return read_lines(path, yesterday)
