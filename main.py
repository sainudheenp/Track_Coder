from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta


options = Options()
options.add_argument('-private')
options.add_argument('--no-sandbox')

geckodriver_path = './driver/geckodriver'
service = FirefoxService(geckodriver_path)

driver = webdriver.Firefox(service=service, options=options)

try:
    driver.get("https://app.software.com/dashboard/components/active_code_time_graph")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))

    userName_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")
    signIn_btn = driver.find_element(By.CLASS_NAME, "btn-primary")

    userName_field.send_keys("nodaf49737@rowplant.com")
    password_field.send_keys("12345678")
    signIn_btn.click()


    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday_day = yesterday.strftime('%A')
    day_map = {
    'Monday': 'Mon',
    'Tuesday': 'Tue',
    'Wednesday': 'Wed',
    'Thursday': 'Thu',
    'Friday': 'Fri',
    'Saturday': 'Sat',
    'Sunday': 'Sun'
    }
    yesterday_abbr = day_map[yesterday_day]

    xpath = f'//*[contains(@aria-label, "{yesterday_abbr},")]'
    element = driver.find_element(By.XPATH, xpath)
    aria_label = element.get_attribute('aria-label')
    site_act = aria_label.split(",")[1].strip().split()[0]
    site_act_clean = site_act.rstrip('.')
    active_code_time =round(float(site_act_clean),2)

    hours=int(active_code_time)
    ft_minutes= active_code_time - hours
    minutes=int(ft_minutes*60)
    print(f"Yesterday's ({yesterday_abbr}) Active Code Time: {hours:01}:{minutes:02}" )




    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@aria-label, "Active Code Time")]')))

    element = driver.find_element(By.XPATH, '//*[contains(@aria-label, "Active Code Time")]')

    print(element.text)

finally:
    driver.quit()
