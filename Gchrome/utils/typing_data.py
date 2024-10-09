from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as Service
from selenium.webdriver.firefox.options import Options
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


from dotenv import load_dotenv
import os


# incognito

options = Options()
options.add_argument('-private')
options.add_argument('--no-sandbox')
options.add_argument("--headless")





service = Service('./driver/geckodriver')
driver = webdriver.Firefox(service=service)



# function for logging into monkeytyping.com

driver.get("https://monkeytype.com/login")

time.sleep(10)

# Cache_btn = driver.find_elements_by_class_name("acceptAll").click()
print("hi1")

try:
    dd = driver.find_element(By.CLASS_NAME, "acceptAll").click()
    print("Cookie popup accepted.")
except Exception as e:
    print("No cookie button found or other error:", e)






# get fields
userName_field =driver.find_element(By.NAME, "current-email")
password_field =driver.find_element(By.NAME, "current-password")
signIn_btn = driver.find_element(By.CLASS_NAME, "signIn")


#entering inot fields
userName_field.send_keys("email")
password_field.send_keys("psd")

signIn_btn.click()

time.sleep(10)


wpm_value = driver.find_element(By.CSS_SELECTOR, ".averageWpm .val")
ssf =wpm_value.text
print(f"avg wpm : {ssf}")

driver.quit()