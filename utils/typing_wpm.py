# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
from dotenv import load_dotenv
from utils.get_driver import get_driver
from .get_driver import get_driver

load_dotenv()

def get_wpm():
    print("Driver installing...")
    driver = get_driver()
    try:
            driver.get("https://monkeytype.com/account")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rejectAll")))
            driver.find_element(By.CLASS_NAME, "rejectAll").click()

            time.sleep(3)

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "current-email")))
            userName_field = driver.find_element(By.NAME, "current-email")
            password_field = driver.find_element(By.NAME, "current-password")
            signIn_btn = driver.find_element(By.CLASS_NAME, "signIn")



            userName_field.send_keys(os.getenv("userEmail_monkey"))
            password_field.send_keys(os.getenv("password_monkey"))
            signIn_btn.click()


            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".group.averageWpm .val")))

            time.sleep(4)

            wpm_value = driver.find_element(By.CSS_SELECTOR, ".group.averageWpm10 .val")
            avg_wpm = wpm_value.text

            if avg_wpm == '':
                        avg_wpm = 35

            return avg_wpm

    except Exception as error:
        print(f"WPM Fetch error: {str(error)}")
        return 35  # Return default value instead of sys.exit


    finally:
        driver.quit()
