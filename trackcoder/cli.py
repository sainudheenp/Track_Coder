"""Track Coder command-line interface.

Browser providers are imported only inside the collect command, so local
logging, exports, analytics, and even --help never launch Chrome.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import replace
from datetime import date, timedelta
from typing import Sequence

from . import __version__
from .analytics import build_report
from .config import Goals, Settings
from .errors import CollectionError, TrackCoderError, ValidationError
from .exporters import export_records
from .models import DailyMetrics
from .reporting import daily_text, summary_text, write_html_report
from .storage import WorkbookStore
from .timeutils import parse_date, parse_duration
from .trackme import read_lines

COMMANDS = {"collect", "log", "report", "export", "screenshots", "sync"}


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a whole number") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def _nonnegative_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a whole number") from exc
    if number < 0:
        raise argparse.ArgumentTypeError("cannot be negative")
    return number


def _nonnegative_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if not math.isfinite(number):
        raise argparse.ArgumentTypeError("must be a finite number")
    if number < 0:
        raise argparse.ArgumentTypeError("cannot be negative")
    return number


def _workbook_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--workbook", metavar="PATH",
        help="Excel workbook path (default: TRACKCODER_WORKBOOK or ~/TrackCoder/trackcoder.xlsx)",
    )


def _backup_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--no-backup", action="store_true", help="Skip the pre-write workbook backup")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trackcoder",
        description="Local-first coding metrics, streaks, goals, and reports.",
        epilog="Run 'trackcoder COMMAND --help' for command-specific options.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    collect = commands.add_parser("collect", help="Collect browser and TrackMe metrics, then save them")
    collect.add_argument(
        "-date", "--date", default=(date.today() - timedelta(days=1)).isoformat(),
        help="Date to collect in YYYY-MM-DD format (default: yesterday)",
    )
    collect.add_argument("--focus", help="Override calculated focus time, e.g. 02:30 or 2h 30m")
    collect.add_argument("--non-interactive", action="store_true", help="Never prompt; suitable for cron and CI")
    collect.add_argument("--skip-wpm", action="store_true", help="Do not collect MonkeyType WPM")
    collect.add_argument("--skip-code-time", action="store_true", help="Do not collect Software.com code time")
    collect.add_argument("--skip-loc", action="store_true", help="Do not read local TrackMe line counts")
    collect.add_argument("--strict", action="store_true", help="Do not save if any enabled provider fails")
    collect.add_argument("--dry-run", action="store_true", help="Collect and display without writing the workbook")
    collect.add_argument("--clipboard", action="store_true", help="Copy the final daily summary to the clipboard")
    _workbook_argument(collect)
    _backup_argument(collect)
    collect.set_defaults(handler=_collect)

    log = commands.add_parser("log", help="Create or correct a daily entry without browser automation")
    log.add_argument("--date", default=date.today().isoformat(), help="Entry date (default: today)")
    log.add_argument("--focus", help="Focus duration: HH:MM, 2h 15m, or 135m")
    log.add_argument("--code-time", "--ct", dest="code_time", help="Total code-time duration")
    log.add_argument("--active-code-time", "--act", dest="active_code_time", help="Active code-time duration")
    log.add_argument("--wpm", type=_nonnegative_float, help="Measured typing speed; omit when unknown")
    log.add_argument("--html", type=_nonnegative_int, help="HTML lines changed")
    log.add_argument("--css", type=_nonnegative_int, help="CSS lines changed")
    log.add_argument("--js", "--javascript", dest="javascript", type=_nonnegative_int, help="JavaScript/JSX lines changed")
    log.add_argument("--notes", help="Optional daily note")
    log.add_argument("--replace", action="store_true", help="Reset unspecified fields instead of preserving existing values")
    log.add_argument("--dry-run", action="store_true", help="Validate and preview without saving")
    _workbook_argument(log)
    _backup_argument(log)
    log.set_defaults(handler=_log)

    report = commands.add_parser("report", help="Show trends, streaks, goals, and an optional HTML dashboard")
    report.add_argument("--days", type=_positive_int, default=30, help="Period length in days (default: 30)")
    report.add_argument("--end", default=date.today().isoformat(), help="Period end date (default: today)")
    report.add_argument("--html", nargs="?", const="", metavar="PATH", help="Write a self-contained dashboard; PATH is optional")
    report.add_argument("--daily-focus-goal", help="Override daily focus target, e.g. 02:00")
    report.add_argument("--weekly-code-goal", help="Override weekly code-time target, e.g. 10:00")
    report.add_argument("--weekly-lines-goal", type=_nonnegative_int, help="Override weekly lines target")
    _workbook_argument(report)
    report.set_defaults(handler=_report)

    export = commands.add_parser("export", help="Export workbook records to CSV or JSON")
    export.add_argument("--output", required=True, help="Destination .csv or .json file")
    export.add_argument("--format", choices=("csv", "json"), help="Format (normally inferred from output extension)")
    export.add_argument("--days", type=_positive_int, help="Only export the most recent N days")
    export.add_argument("--end", default=date.today().isoformat(), help="End date used with --days")
    _workbook_argument(export)
    export.set_defaults(handler=_export)

    screenshots = commands.add_parser("screenshots", help="Capture weekly Software.com graphs (legacy workflow)")
    screenshots.add_argument("start_date", help="First date in YYYY-MM-DD format")
    screenshots.add_argument("end_date", help="Last date in YYYY-MM-DD format")
    screenshots.set_defaults(handler=_screenshots)

    sync = commands.add_parser("sync", help="Synchronize local records to an external destination")
    destinations = sync.add_subparsers(dest="destination", required=True)
    sheets = destinations.add_parser("sheets", help="Replace a dedicated Google Sheets worksheet in one batch")
    sheets.add_argument("--spreadsheet-id", help="Google spreadsheet ID (or GOOGLE_SHEET_ID)")
    sheets.add_argument("--credentials-file", help="Service-account JSON (or GOOGLE_SHEETS_CREDENTIALS_FILE)")
    sheets.add_argument("--worksheet", help="Worksheet name (default: Track Coder)")
    sheets.add_argument("--dry-run", action="store_true", help="Validate and count rows without contacting Google")
    _workbook_argument(sheets)
    sheets.set_defaults(handler=_sync_sheets)
    return parser


def _settings(args: argparse.Namespace) -> Settings:
    return Settings.from_env().with_workbook(getattr(args, "workbook", None))


def _store(args: argparse.Namespace, settings: Settings) -> WorkbookStore:
    backups = settings.backups and not getattr(args, "no_backup", False)
    return WorkbookStore(settings.workbook_path, backups=backups)


def _print_save(record: DailyMetrics, created: bool, days: int, store: WorkbookStore, backup) -> None:
    action = "Created" if created else "Updated"
    print(f"✓ {action} {record.day.isoformat()} · logged day #{days}")
    print(daily_text(record))
    print(f"\nWorkbook: {store.path}")
    if backup:
        print(f"Backup:   {backup}")


def _log(args: argparse.Namespace) -> int:
    settings = _settings(args)
    store = _store(args, settings)
    day = parse_date(args.date)
    fields = ("focus", "code_time", "active_code_time", "wpm", "html", "css", "javascript", "notes")
    if not any(getattr(args, name) is not None for name in fields):
        raise ValidationError("Provide at least one metric or --notes. Use 'trackcoder log --help' for examples.")
    existing = None if args.replace else store.get(day)
    base = existing or DailyMetrics(day)

    def duration(argument: str | None, current: int, name: str) -> int:
        return current if argument is None else parse_duration(argument, field=name)

    record = DailyMetrics(
        day=day,
        focus_minutes=duration(args.focus, base.focus_minutes, "focus"),
        wpm=base.wpm if args.wpm is None else args.wpm,
        code_time_minutes=duration(args.code_time, base.code_time_minutes, "code time"),
        active_code_time_minutes=duration(args.active_code_time, base.active_code_time_minutes, "active code time"),
        html=base.html if args.html is None else args.html,
        css=base.css if args.css is None else args.css,
        javascript=base.javascript if args.javascript is None else args.javascript,
        notes=base.notes if args.notes is None else args.notes,
    )
    if args.dry_run:
        print("Dry run — workbook not changed.\n")
        print(daily_text(record))
        return 0
    saved, created, days, backup = store.upsert(record)
    _print_save(saved, created, days, store, backup)
    return 0


def _collect(args: argparse.Namespace) -> int:
    settings = _settings(args)
    store = _store(args, settings)
    day = parse_date(args.date)
    if args.skip_wpm and args.skip_code_time and args.skip_loc:
        raise ValidationError("All providers are disabled; enable at least one provider or use 'trackcoder log'.")
    focus_override = parse_duration(args.focus, field="focus") if args.focus else None
    base = store.get(day) or DailyMetrics(day)
    values = {
        "wpm": base.wpm,
        "focus_minutes": base.focus_minutes,
        "code_time_minutes": base.code_time_minutes,
        "active_code_time_minutes": base.active_code_time_minutes,
        "html": base.html,
        "css": base.css,
        "javascript": base.javascript,
    }
    errors: list[str] = []
    successes = 0

    if not args.skip_wpm:
        try:
            from utils.typing_wpm import get_wpm
            wpm = get_wpm(timeout=settings.browser_timeout, headless=settings.headless)
            if wpm is None or float(wpm) < 0:
                raise CollectionError("MonkeyType returned no valid WPM measurement.")
            values["wpm"] = float(wpm)
            successes += 1
            print(f"✓ MonkeyType: {values['wpm']:.0f} WPM")
        except Exception as exc:
            errors.append(f"MonkeyType: {exc}")
            print(f"⚠ MonkeyType failed: {exc}", file=sys.stderr)

    if not args.skip_code_time:
        try:
            from utils.code_time import get_code_time
            focus, active, code = get_code_time(
                day.isoformat(), focus_override=focus_override,
                interactive=not args.non_interactive, timeout=settings.browser_timeout,
                headless=settings.headless,
            )
            values["focus_minutes"] = parse_duration(focus, field="collected focus")
            values["active_code_time_minutes"] = parse_duration(active, field="collected ACT")
            values["code_time_minutes"] = parse_duration(code, field="collected CT")
            successes += 1
            print(f"✓ Software.com: CT {code}, ACT {active}, focus {focus}")
        except Exception as exc:
            errors.append(f"Software.com: {exc}")
            print(f"⚠ Software.com failed: {exc}", file=sys.stderr)

    if not args.skip_loc:
        try:
            html, css, javascript, _ = read_lines(settings.trackme_path, day)
            values.update(html=html, css=css, javascript=javascript)
            successes += 1
            print(f"✓ TrackMe: {html + css + javascript:,} lines")
        except Exception as exc:
            errors.append(f"TrackMe: {exc}")
            print(f"⚠ TrackMe failed: {exc}", file=sys.stderr)

    if not successes:
        raise CollectionError("No provider succeeded; workbook was not changed. " + " | ".join(errors))
    if errors and args.strict:
        raise CollectionError("Strict collection aborted without saving. " + " | ".join(errors))

    record = DailyMetrics(day=day, notes=base.notes, **values)
    if args.dry_run:
        print("\nDry run — workbook not changed.\n")
        print(daily_text(record))
    else:
        saved, created, days, backup = store.upsert(record)
        print()
        _print_save(saved, created, days, store, backup)

    if args.clipboard and not args.dry_run:
        try:
            import pyperclip
            pyperclip.copy(daily_text(record))
            print("✓ Daily summary copied to clipboard.")
        except Exception as exc:
            print(f"⚠ Clipboard unavailable: {exc}", file=sys.stderr)

    if errors:
        print("\nCompleted partially. Existing values were preserved for failed providers.", file=sys.stderr)
        return 2
    return 0


def _goals(args: argparse.Namespace, settings: Settings) -> Goals:
    goals = settings.goals
    if args.daily_focus_goal is not None:
        goals = replace(goals, daily_focus_minutes=parse_duration(args.daily_focus_goal, field="daily focus goal"))
    if args.weekly_code_goal is not None:
        goals = replace(goals, weekly_code_time_minutes=parse_duration(args.weekly_code_goal, field="weekly code goal"))
    if args.weekly_lines_goal is not None:
        goals = replace(goals, weekly_lines=args.weekly_lines_goal)
    return goals


def _report(args: argparse.Namespace) -> int:
    settings = _settings(args)
    records = _store(args, settings).all()
    report = build_report(
        records, end=parse_date(args.end, field="end date"), days=args.days, goals=_goals(args, settings),
    )
    print(summary_text(report))
    if args.html is not None:
        destination = args.html or settings.data_dir / "dashboard.html"
        path = write_html_report(report, destination)
        print(f"HTML dashboard: {path}")
    return 0


def _export(args: argparse.Namespace) -> int:
    settings = _settings(args)
    records = _store(args, settings).all()
    if args.days is not None:
        end = parse_date(args.end, field="end date")
        start = end - timedelta(days=args.days - 1)
        records = [record for record in records if start <= record.day <= end]
    path = export_records(records, args.output, file_format=args.format)
    print(f"✓ Exported {len(records)} records to {path}")
    return 0


def _screenshots(args: argparse.Namespace) -> int:
    start = parse_date(args.start_date, field="start date")
    end = parse_date(args.end_date, field="end date")
    if start > end:
        raise ValidationError("start date cannot be after end date.")
    settings = Settings.from_env()
    from utils.screenshot_xl import screenshot_xl
    screenshot_xl(
        start.isoformat(), end.isoformat(), output_dir=settings.screenshot_dir,
        timeout=settings.browser_timeout, headless=settings.headless,
    )
    return 0


def _sync_sheets(args: argparse.Namespace) -> int:
    settings = _settings(args)
    records = _store(args, settings).all()
    from .sheets import sync_to_google_sheets
    message = sync_to_google_sheets(
        records, spreadsheet_id=args.spreadsheet_id, credentials_file=args.credentials_file,
        worksheet_name=args.worksheet, dry_run=args.dry_run,
    )
    print(f"✓ {message}")
    return 0


def normalize_argv(argv: Sequence[str]) -> list[str]:
    """Keep the repository's original ``-date`` and ``-scrxl`` calls working."""
    arguments = list(argv)
    if arguments and arguments[0] == "-scrxl":
        return ["screenshots", *arguments[1:]]
    if not arguments:
        return ["collect"]
    if arguments[0] not in COMMANDS and arguments[0] not in {"-h", "--help", "--version"}:
        return ["collect", *arguments]
    return arguments


def main(argv: Sequence[str] | None = None) -> int:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    parser = build_parser()
    args = parser.parse_args(normalize_argv(sys.argv[1:] if argv is None else argv))
    try:
        return args.handler(args)
    except TrackCoderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"File/system error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled; no further actions were taken.", file=sys.stderr)
        return 130


def entrypoint() -> None:
    raise SystemExit(main())
