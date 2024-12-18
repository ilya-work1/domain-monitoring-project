from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time

url = '127.0.0.1:8081'

driver = webdriver.Chrome()

def register():
    driver.get(f'{url}')
    time.sleep(5)

    register_button = driver.find_element(by=By.ID, value='register')
    register_button.click()

    username_input = driver.find_element(by=By.ID, value="username")
    password_input = driver.find_element(by=By.ID, value="password")
    confirm_password_input = driver.find_element(by=By.ID, value="confirm-password")
    
    username_input.send_keys("seleum")
    password_input.send_keys("123456")
    confirm_password_input.send_keys("123456")
    time.sleep(3)
    confirm_password_input.send_keys(Keys.RETURN)     

    time.sleep(5)
    
    driver.quit()


register()
