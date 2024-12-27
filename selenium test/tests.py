from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from logger import logging , url , test_email , test_password
import time
import os

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('detach', True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(10)
    return driver



def register_test():
    driver = setup_driver() 
    wait = WebDriverWait(driver, 10)

    try:
        logging.info('Starting register test')
        driver.get(url)
        logging.info('Page loaded')

        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        register_button.click()
        logging.info("Register button clicked")

        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys("test1")
        logging.info("Username entered")
        
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        logging.info("Password entered")

        confirm_password = wait.until(EC.presence_of_element_located((By.ID, "confirm-password")))
        confirm_password.send_keys('test')
        logging.info("Confirm password entered")
        
        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        time.sleep(1)
        register_button.click()
        logging.info("Register button clicked")
        
        try:
            positive_message=driver.find_element(By.ID, "positive")
            if positive_message.text == "You have successfully registered. Please sign in.":
                logging.info("User registered successfully")
            else:
                logging.error("Registration failed")
                raise Exception("Registration failed")
        except:
            logging.error('Registration failed')
            raise Exception("Registration failed")

    except WebDriverException as e:
        logging.error(f"Could not reach site {url}: {e}")
        raise

    finally:
        driver.quit()

def login_test():
    driver = setup_driver() 
    wait = WebDriverWait(driver, 10)

    try:
        logging.info('Starting login test')
        driver.get(url)
        logging.info('Page loaded')

        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys("test1")
        logging.info("Username entered")

        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        logging.info("Password entered")

        login_button = wait.until(EC.presence_of_element_located((By.ID, "login")))
        login_button.click()
        logging.info("Login button clicked")
        
        try:
            user_profile = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "user-profile")))
            if user_profile.is_displayed():
                logging.info('Login successful')
        except:
            logging.error('Login failed')
            raise Exception('Login failed')

    except WebDriverException as e:
        logging.error(f"Could not reach site {url}: {e}")
        raise

    finally:
        driver.quit()


#checks for single add domain , refresh all , domain deletion and logout functionality

def dashboard_test():
    driver = setup_driver() 
    wait = WebDriverWait(driver, 10)

    try:
        logging.info('Starting dashboard test')
        driver.get(url)
        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        register_button.click()
        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys("DashboardTest")
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        confirm_password = wait.until(EC.presence_of_element_located((By.ID, "confirm-password")))
        confirm_password.send_keys('test')
        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        time.sleep(3)
        register_button.click()
        logging.info('Registering DashboardTest user')

        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys("DashboardTest")
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        login_button = wait.until(EC.presence_of_element_located((By.ID, "login")))
        login_button.click()
        logging.info("Login in as DashboardTest user")
        try:
            user_profile = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "user-profile")))
            if user_profile.is_displayed():
                logging.info('Dashboard page loaded')
        except:
            driver.quit()
            logging.error('Dashboard page failed to load')
            raise Exception('Dashboard page failed to load')
        
        logging.info('**CHECKING** single add domain functionality')
        domain_input=wait.until(EC.presence_of_element_located((By.ID, 'domainInput')))
        domain_input.send_keys('google.com')
        logging.info('url "google.com" typed in add domain card')

        add_button=wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-button")))
        add_button.click()
        logging.info('Add button clicked')
        
        try:
            domain_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//tbody[@id='domainsTableBody']//td[contains(text(), 'google.com')]")))
            if domain_element.is_displayed():
                logging.info("Domain was successfully added to dashboard")
        except:
            driver.quit()
            logging.error("Failed to find added domain in dashboard")
            raise Exception("Failed to find added domain in dashboard")

        logging.info('**CHECKING** Refresh All button')
        refresh_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "refresh-button")))
        refresh_button.click()  
        
        spinner = wait.until(EC.presence_of_element_located((By.ID, "spinner")))
        if spinner.is_displayed():
            logging.info("Refresh started")
        else:
            driver.quit()
            logging.error("Refresh failed to start")
            raise Exception("Refresh failed to start")

        wait.until(EC.invisibility_of_element_located((By.ID, "spinner")))
        logging.info("Refresh completed")

        table_body = wait.until(EC.presence_of_element_located((By.ID, "domainsTableBody")))
        if table_body.is_displayed():
            logging.info("Table refreshed successfully")
        else:
            driver.quit()
            logging.error("Table failed to refresh")
            raise Exception("Table failed to refresh")
            
        logging.info('**CHECKING** domain deletion from table')
        table_body = wait.until(EC.presence_of_element_located((By.ID, "domainsTableBody")))
        initial_domains = table_body.find_elements(By.TAG_NAME, "tr")
        initial_count = len(initial_domains)

        delete_button = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//tbody[@id='domainsTableBody']//tr[1]//button[contains(@class, 'delete-button')]")))
        domain_to_delete = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//tbody[@id='domainsTableBody']//tr[1]//td[1]"))).text
        delete_button.click()
        logging.info('Delete button clicked')

        alert = wait.until(EC.alert_is_present())
        alert.accept() 
        logging.info("Deletion Alert accepted")

        alert = wait.until(EC.alert_is_present())
        alert.accept()
        logging.info("Confirmation Alert accepted")
        
        wait.until(EC.invisibility_of_element_located(
            (By.XPATH, f"//tbody[@id='domainsTableBody']//td[contains(text(), '{domain_to_delete}')]")))

        updated_domains = table_body.find_elements(By.TAG_NAME, "tr")
        if len(updated_domains) < initial_count:
            logging.info(f"Domain {domain_to_delete} was successfully deleted")
        else:
            logging.error("Domain deletion failed")
            raise Exception("Domain deletion failed")

        logging.info('**CHECKING** Logout button')

        logout_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "logout-button")))
        logout_button.click()
        logging.info("Clicked logout button")

        login_form = wait.until(EC.presence_of_element_located((By.ID, "username")))
        if login_form.is_displayed():
            logging.info("Successfully logged out")
        else:
            driver.quit()
            logging.error("Failed to log out")
            raise Exception("Failed to log out")

    except WebDriverException as e:
        logging.error(f"An error occurred: {e}")
        raise
    
    finally:
        driver.quit()
    
