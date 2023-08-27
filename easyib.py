import time
import threading
from datetime import datetime
import urllib3
from login_state_machine import IBKRWebPageStateMachine
from ibkr_rest_api import REST
import IBKRServerManager
import logging

logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # disable SSL warnings


def get_current_time():
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def ping_and_authenticate(api, sleep_interval=300, MAX_RETRIES=5):
    retry_count = 0
    while True:
        try:
            if not api.ping_server()["iserver"]["authStatus"]["authenticated"]:
                api.re_authenticate()
                time.sleep(5)
                if api.get_auth_status()["authenticated"]:
                    logging.info("Re-authentication is successful.")
                else:
                    logging.info("Re-authentication is failing.")
            else:              
                logging.info("Authenticated.")
            retry_count = 0  # Reset retry count on successful operation
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            retry_count += 1
            if retry_count >= MAX_RETRIES:
                logging.error(f"Max retries exceeded. Exiting the program.")
                raise

        time.sleep(sleep_interval)

if __name__ == "__main__":
    sleep_interval = 60 * 5
    MAX_RETRIES = 20 
    api = REST()

    server_manager = IBKRServerManager(target_port=5000, target_cmd_substring="ibgroup.web.core.clientportal.gw.GatewayStart")
    server_manager.manage_server(restart=True)
    browser_session = IBKRWebPageStateMachine()
    browser_session.main_controller()

    # Start the thread to keep the session authenticated
    auth_thread = threading.Thread(target=ping_and_authenticate, args=(api, sleep_interval, MAX_RETRIES))
    auth_thread.daemon = True  # Set as a daemon thread so it exits when the main program exits
    auth_thread.start()

    while True: 
        logging.info(api.get_portfolio())
        time.sleep(10)

    
        
    # print(api.reply_yes("a37bcc93-736b-441b-88a3-ee291d5dbcbd"))
    orders = [
        {
            "conid": api.get_conid("AAPL"),
            "orderType": "MKT",
            "side": "BUY",
            "quantity": 7,
            "tif": "GTC",
        }
    ]

    server_manager.terminate_server()

    # print(api.submit_order(orders))
    # print(api.modify_order(1258176643, orders[0]))
    # print(api.get_order(1258176642))
    # print(api.get_portfolio())
    # print(api.get_live_orders())
    # print(api.get_bars("TSLA"))
    # print(api.get_conid("AAPL"))
    # print(api.get_conid("MUB", contract_filters={"isUS": True, "exchange": "ARCA"}))
    # print(api.get_conid("MUB", instrument_filters={"name": "ISHARES NATIONAL MUNI BOND E", "assetClass": "STK"}))
    # print(api.cancel_order(2027388848))
