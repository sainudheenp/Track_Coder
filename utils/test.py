from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up incognito mode
options = Options()
options.add_argument('-private')
options.add_argument('--no-sandbox')

# Driver path
geckodriver_path = './driver/geckodriver'
service = FirefoxService(geckodriver_path)

# Initialize WebDriver
driver = webdriver.Firefox(service=service, options=options)

try:
    # Navigate to the login page
    driver.get("https://monkeytype.com/account")
    
    # Wait for the elements to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "current-email")))
    
    # Get fields
    userName_field = driver.find_element(By.NAME, "current-email")
    password_field = driver.find_element(By.NAME, "current-password")
    signIn_btn = driver.find_element(By.CLASS_NAME, "signIn")
    
    # Entering into fields
    userName_field.send_keys("sainudheenzain313@gmail.com")
    password_field.send_keys("")  # Make sure to enter your password here
    signIn_btn.click()

    # Wait for the result page to load
    time.sleep(5)  # You can adjust this or replace it with an explicit wait

    # Check for login status
    if "dashboard" in driver.current_url:  # Adjust this condition based on the expected URL
        print("Login successful! Current URL:", driver.current_url)
    else:
        print("Login failed. Current URL:", driver.current_url)
    
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()  # Ensure the driver closes at the end