#checks to see if users are not sharing the same dashboard

def DataManagment_test():
    driver = setup_driver() 
    try:
        wait = WebDriverWait(driver, 10)
        logging.info('Starting DataManagment Test')
        driver.get(url)

        logging.info('Registering 2 TestUsers')    
        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        register_button.click()
        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys("testuser1")
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        confirm_password = wait.until(EC.presence_of_element_located((By.ID, "confirm-password")))
        confirm_password.send_keys('test')
        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        time.sleep(3)
        register_button.click()
        
        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        register_button.click()
        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys("testuser2")
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        confirm_password = wait.until(EC.presence_of_element_located((By.ID, "confirm-password")))
        confirm_password.send_keys('test')
        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        time.sleep(3)
        register_button.click()

        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys("testuser1")
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        login_button = wait.until(EC.presence_of_element_located((By.ID, "login")))
        login_button.click()
        logging.info('Logged in as testuser1')
        
        
        domain_input = wait.until(EC.presence_of_element_located((By.ID, "domainInput")))
        domain_input.send_keys("example.com")
        add_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-button")))
        add_button.click()
        domain_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//tbody[@id='domainsTableBody']//td[contains(text(), 'example.com')]")))
        
        if domain_element.is_displayed():
            logout_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "logout-button")))
            logout_button.click()
            logging.info('adding domain example.com and logging out')

        username2 = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username2.send_keys("testuser2")
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        login_button = wait.until(EC.presence_of_element_located((By.ID, "login")))
        login_button.click()
        logging.info('logging in as testuser2')

        logging.info('checking dashboard')
        domains_list = driver.find_elements(By.XPATH, "//tbody[@id='domainsTableBody']//td") 
        domain_found = False  
        for domain in domains_list:  
            if "example.com" in domain.text:
                domain_found = True
                logging.error("Security issue: Shared Dashboard")
                raise Exception("Security issue: Shared Dashboard")
        
        if not domain_found: 
            logging.info("Dashboard not shared")
    
    except WebDriverException as e:
        logging.error(f"An error occurred: {e}")
        raise
    
    finally:
        driver.quit()

def BulkUpload_test():
    driver = setup_driver() 
    try:
        wait = WebDriverWait(driver, 10)
        logging.info('Starting bulk upload test')
        driver.get(url)
        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        register_button.click()
        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys("DomainBulkTest")
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        confirm_password = wait.until(EC.presence_of_element_located((By.ID, "confirm-password")))
        confirm_password.send_keys('test')
        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        time.sleep(3)
        register_button.click()
        logging.info('Registering DomainBulkTest user')

        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys("DomainBulkTest")
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        login_button = wait.until(EC.presence_of_element_located((By.ID, "login")))
        login_button.click()
        logging.info("Login in as DomainBulkTest user")

        file_input = wait.until(EC.presence_of_element_located((By.ID, "file-upload")))
        
        logging.info('Creating a temporary file with domains')
        temp_file_path = "test_domains.txt"
        with open(temp_file_path, "w") as f:
            f.write("example1.com\nexample2.com\nexample3.com")
        
        logging.info('Uploading the file') 
        file_input.send_keys(os.path.abspath(temp_file_path))
        logging.info("File uploaded")

        alert = wait.until(EC.alert_is_present())
        alert.accept() 
        logging.info("Upload Alert accepted")

        spinner = wait.until(EC.presence_of_element_located((By.ID, "spinner")))
        if spinner.is_displayed():
            logging.info("Waiting for domains to load")

        wait.until(EC.invisibility_of_element_located((By.ID, "spinner")))
        logging.info("Domains loaded")
            
        try:
            logging.info('Verifying domains')
            for domain in ["example1.com", "example2.com", "example3.com"]:
                domain_element = wait.until(EC.presence_of_element_located(
                    (By.XPATH, f"//tbody[@id='domainsTableBody']//td[contains(text(), '{domain}')]")))
                if domain_element.is_displayed():
                    logging.info(f"Domain {domain} was successfully added")
                    
            logging.info("Bulk upload successful - all domains found")
            
        except Exception as e:
            driver.quit
            logging.error(f"Failed to verify uploaded domains: {e}")
            raise
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    except WebDriverException as e:
        logging.error(f"An error occurred: {e}")
        raise

    finally:
        driver.quit() 
        
