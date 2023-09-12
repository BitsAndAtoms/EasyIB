import time, logging, urllib3
from ibkr_rest_api import REST  # Your custom class
from startgateway import thread_run_api_ping, start_gateway, operate_browser
logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings(urllib3.connectionpool.InsecureRequestWarning)

if __name__ == "__main__":
    # TODO Restart the whole program if an error occurs. Idempotent operation.
    # # Initialize REST API
    api = REST()
    ACCOUNT_TYPE = "paper"  # Change to "live" for live account
    start_gateway(restart=True)
    operate_browser(account_type=ACCOUNT_TYPE, wait_to_confirm=True)
    thread_run_api_ping(api)

    # Start the thread for trading logic
    # trade_thread = threading.Thread(target=trading_logic, args=(api,))
    # trade_thread.daemon = True  # Set as a daemon thread
    # trade_thread.start()

    while True: 
        try:
         logging.info(api.get_portfolio())
         logging.info(api.get_accounts())
         time.sleep(10)
        except Exception as e:
            logging.error(f"An error occurred in the trading logic: {e}")
