import time
import threading
from datetime import datetime
import urllib3
from login_state_machine import IBKRWebPageStateMachine  # Your custom class
from ibkr_rest_api import REST  # Your custom class
from portfolio import Portfolio  # The Portfolio class we developed
import IBKRServerManager  # Your custom class
import logging

logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # disable SSL warnings


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

def trading_logic(api):
    try:
        # Initialize Portfolio
        portfolio = Portfolio(api)
    except Exception as e:
        logging.error(f"Failed to initialize Portfolio: {e}")
        return

    while True:
        try:
            # Update Portfolio and Stocks
            portfolio.update()
            
            # Print Current Portfolio Status
            logging.info("Current Portfolio Status:")
            logging.info(portfolio.get_status())
            
            # Identify Stocks to Buy
            for symbol in portfolio.stocks:
                stock = portfolio.stocks[symbol]
                if stock.meets_buy_criteria():
                    portfolio.buy_stock(symbol, 1)  # Buy one share for demonstration
            
            # Identify Stocks to Sell
            for symbol in portfolio.stocks:
                stock = portfolio.stocks[symbol]
                if stock.meets_sell_criteria():
                    portfolio.sell_stock(symbol, 1)  # Sell one share for demonstration
            
            # Wait before the next iteration
            time.sleep(3600)  # Wait for 1 hour before the next iteration
            
        except Exception as e:
            logging.error(f"An error occurred in the trading logic: {e}")
            time.sleep(60)  # Wait for 1 minute before retrying




if __name__ == "__main__":
    sleep_interval = 60 * 5  # 5 minutes
    MAX_RETRIES = 20

    # Initialize REST API
    api = REST()

    # Initialize and manage server
    server_manager = IBKRServerManager(target_port=5000, target_cmd_substring="ibgroup.web.core.clientportal.gw.GatewayStart")
    server_manager.manage_server(restart=True)
    
    # Initialize browser session for authentication
    browser_session = IBKRWebPageStateMachine()
    browser_session.main_controller()

    # Start the thread to keep the session authenticated
    auth_thread = threading.Thread(target=ping_and_authenticate, args=(api, sleep_interval, MAX_RETRIES))
    auth_thread.daemon = True  # Set as a daemon thread so it exits when the main program exits
    auth_thread.start()

    # Start the thread for trading logic
    trade_thread = threading.Thread(target=trading_logic, args=(api,))
    trade_thread.daemon = True  # Set as a daemon thread
    trade_thread.start()

    while True: 
        logging.info(api.get_portfolio())
        time.sleep(10)
