from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
import logging

logging.basicConfig(level=logging.INFO)

def wait_for_page_to_load(sleep_time=5, max_retries=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            page_able_to_load = False
            retry_count = 0
            while not page_able_to_load and retry_count < max_retries:
                try:
                    func(*args, **kwargs)
                    page_able_to_load = True
                except NoSuchElementException:
                    retry_count += 1
                    logging.warning(f"Page is not able to load. Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
            if not page_able_to_load:
                logging.error("Page is not able to load after max retries.")
                raise Exception("Page is not able to load after max retries.")
        return wrapper
    return decorator


class IBKRWebPage:

    def __init__(self):
        self.driver: WebDriver = self.setup_chrome_driver()

    def setup_chrome_driver(self) -> WebDriver:
        chrome_options = Options()
        chrome_options.add_argument("--ignore-certificate-errors")
        return webdriver.Chrome(options=chrome_options)
    
    @wait_for_page_to_load(sleep_time=5, max_retries=10)
    def fill_form(self, element_id, value):
        self.driver.find_element(By.ID, element_id).send_keys(value)

    @wait_for_page_to_load(sleep_time=5, max_retries=10)
    def click_button(self, element_id):
        self.driver.find_element(By.ID, element_id).click()
    
    @wait_for_page_to_load(sleep_time=5, max_retries=10)
    def click_partial_link_text(self, text):
        self.driver.find_element(By.PARTIAL_LINK_TEXT, text).click()

    @wait_for_page_to_load(sleep_time=5, max_retries=10)
    def click_by_css_selector(self, selector):
        self.driver.find_element(By.CSS_SELECTOR, selector).click()

    @wait_for_page_to_load(sleep_time=5, max_retries=10)
    def find_element_by_class(self, class_name):
        return self.driver.find_element(By.CLASS_NAME, class_name)

    @wait_for_page_to_load(sleep_time=5, max_retries=10)
    def find_element_by_id(self, element_id):
        return self.driver.find_element(By.ID, element_id)

    @wait_for_page_to_load(sleep_time=5, max_retries=10)
    def submit_form(self):
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    def login_to_ibkr_server(self, username, password):
        self.fill_form("xyz-field-username", username)
        self.fill_form("xyz-field-password", password)
        self.click_button("login-button-id") 
    
    @wait_for_page_to_load(sleep_time=5, max_retries=10)
    def navigate_to_home(self):
        self.driver.get("https://localhost:5000")
    
      