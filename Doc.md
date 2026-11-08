# Track Coder technical guide

The user-facing installation, command, Docker, scheduling, and Google Sheets guides live in [README.md](README.md). The execution diagram and reliability rules live in [flowchart.md](flowchart.md).

## Data model

`DailyMetrics` is the single normalized representation used by storage, analytics, and exports. Dates are Python `date` objects; durations are non-negative integer minutes; missing WPM is `None`; JavaScript includes JSX. `total_lines` and `is_active` are derived rather than trusted from stale workbook totals.

Excel remains the source of truth. Its original ten columns are supported, with an optional `Notes` column. `WorkbookStore` deduplicates by date on reads (last row wins), updates existing dates, and consolidates duplicate rows when that date is written. All writes go through a temporary file in the destination directory followed by `os.replace`.

## Analytics definitions

- **Active day:** non-zero focus, CT, ACT, or changed lines. WPM alone is insufficient.
- **Current streak:** consecutive active days ending on the report date, with one grace day.
- **Best streak:** longest consecutive active-day sequence across all available records.
- **Previous period:** an equally sized period immediately before the selected period.
- **Average WPM:** unweighted mean of records with a real WPM observation.
- **Goal targets:** daily focus is multiplied by elapsed days; weekly CT/lines targets are multiplied by elapsed days / 7.

The HTML dashboard is generated locally with escaped text and inline CSS/SVG. It includes no analytics scripts, external fonts, CDNs, or runtime dependencies.

## Provider boundaries

Selenium code remains under `utils/` and is imported lazily by `collect`/`screenshots`. Pure parsing logic is under `trackcoder/software.py` and `trackcoder/trackme.py`, so it can be tested without network or browser access.

Collection is provider-independent. Successful sources update their fields; failed sources preserve existing values. `--strict` changes this to all-or-nothing. Utilities raise domain exceptions instead of calling `sys.exit`, leaving exit policy to the CLI.

## Integration safety

Google Sheets sync is opt-in and requires a service account. It targets one dedicated worksheet and sends a single batch. CSV and JSON exports are atomic. Credentials and generated metrics are ignored by Git and Docker build context.

## Verification

```bash
python -m pytest
python -m compileall -q trackcoder utils main.py
python main.py --help
```

Tests use temporary workbooks and mocked providers; they never require personal credentials, modify `~/TrackCoder`, or contact external services.
