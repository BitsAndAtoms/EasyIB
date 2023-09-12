from enum import Enum, auto
from ibkr_webpage import IBKRWebPage
from Utils.Utils import Utils
import time
import logging

class BrowserState(Enum):
    LOGGED_OUT = auto()
    LOGGED_IN = auto()
    CHALLENGE_PRESENTED = auto()

class IBKRWebPageStateMachine(IBKRWebPage):
    def __init__(self, type="paper"):
        super().__init__(type=type)
        self.state = BrowserState.LOGGED_OUT
        self.account_data = Utils().read_json_data("Account.json")
        self.page_login = Utils().read_json_data("Config.json")["Login_page_elements"]
        self.page_challenge = Utils().read_json_data("Config.json")["Challenge_page_elements"]

    def transition_to_logged_in(self, type="paper"):
        self.navigate_to_url(self.page_login["url"])
        self.fill_form(self.page_login["username"], self.account_data[type + "_username"])
        self.fill_form(self.page_login["password"], self.account_data[type + "_password"])
        self.click_by_css_selector(self.page_login["login_button"])
        self.state = BrowserState.LOGGED_IN

    def transition_to_challenge_presented(self, wait_to_confirm=True):
        if wait_to_confirm:
           logging.info("Please confirm the login from your phone.")
           time.sleep(5)
           retry_count = 0
           while self.page_login["max_retries"] > retry_count:
               retry_count += 1
               # check if the text on page is success
               if self.find_element_by_xpath("//*[text()='Client login succeeds']"):
                     self.state = BrowserState.LOGGED_IN
                     return
               time.sleep(self.page_login["sleep_interval"])
        self.click_partial_link_text(self.page_challenge["QR_link"])
        self.click_partial_link_text(self.page_challenge["Challenge_link"])
        self.state = BrowserState.CHALLENGE_PRESENTED

    def handle_challenge(self, challenge_code):
        # Handle the challenge here
        submit_value_field = self.find_element_by_id(self.page_challenge["Challenge_response"])  # Replace with the actual ID
        user_input = input(f"Use the challenge code {challenge_code} and enter the reply to continue.")
        submit_value_field.send_keys(user_input)
        self.click_by_css_selector(self.page_login["login_button"])
        self.state = BrowserState.LOGGED_IN

    def main_controller(self, type="paper", wait_to_confirm=True):
        if self.state == BrowserState.LOGGED_OUT:
            self.transition_to_logged_in(type)
        
        if self.state == BrowserState.LOGGED_IN:
            self.transition_to_challenge_presented(wait_to_confirm)

        if self.state == BrowserState.CHALLENGE_PRESENTED:
            self.handle_challenge(self.find_element_by_class(self.page_challenge["Challenge_text"]).text)


