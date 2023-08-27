from enum import Enum, auto
from ibkr_webpage import IBKRWebPage
import json
import os

class BrowserState(Enum):
    LOGGED_OUT = auto()
    LOGGED_IN = auto()
    CHALLENGE_PRESENTED = auto()

class IBKRWebPageStateMachine(IBKRWebPage):
    def __init__(self):
        super().__init__()
        self.state = BrowserState.LOGGED_OUT

    def read_account_data(self):
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "Account.json"), 'r') as f:
                return json.load(f)

    def transition_to_logged_in(self):
        self.navigate_to_home()
        account_data = self.read_account_data()  # Assume read_account_data method is available
        self.login_to_ibkr_server(account_data['username'], account_data['password'])
        self.state = BrowserState.LOGGED_IN

    def transition_to_challenge_presented(self):
        self.click_partial_link_text("Log in with QR Code")
        self.click_partial_link_text("Log in with Challenge/Response")
        self.state = BrowserState.CHALLENGE_PRESENTED

    def handle_challenge(self, challenge_code):
        # Handle the challenge here
        submit_value_field = self.find_element_by_id("xyz-field-gold-response")  # Replace with the actual ID
        user_input = input(f"Use the challenge code {challenge_code.text} and enter the reply to continue.")
        submit_value_field.send_keys(user_input)
        self.submit_form()
        self.state = BrowserState.LOGGED_IN

    def main_controller(self):
        if self.state == BrowserState.LOGGED_OUT:
            self.transition_to_logged_in()
        
        if self.state == BrowserState.LOGGED_IN:
            self.transition_to_challenge_presented()

        if self.state == BrowserState.CHALLENGE_PRESENTED:
            challenge_code = self.find_element_by_class("xyz-goldchallenge")  # Replace with the actual class name
            self.handle_challenge(challenge_code)


