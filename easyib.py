import time
import threading
from IBKRWebPageStateMachine import IBKRWebPageStateMachine  # Your custom class
from ibkr_rest_api import REST  # Your custom class
from IBKRServerManager  import IBKRServerManager  # Your custom class
import logging
import urllib3
from Utils.Utils import Utils 
logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings(urllib3.connectionpool.InsecureRequestWarning)




if __name__ == "__main__":
    # TODO Restart the whole program if an error occurs. Idempotent operation.
    ACCOUNT_TYPE = "paper"  # Change to "live" for live account

    ## config
    config_json= Utils().read_json_data("Config.json")
    sleep_interval = config_json["sleep_interval"]
    MAX_RETRIES = config_json["max_retries"]

    # Initialize and manage server
    server_manager = IBKRServerManager(target_port=5000, target_cmd_substring="ibgroup.web.core.clientportal.gw.GatewayStart")
    server_manager.manage_server(restart=True)

    # Initialize browser session for authentication
    browser_session = IBKRWebPageStateMachine(ACCOUNT_TYPE)
    browser_session.main_controller(type=ACCOUNT_TYPE,wait_to_confirm=True)

    # # Initialize REST API
    api = REST()

    # Start the thread to keep the session authenticated
    utils_obj = Utils()
    auth_thread = threading.Thread(target=utils_obj.ping_and_authenticate, args=(api, sleep_interval, MAX_RETRIES))
    auth_thread.daemon = True  # Set as a daemon thread so it exits when the main program exits
    auth_thread.start()

    # Start the thread for trading logic
    # trade_thread = threading.Thread(target=trading_logic, args=(api,))
    # trade_thread.daemon = True  # Set as a daemon thread
    # trade_thread.start()

    while True: 
        try:
         logging.info(api.get_portfolio())
         time.sleep(10)
        except Exception as e:
            logging.error(f"An error occurred in the trading logic: {e}")
