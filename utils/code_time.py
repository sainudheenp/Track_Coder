from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()
import time
from utils.get_driver import get_driver
from .get_driver import get_driver


Focus = "00:00"
ACT = "00:00"
CT = "00:00"

def get_code_time():
    driver = get_driver()
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday_day = yesterday.strftime('%A')
    yesterday_url = yesterday.strftime("%Y-%m-%d")

    try:
        driver.get(f"https://app.software.com/code_time?week_of={yesterday_url}")



        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))

        userName_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        signIn_btn = driver.find_element(By.CLASS_NAME, "btn-primary")

        userName_field.send_keys(os.getenv("userEmail_code_time"))
        password_field.send_keys(os.getenv("password_code_time"))
        signIn_btn.click()


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

        Focus = "00:00"
        ACT = "00:00"
        CT = "00:00"




        time.sleep(3)

        xpath_active = f'//*[contains(@aria-label, "{yesterday_abbr},") and contains(@aria-label, "Active Code Time")]'
        element_active = driver.find_element(By.XPATH, xpath_active)
        aria_label_active = element_active.get_attribute('aria-label')

        os.makedirs(os.path.dirname(os.path.expanduser("~/TrackCoder/screenshots/")), exist_ok=True)
        driver.save_screenshot(os.path.expanduser(f"~/TrackCoder/screenshots/{yesterday_url}.png"))


        site_act = aria_label_active.split(",")[1].strip().split()[0]
        active_code_time = round(float(site_act.rstrip('.')), 2)

        hours_active = int(active_code_time//60)
        minutes_active = int(active_code_time % 60)






        # Find Code Time
        xpath_code_time = f'//*[contains(@aria-label, "{yesterday_abbr},") and contains(@aria-label, "Code Time")]'
        element_code_time = driver.find_element(By.XPATH, xpath_code_time)
        aria_label_code_time = element_code_time.get_attribute('aria-label')

        # Extract Code Time
        site_ct = aria_label_code_time.split(",")[1].strip().split()[0]
        code_time = round(float(site_ct.rstrip('.')), 2)

        ct_hours = int(code_time // 60)
        minutes_ct = int(code_time%60)

        # Calculate Total Time (Active Code Time + Code Time)
        total_minutes = (hours_active * 60 + minutes_active) + (ct_hours * 60 + minutes_ct)
        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60
        # print(f"CT      : {total_hours:01}:{remaining_minutes:02}")
        # print("total minutes",total_minutes)


        # focus
        if total_minutes != 0 :
                fc_total_minutes = total_minutes + 60
        else :
                fc_total_minutes = total_minutes


        fc_hours = fc_total_minutes // 60
        fc_minutes = fc_total_minutes % 60


        Focus=f"{fc_hours:01}:{fc_minutes:02}"
        ACT=f"{hours_active:01}:{minutes_active:02}"
        CT=f"{total_hours:01}:{remaining_minutes:02}"
        # print(f"{fc_hours:01}:{fc_minutes:02}")



        #print values

        # print(f"Focus   : {Focus}")
        # print(f"ACT     : {ACT}")
        # print(f"CT      : {CT}")




    except Exception as e:
        # print(f"Focus   : 00:00")
        print("code time err",e)
        # print(f"CT      : 00:00")

        # print(f"Focus   : {Focus}")
        # print(f"ACT     : {ACT}")
        # print(f"CT      : {CT}")



    finally:
        driver.quit()

    return Focus , ACT ,CT

# get_code_time()




