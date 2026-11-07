"""MonkeyType provider; importing this module never starts a browser."""

from __future__ import annotations

import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from trackcoder.errors import CollectionError, ConfigurationError

from .get_driver import get_driver


def get_wpm(*, timeout: int = 20, headless: bool | None = None) -> float | None:
    email = os.getenv("userEmail_monkey")
    password = os.getenv("password_monkey")
    if not email or not password:
        raise ConfigurationError(
            "MonkeyType credentials are missing. Set userEmail_monkey and password_monkey, or use --skip-wpm."
        )
    driver = None
    try:
        driver = get_driver(headless=headless, timeout=timeout)
        wait = WebDriverWait(driver, timeout)
        driver.get("https://monkeytype.com/account")
        cookie_buttons = driver.find_elements(By.CLASS_NAME, "rejectAll")
        if cookie_buttons:
            cookie_buttons[0].click()

        wait.until(EC.presence_of_element_located((By.NAME, "current-email")))
        driver.find_element(By.NAME, "current-email").send_keys(email)
        driver.find_element(By.NAME, "current-password").send_keys(password)
        driver.find_element(By.CLASS_NAME, "signIn").click()

        wait.until(EC.any_of(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".group.averageWpm10 .val")),
            EC.presence_of_element_located((By.CSS_SELECTOR, ".group.averageWpm .val")),
        ))
        elements = driver.find_elements(By.CSS_SELECTOR, ".group.averageWpm10 .val")
        if not elements:
            elements = driver.find_elements(By.CSS_SELECTOR, ".group.averageWpm .val")
        text = elements[0].text.strip() if elements else ""
        # Missing measurements stay missing. Never substitute a fabricated WPM.
        return float(text) if text else None
    except (ConfigurationError, CollectionError):
        raise
    except Exception as exc:
        raise CollectionError(f"Could not collect MonkeyType WPM: {exc}") from exc
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
