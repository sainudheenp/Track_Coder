"""Chrome factory with local, headless, and Docker-friendly configuration."""

from __future__ import annotations

import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService

from trackcoder.errors import ConfigurationError


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_driver(*, headless: bool | None = None, timeout: int = 20):
    use_headless = _as_bool(os.getenv("TRACKCODER_HEADLESS"), True) if headless is None else headless
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    if use_headless:
        options.add_argument("--headless=new")
    binary = os.getenv("CHROME_BINARY")
    if binary:
        options.binary_location = binary

    driver_path = os.getenv("CHROME_DRIVER_PATH")
    try:
        if driver_path:
            service = ChromeService(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            # Selenium Manager resolves a compatible local driver without an
            # unconditional webdriver-manager network request.
            driver = webdriver.Chrome(options=options)
    except Exception as selenium_error:
        if driver_path:
            raise ConfigurationError(
                f"Chrome could not start with CHROME_DRIVER_PATH={driver_path}: {selenium_error}"
            ) from selenium_error
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()), options=options,
            )
        except Exception as fallback_error:
            raise ConfigurationError(
                "Chrome could not start. Install Chrome/Chromium, set CHROME_DRIVER_PATH, "
                f"or use offline commands. Selenium: {selenium_error}; fallback: {fallback_error}"
            ) from fallback_error
    driver.set_page_load_timeout(timeout)
    return driver
