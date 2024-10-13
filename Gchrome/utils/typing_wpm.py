from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv
from get_driver import get_driver


avg_wpm = 30

load_dotenv()

options = Options()
options.add_argument('--incognito')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--headless")

# service = Service('./Gchrome/driver/chromedriver')
# driver = webdriver.Chrome(service=service, options=options)
driver =  get_driver()

def get_wpm():
    try:
            driver.get("https://monkeytype.com/account")

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rejectAll")))

            driver.find_element(By.CLASS_NAME, "acceptAll").click()

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "current-email")))
            userName_field = driver.find_element(By.NAME, "current-email")
            password_field = driver.find_element(By.NAME, "current-password")
            signIn_btn = driver.find_element(By.CLASS_NAME, "signIn")



            userName_field.send_keys(os.getenv("userEmail_monkey"))
            password_field.send_keys(os.getenv("password_monkey"))
            signIn_btn.click()


            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".group.averageWpm .val")))

            time.sleep(5)

            wpm_value = driver.find_element(By.CSS_SELECTOR, ".group.averageWpm .val")
            avg_wpm = wpm_value.text
            # print(f"Typing  : {avg_wpm}")
            return avg_wpm

    except Exception as error:
        print(f"An error occurred: {error}")
        get_wpm()


    finally:
        driver.quit()





# check = get_typing_data()
# if (check):
#     print(check)
# else :
get_wpm()
