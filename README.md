# Track Coder

**Local-first coding analytics for people who already have enough dashboards.**

Track Coder collects typing speed, Software.com code time, and TrackMe line counts into Excel. It now also works completely offline: log or correct a day, measure real streaks, compare periods, track goals, export your data, and generate a self-contained HTML report.

## What’s new

- **Offline daily logging** with patch-style updates and dry runs.
- **Useful analytics:** active-day consistency, current/best streaks, previous-period trends, language share, and configurable goals.
- **Portable reports:** responsive HTML dashboard plus CSV and JSON exports.
- **Google Sheets sync** using a service account and one batch update (addresses [#12](https://github.com/sainudheenp/Track_Coder/issues/12)).
- **Production-ready container:** non-root user, Chromium, persistent volume, health check, and Compose configuration (addresses [#2](https://github.com/sainudheenp/Track_Coder/issues/2)).
- **Safer automation:** no browser launch on import, explicit waits, headless mode, independent provider failures, non-interactive scheduling, and useful exit codes.
- **Safe storage:** atomic writes, pre-write backups, strict validation, duplicate-date correction, and no automatic deletion of damaged workbooks.
- **Honest data:** missing WPM remains missing instead of becoming a fabricated fallback value.

## Requirements

- Python **3.10+**
- Chrome or Chromium only for `collect` and `screenshots`
- Optional: [TrackMe](https://marketplace.visualstudio.com/) VS Code extension for local line counts
- Optional: MonkeyType and Software.com accounts for their respective providers

Manual logging, analytics, exports, and Google Sheets sync do **not** require Chrome or those accounts.

## Install

```bash
git clone https://github.com/sainudheenp/Track_Coder.git
cd Track_Coder
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -e .
cp .env.example .env                  # then edit credentials/paths as needed
```

For development or Google Sheets:

```bash
pip install -e ".[dev]"
pip install -e ".[sheets]"
```

The traditional `pip install -r requirements.txt` workflow is still supported.

## Quick start

```bash
# Add an entry without launching a browser
trackcoder log --date 2026-11-07 --focus 1h30m --ct 55m --act 40m \
  --wpm 62 --html 20 --css 8 --js 45 --notes "Shipped the new report"

# Correct only CSS; every other value is preserved
trackcoder log --date 2026-11-07 --css 12

# Print a 30-day review and create an offline dashboard
trackcoder report --days 30 --html

# Export everything
trackcoder export --output exports/metrics.csv
trackcoder export --output exports/metrics.json

# Run the original automated collection for yesterday
trackcoder collect --non-interactive
```

`python main.py …` is equivalent to `trackcoder …`. The legacy forms still work:

```bash
python main.py -date 2026-11-06
python main.py -scrxl 2026-10-01 2026-10-31
```

Running `python main.py` with no arguments still collects yesterday’s metrics.

## Commands

### `log` — manual entry and corrections

Durations accept `HH:MM`, `HH:MM:SS`, `2h 15m`, `135m`, or a number of minutes.

```bash
trackcoder log --focus 02:00 --ct 01:20 --act 00:50 --js 80
trackcoder log --date 2026-11-01 --focus 45m --dry-run
trackcoder log --date 2026-11-01 --replace --focus 0 --ct 0 --act 0
```

By default, unspecified fields preserve the existing entry. `--replace` resets unspecified fields. `--dry-run` validates and previews without writing.

### `collect` — automated providers

```bash
trackcoder collect --date 2026-11-06 --non-interactive
trackcoder collect --skip-wpm --focus 01:45
trackcoder collect --strict --dry-run
trackcoder collect --clipboard
```

Providers run independently. If one fails, successful values are saved and existing values for the failed provider are preserved; the command exits with status **2**. `--strict` instead aborts without saving when any enabled provider fails. If every provider fails, the workbook is never changed.

The project’s original definitions are retained: total CT is active code time plus non-active code time, and calculated focus adds one hour to non-zero CT. Use `--focus` or `log --focus` when you have an observed focus duration.

### `report` — trends, streaks, and goals

```bash
trackcoder report --days 7
trackcoder report --end 2026-10-31 --days 30 --html reports/october.html
trackcoder report --daily-focus-goal 02:30 --weekly-code-goal 12h \
  --weekly-lines-goal 800
```

Goals are prorated to the selected period. A coding day requires code/focus time or changed lines; WPM alone does not create a streak. Current streaks allow one grace day for an unfinished day. Average WPM is the mean of days that have an actual measurement.

The HTML report has inline CSS/SVG, no external scripts or CDNs, and print/mobile layouts. Your data is not sent anywhere by report generation.

### `export` — CSV or JSON

```bash
trackcoder export --output metrics.csv
trackcoder export --output november.json --days 30 --end 2026-11-30
```

CSV uses readable durations. JSON has a versioned schema and explicit `*_minutes` fields for reliable automation.

### `screenshots` — weekly capture

```bash
trackcoder screenshots 2026-10-01 2026-10-31
```

Existing weeks are skipped, making reruns resumable. Failed weeks are reported but never inserted as the string `Error` into numeric cells.

## Configuration

Everything has a working default; credentials are needed only by their provider.

| Variable | Default | Purpose |
|---|---|---|
| `TRACKCODER_DATA_DIR` | `~/TrackCoder` | Reports and default data directory |
| `TRACKCODER_WORKBOOK` | `~/TrackCoder/trackcoder.xlsx` | Main Excel workbook |
| `TRACKME_PROGRESS_FILE` | `~/bin/TrackMe/daily-progress-tracker.json.b64` | TrackMe source |
| `TRACKCODER_SCREENSHOT_DIR` | `~/TrackCoder/screenshots` | Screenshots |
| `TRACKCODER_BACKUPS` | `true` | Backup before every workbook write |
| `TRACKCODER_HEADLESS` | `true` | Headless Chrome |
| `TRACKCODER_BROWSER_TIMEOUT` | `20` | Provider wait/page-load timeout in seconds |
| `CHROME_BINARY` | auto-detected | Optional browser executable |
| `CHROME_DRIVER_PATH` | Selenium Manager | Optional ChromeDriver executable |
| `TRACKCODER_DAILY_FOCUS_GOAL` | `02:00` | Daily focus target |
| `TRACKCODER_WEEKLY_CODE_GOAL` | `10:00` | Weekly CT target |
| `TRACKCODER_WEEKLY_LINES_GOAL` | `500` | Weekly changed-lines target |

See [.env.example](.env.example) for provider credentials and integration settings. Never commit `.env` or service-account JSON files.

Each write saves atomically with `os.replace`. Existing workbooks are copied to `backups/` first. Re-running an entry for the same date updates it rather than adding a duplicate. The original `Date, Focus, Wpm, CT, ACT, HTML, CSS, JS, Total, Days` columns remain compatible; `Notes` is added when written.

## Google Sheets sync

> Sync **replaces the contents of the dedicated worksheet**. Use a separate worksheet named `Track Coder`, not a sheet containing unrelated data.

1. In Google Cloud, enable the **Google Sheets API** and **Google Drive API**.
2. Create a service account and download its JSON key.
3. Share your spreadsheet with the service account’s `client_email` as an **Editor**.
4. Install the optional dependencies and configure:

```bash
pip install -e ".[sheets]"
export GOOGLE_SHEET_ID="the_id_from_the_spreadsheet_url"
export GOOGLE_SHEETS_CREDENTIALS_FILE="$HOME/TrackCoder/service-account.json"
export GOOGLE_SHEETS_WORKSHEET="Track Coder"

trackcoder sync sheets --dry-run
trackcoder sync sheets
```

Rows are sorted by date and sent in one batch to avoid row-by-row API quota usage. The worksheet is created if necessary and its header is frozen.

## Docker and Compose

The image includes Chromium/ChromeDriver, runs as UID `10001`, and stores data in `/data`.

```bash
docker build -t track-coder .

# Offline logging works with no credentials
docker run --rm -v trackcoder-data:/data track-coder \
  log --date 2026-11-07 --focus 1h --ct 45m --js 30

# Reports use the same persistent volume
docker run --rm -v trackcoder-data:/data track-coder report --days 30

# Automated collection (credentials come from .env)
docker compose run --rm trackcoder collect --non-interactive
```

To use TrackMe in a container, mount its data directory read-only at `/trackme`. For Google Sheets, mount the key read-only and set `GOOGLE_SHEETS_CREDENTIALS_FILE` to its **container** path, for example `/secrets/google.json`.

## Scheduled collection

Cron example for Linux/macOS:

```cron
10 1 * * * cd /path/to/Track_Coder && .venv/bin/trackcoder collect --non-interactive >> "$HOME/TrackCoder/cron.log" 2>&1
```

Exit codes: **0** success, **1** validation/provider/configuration failure with no successful collection, **2** partial collection, **130** interrupted. Use one scheduled writer at a time to avoid concurrent workbook updates.

## Development

```bash
make install
make test       # deterministic tests; no real browser or Google calls
make check
```

The test suite covers duration/date parsing, TrackMe decoding, Software.com labels, Excel upsert/backfill/backups, partial collection, streaks/trends/goals, CLI workflows, exports, HTML escaping, and Sheets payloads. Run `make check` locally on Python 3.10–3.12.

Project structure:

```text
trackcoder/
  analytics.py    # periods, trends, streaks, goals, insights
  cli.py          # commands and backward-compatible arguments
  config.py       # environment-driven paths/browser/goals
  models.py       # validated daily record
  storage.py      # atomic Excel repository
  reporting.py    # terminal and standalone HTML reports
  exporters.py    # CSV / JSON
  sheets.py       # optional Google Sheets destination
  trackme.py      # local TrackMe decoder
utils/            # Selenium providers and legacy compatibility wrappers
```

## Troubleshooting

- **A provider fails:** use its `--skip-*` option, correct its credentials, or use `log`. Other providers can still succeed.
- **Chrome cannot start:** install Chrome/Chromium, set `CHROME_BINARY`/`CHROME_DRIVER_PATH`, or use offline commands.
- **TrackMe is missing:** set `TRACKME_PROGRESS_FILE` or use `--skip-loc`.
- **Workbook is damaged:** Track Coder leaves it untouched and reports the path. Restore a copy from `backups/` after inspecting it.
- **Clipboard is unavailable:** clipboard copying is opt-in with `--clipboard`; failure does not undo saved metrics.

## License

MIT — see [LICENSE](LICENSE).
