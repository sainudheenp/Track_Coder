from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
import time




# driver path
geckodriver_path = '../driver/geckodriver'
service =service(geckodriver_path)
driver= webdriver.Firefox(service=service)



# function for logging into monkeytyping.com

driver.get("https://monkeytype.com/account")

time.sleep(10)


# get fields
userName_field =driver.find_element(By.NAME, "current-email")
password_field =driver.find_element(By.NAME, "current-password")
signIn_btn = driver.find_element(By.CLASS , "signIn")


#entering inot fields
userName_field.send_keys("sainudheenzain313@gmail.com")
password_field.send_keys("")

signIn_btn.click()


