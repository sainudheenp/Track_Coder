"""Software.com code-time provider with explicit waits and safe cleanup."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from trackcoder.config import Settings
from trackcoder.errors import CollectionError, ConfigurationError, ValidationError
from trackcoder.software import calculate_software_metrics, minutes_from_aria
from trackcoder.timeutils import format_duration, parse_date, parse_duration

from .get_driver import get_driver


def _focus_from_prompt(calculated: int) -> int:
    if not sys.stdin.isatty():
        return calculated
    suggestion = format_duration(calculated)
    while True:
        answer = input(f"Focus time [{suggestion}] (Enter to accept, or type 02:30): ").strip()
        if not answer:
            return calculated
        try:
            return parse_duration(answer, field="focus")
        except ValidationError as exc:
            print(exc)


def get_code_time(
    yesterday: str, *, focus_override: int | None = None, interactive: bool = True,
    timeout: int = 20, headless: bool | None = None, screenshot_dir: str | Path | None = None,
) -> tuple[str, str, str]:
    day = parse_date(yesterday)
    email = os.getenv("userEmail_code_time")
    password = os.getenv("password_code_time")
    if not email or not password:
        raise ConfigurationError(
            "Software.com credentials are missing. Set userEmail_code_time and "
            "password_code_time, or use --skip-code-time."
        )
    settings = Settings.from_env()
    destination = Path(screenshot_dir).expanduser() if screenshot_dir else settings.screenshot_dir
    driver = None
    try:
        driver = get_driver(headless=headless, timeout=timeout)
        wait = WebDriverWait(driver, timeout)
        driver.get(f"https://app.software.com/code_time?week_of={day.isoformat()}")
        wait.until(lambda current: (
            current.find_elements(By.NAME, "email")
            or current.find_elements(By.CLASS_NAME, "highcharts-background")
        ))
        if driver.find_elements(By.NAME, "email"):
            driver.find_element(By.ID, "email").send_keys(email)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.CLASS_NAME, "btn-primary").click()

        day_abbr = day.strftime("%a")
        active_xpath = (
            f'//*[contains(@aria-label, "{day_abbr},") and '
            'contains(@aria-label, "Active Code Time")]'
        )
        code_xpath = (
            f'//*[contains(@aria-label, "{day_abbr},") and '
            'contains(@aria-label, "Code Time") and not(contains(@aria-label, "Active Code Time"))]'
        )
        active_element = wait.until(EC.presence_of_element_located((By.XPATH, active_xpath)))
        code_element = wait.until(EC.presence_of_element_located((By.XPATH, code_xpath)))
        active_minutes = minutes_from_aria(active_element.get_attribute("aria-label"))
        code_minutes = minutes_from_aria(code_element.get_attribute("aria-label"))
        metrics = calculate_software_metrics(
            active_minutes, code_minutes, focus_override=focus_override,
        )
        focus_minutes = metrics.focus_minutes
        if focus_override is None and interactive:
            focus_minutes = _focus_from_prompt(focus_minutes)

        graph = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "highcharts-background")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", graph)
        destination.mkdir(parents=True, exist_ok=True)
        screenshot_path = destination / f"{day.isoformat()}.png"
        if not driver.save_screenshot(str(screenshot_path)):
            raise CollectionError(f"Chrome did not save the screenshot to {screenshot_path}.")
        print(f"✓ Screenshot saved: {screenshot_path}")
        return (
            format_duration(focus_minutes),
            format_duration(metrics.active_code_time_minutes),
            format_duration(metrics.code_time_minutes),
        )
    except (ConfigurationError, CollectionError):
        raise
    except Exception as exc:
        raise CollectionError(f"Could not collect Software.com code time for {day}: {exc}") from exc
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
