from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import os



from dotenv import load_dotenv
load_dotenv()


# incognito

options = Options()
options.add_argument('--incognito')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--headless")





service = Service('./Gchrome/driver/chromedriver')
driver = webdriver.Chrome(service=service , options=options)


try:
    driver.get("https://monkeytype.com/account")

    WebDriverWait(driver ,10).until(EC.presence_of_element_located((By.CLASS_NAME,"rejectAll")))
    # time.sleep(10)
    try:
        dd = driver.find_element(By.CLASS_NAME, "acceptAll").click()
        print("Cookie popup accepted.")
    except Exception as e:
        print("No cookie button found or other error:", e)

    userName_field =driver.find_element(By.NAME, "current-email")
    password_field =driver.find_element(By.NAME, "current-password")
    signIn_btn = driver.find_element(By.CLASS_NAME, "signIn")

    userName_field.send_keys(os.getenv("userEmail_monkey"))
    password_field.send_keys(os.getenv("userEmail_password"))
    signIn_btn.click()
    print("hey")
    wpm_value = driver.find_element(By.CSS_SELECTOR, ".group.averageWpm .val")
    ssf =wpm_value.text
    print(f"avg wpm : {ssf}")

except Exception as error:
    print(f"An error occurred : {error}")
finally:
    driver.quit()
