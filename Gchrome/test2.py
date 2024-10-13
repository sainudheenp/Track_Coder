import os
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from utils.get_driver import get_driver
# def get_driver():
#     # Get the ChromeDriver regardless of the OS
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#     return driver


# Example usage
if __name__ == "__main__":
    driver = get_driver()
    driver.get("https://www.example.com")
    print(driver.title)  # Print the title of the page
    driver.quit()  # Close the browser
