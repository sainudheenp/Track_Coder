from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Chrome options for headless/incognito mode
options = Options()
options.add_argument('--incognito')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--headless")

# Define the path to the Chrome driver
service = Service('./Gchrome/driver/chromedriver')
driver = webdriver.Chrome(service=service, options=options)

def get_typing_data():
    try:
            driver.get("https://monkeytype.com/account")

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "acceptAll")))

            driver.find_element(By.CLASS_NAME, "acceptAll").click()

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "current-email")))
            userName_field = driver.find_element(By.NAME, "current-email")
            password_field = driver.find_element(By.NAME, "current-password")
            signIn_btn = driver.find_element(By.CLASS_NAME, "signIn")



            userName_field.send_keys(os.getenv("userEmail_monkey"))
            password_field.send_keys(os.getenv("password_monkey"))
            signIn_btn.click()


            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".group.averageWpm .val")))
            time.sleep(3)
            wpm_value = driver.find_element(By.CSS_SELECTOR, ".group.averageWpm .val")
            avg_wpm = wpm_value.text
            print(f"Typing  : {avg_wpm}wpm")

    except Exception as error:
        print(f"An error occurred: {error}")
        get_typing_data()

    finally:
        driver.quit()


get_typing_data()

# check = get_typing_data()
# if (check):
#     print(check)
# else :
#      get_typing_data()
