"""Explicit workbook copy helper retained for older scripts."""

from __future__ import annotations

import shutil
from pathlib import Path

from trackcoder.config import Settings


def copy_past(destination=None):
    source = Settings.from_env().workbook_path
    target = Path(destination or Path.cwd()).expanduser().resolve()
    if target.is_dir():
        target = target / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if source == target:
        return target
    shutil.copy2(source, target)
    return target
