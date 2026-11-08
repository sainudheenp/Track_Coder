"""Environment-driven configuration with portable defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .errors import ConfigurationError, ValidationError
from .timeutils import parse_duration


def _path(name: str, default: Path) -> Path:
    return Path(os.getenv(name, str(default))).expanduser().resolve()


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"{name} must be true/false, yes/no, on/off, or 1/0.")


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a whole number.") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} must be greater than zero.")
    return value


@dataclass(frozen=True, slots=True)
class Goals:
    daily_focus_minutes: int = 120
    weekly_code_time_minutes: int = 600
    weekly_lines: int = 500

    def __post_init__(self) -> None:
        for name in ("daily_focus_minutes", "weekly_code_time_minutes", "weekly_lines"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValidationError(f"{name} must be a positive integer.")


@dataclass(frozen=True, slots=True)
class Settings:
    data_dir: Path
    workbook_path: Path
    trackme_path: Path
    screenshot_dir: Path
    browser_timeout: int = 20
    headless: bool = True
    backups: bool = True
    goals: Goals = Goals()

    @classmethod
    def from_env(cls) -> "Settings":
        home = Path.home()
        data_dir = _path("TRACKCODER_DATA_DIR", home / "TrackCoder")
        workbook = _path("TRACKCODER_WORKBOOK", data_dir / "trackcoder.xlsx")
        trackme = _path(
            "TRACKME_PROGRESS_FILE",
            home / "bin" / "TrackMe" / "daily-progress-tracker.json.b64",
        )
        screenshots = _path("TRACKCODER_SCREENSHOT_DIR", data_dir / "screenshots")
        goals = Goals(
            daily_focus_minutes=parse_duration(
                os.getenv("TRACKCODER_DAILY_FOCUS_GOAL", "02:00"),
                field="TRACKCODER_DAILY_FOCUS_GOAL",
            ),
            weekly_code_time_minutes=parse_duration(
                os.getenv("TRACKCODER_WEEKLY_CODE_GOAL", "10:00"),
                field="TRACKCODER_WEEKLY_CODE_GOAL",
            ),
            weekly_lines=_positive_int("TRACKCODER_WEEKLY_LINES_GOAL", 500),
        )
        return cls(
            data_dir=data_dir,
            workbook_path=workbook,
            trackme_path=trackme,
            screenshot_dir=screenshots,
            browser_timeout=_positive_int("TRACKCODER_BROWSER_TIMEOUT", 20),
            headless=_bool("TRACKCODER_HEADLESS", True),
            backups=_bool("TRACKCODER_BACKUPS", True),
            goals=goals,
        )

    def with_workbook(self, workbook: str | Path | None) -> "Settings":
        if workbook is None:
            return self
        path = Path(workbook).expanduser().resolve()
        return Settings(
            data_dir=path.parent,
            workbook_path=path,
            trackme_path=self.trackme_path,
            screenshot_dir=self.screenshot_dir,
            browser_timeout=self.browser_timeout,
            headless=self.headless,
            backups=self.backups,
            goals=self.goals,
        )