def scheduler_test():
    driver = setup_driver() 
    try:
        wait = WebDriverWait(driver, 10)
        logging.info('Starting scheduler test')
        driver.get(url)
        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        register_button.click()
        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys("SchedulerTest")
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        confirm_password = wait.until(EC.presence_of_element_located((By.ID, "confirm-password")))
        confirm_password.send_keys('test')
        register_button = wait.until(EC.presence_of_element_located((By.ID, "register")))
        time.sleep(3)
        register_button.click()
        logging.info('Registering SchedulerTest user')
        
        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.send_keys("SchedulerTest")
        password = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password.send_keys('test')
        login_button = wait.until(EC.presence_of_element_located((By.ID, "login")))
        login_button.click()
        logging.info('Logging in as SchedulerTest user')

        domain_input=wait.until(EC.presence_of_element_located((By.ID, 'domainInput')))
        domain_input.send_keys('example.com')
        logging.info('adding example.com url')

        add_button=wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-button")))
        add_button.click()

        domain_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//tbody[@id='domainsTableBody']//td[contains(text(), 'example.com')]")))
        if domain_element.is_displayed():
            logging.info("added example.com")
        
        logging.info("Testing hourly schedule")
        hourly_radio = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@name='schedule-type'][@value='hourly']")))
        hourly_radio.click()
        
        logging.info('setting interval every 2 hours')
        interval_input = wait.until(EC.presence_of_element_located((By.ID, "hourlyInterval")))
        interval_input.clear()
        interval_input.send_keys("2")
        
        logging.info('Starting Schedule')
        start_button = wait.until(EC.presence_of_element_located((By.ID, "startSchedule")))
        start_button.click()
        
        next_run = wait.until(EC.presence_of_element_located((By.ID, "nextRunTime")))
        if "Not scheduled" not in next_run.text:
            logging.info("test successful")
        
        logging.info('Stopping Schedule')
        stop_button = wait.until(EC.presence_of_element_located((By.ID, "stopSchedule")))
        stop_button.click()
        
        logging.info("Testing daily schedule")
        daily_radio = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@name='schedule-type'][@value='daily']")))
        daily_radio.click()
        
        logging.info('Setting time to 14:00')
        time_input = wait.until(EC.presence_of_element_located((By.ID, "dailyTime")))
        time_input.clear()
        time_input.send_keys("14:00")
        
        logging.info('Starting Schedule')
        start_button.click()
        
        next_run = wait.until(EC.presence_of_element_located((By.ID, "nextRunTime")))
        if "Not scheduled" not in next_run.text:
            logging.info("test successful")
            
        logging.info('Stopping Schedule')
        stop_button.click()
        
        logging.info("Scheduler test completed successfully")
            
    except WebDriverException as e:
        logging.error(f"An error occurred: {e}")
        raise
    
    finally:
        driver.quit() 

def GoogleLogin_test():
    driver = setup_driver() 
    wait = WebDriverWait(driver, 10)
    try:
        logging.info('Starting Google login test')
        driver.get(url)

        google_button = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "google-button")))
        google_button.click()
        logging.info("Clicked Google login button")
        
        try:
            logging.info('Typing test email')
            email_input = wait.until(EC.presence_of_element_located(
                (By.NAME, "identifier")))
            email_input.send_keys(test_email)
            
            logging.info('Clicking next')
            next_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[text()='Next']")))
            next_button.click()
            
            logging.info('Typing test password')
            password_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input.whsOnd.zHQkBf[type='password']")))
            password_input.send_keys(test_password)
            
            logging.info('logging in')
            signin_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[text()='Next']")))
            signin_button.click()

            try:
                logging.info('Checking for Terms of Service page')
                accept_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(), 'Accept')]") or 
                    (By.XPATH, "//span[contains(text(), 'I agree')]")))
                accept_button.click()
                logging.info('Accepted Terms of Service')
            except:
                logging.info('No Terms of Service page found, continuing...')
            
            logging.info('checking if logged in')
            user_profile = wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, "user-profile")))
            
            if user_profile.is_displayed():
                logging.info("Google login was successful")
                    
        except WebDriverException as e:
            logging.error(f"Failed during Google authentication: {e}")
            raise
            
    except WebDriverException as e:
        logging.error(f"Google login test failed: {e}")
        raise
        
    finally:
        driver.quit()




