"""Weekly Software.com screenshots with resumable, validated Excel output."""

from __future__ import annotations

import os
import tempfile
from datetime import timedelta
from pathlib import Path

import openpyxl
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from trackcoder.config import Settings
from trackcoder.errors import (
    CollectionError,
    ConfigurationError,
    StorageError,
    ValidationError,
)
from trackcoder.software import calculate_software_metrics, minutes_from_aria
from trackcoder.timeutils import format_duration, parse_date

from .get_driver import get_driver

WEEKLY_HEADERS = ["Week Start", "Week", "Code Time (CT)", "Active Code Time (ACT)", "Screenshot Path"]


def _save(workbook, path: Path) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{path.stem}-", suffix=path.suffix, dir=path.parent, delete=False,
        ) as handle:
            temporary = handle.name
        workbook.save(temporary)
        os.replace(temporary, path)
    except Exception as exc:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
        raise StorageError(f"Could not save weekly workbook {path}: {exc}") from exc


def screenshot_xl(
    startDate: str, endDate: str, *, output_dir: str | Path | None = None,
    timeout: int = 20, headless: bool | None = None,
) -> int:
    """Capture each Monday-Sunday week intersecting an inclusive date range.

    Existing week rows are skipped. Failures are reported without writing the
    string ``Error`` into numeric columns, and corrupt workbooks are preserved.
    Returns the number of newly processed weeks.
    """
    start = parse_date(startDate, field="start date")
    end = parse_date(endDate, field="end date")
    if start > end:
        raise ValidationError("start date cannot be after end date.")
    settings = Settings.from_env()
    root = Path(output_dir).expanduser() if output_dir else settings.screenshot_dir
    screenshot_dir = root / "weekly"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    workbook_path = root.parent / "weekly_screenshots_data.xlsx"

    email = os.getenv("userEmail_code_time")
    password = os.getenv("password_code_time")
    if not email or not password:
        raise ConfigurationError(
            "Software.com credentials are required for screenshots; set "
            "userEmail_code_time and password_code_time."
        )

    try:
        if workbook_path.exists():
            workbook = openpyxl.load_workbook(workbook_path)
            sheet = workbook.active
            if sheet.cell(1, 1).value not in {"Date", "Week Start"}:
                raise StorageError(
                    f"Weekly workbook {workbook_path} has an unrecognized header; it was not changed."
                )
            sheet.cell(1, 1, "Week Start")
        else:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Weekly Metrics"
            sheet.append(WEEKLY_HEADERS)
    except StorageError:
        raise
    except Exception as exc:
        raise StorageError(f"Cannot open weekly workbook {workbook_path}: {exc}") from exc

    sheet.freeze_panes = "A2"
    sheet.column_dimensions["A"].width = 15
    sheet.column_dimensions["B"].width = 20
    sheet.column_dimensions["E"].width = 60
    existing = set()
    for row in range(2, sheet.max_row + 1):
        value = sheet.cell(row, 1).value
        if value:
            existing.add(parse_date(value, field=f"week start at row {row}"))

    driver = None
    processed = 0
    skipped = 0
    failures: list[str] = []
    try:
        driver = get_driver(headless=headless, timeout=timeout)
        wait = WebDriverWait(driver, timeout)
        week_start = start - timedelta(days=start.weekday())
        while week_start <= end:
            if week_start in existing:
                skipped += 1
                week_start += timedelta(days=7)
                continue
            print(f"Processing week of {week_start.isoformat()}…")
            try:
                driver.get(f"https://app.software.com/code_time?week_of={week_start.isoformat()}")
                wait.until(lambda current: (
                    current.find_elements(By.NAME, "email")
                    or current.find_elements(By.CLASS_NAME, "highcharts-background")
                ))
                if driver.find_elements(By.NAME, "email"):
                    driver.find_element(By.ID, "email").send_keys(email)
                    driver.find_element(By.ID, "password").send_keys(password)
                    driver.find_element(By.CLASS_NAME, "btn-primary").click()
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-background")))

                active_total = 0
                code_total = 0
                for day_abbr in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"):
                    active_xpath = (
                        f'//*[contains(@aria-label, "{day_abbr},") and '
                        'contains(@aria-label, "Active Code Time")]'
                    )
                    code_xpath = (
                        f'//*[contains(@aria-label, "{day_abbr},") and '
                        'contains(@aria-label, "Code Time") and not(contains(@aria-label, "Active Code Time"))]'
                    )
                    for element in driver.find_elements(By.XPATH, active_xpath):
                        active_total += minutes_from_aria(element.get_attribute("aria-label"))
                    for element in driver.find_elements(By.XPATH, code_xpath):
                        code_total += minutes_from_aria(element.get_attribute("aria-label"))
                metrics = calculate_software_metrics(active_total, code_total, focus_override=0)

                graph = driver.find_element(By.CLASS_NAME, "highcharts-background")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", graph)
                screenshot_path = screenshot_dir / f"week_{week_start.isoformat()}.png"
                if not driver.save_screenshot(str(screenshot_path)):
                    raise CollectionError("Chrome reported that the screenshot was not saved.")
                sheet.append([
                    week_start.isoformat(), f"Week of {week_start.strftime('%b %d')}",
                    format_duration(metrics.code_time_minutes),
                    format_duration(metrics.active_code_time_minutes), str(screenshot_path),
                ])
                _save(workbook, workbook_path)
                existing.add(week_start)
                processed += 1
                print(f"✓ Saved {screenshot_path}")
            except Exception as exc:
                failures.append(f"{week_start.isoformat()}: {exc}")
                print(f"⚠ Week failed: {exc}")
            week_start += timedelta(days=7)
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
        workbook.close()

    print(f"Weekly capture complete: {processed} processed, {skipped} skipped, {len(failures)} failed.")
    print(f"Workbook: {workbook_path}")
    if not processed and failures and not skipped:
        raise CollectionError("No weeks could be captured. " + " | ".join(failures))
    return processed
