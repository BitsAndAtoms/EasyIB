import time, logging, threading
from IBKRWebPageStateMachine import IBKRWebPageStateMachine  # Your custom class
from Utils.Utils import Utils 
from IBKRServerManager  import IBKRServerManager  # Your custom class

def start_gateway(restart=True):
    # Initialize and manage server
    server_manager = IBKRServerManager(target_port=5000, target_cmd_substring=Utils().read_json_data("Config.json")["target_cmd_substring"])
    server_manager.manage_server(restart=restart)

def thread_run_api_ping(api):
    # Start the thread to keep the session authenticated
    auth_thread = threading.Thread(target=ping_and_authenticate, args=(api,))
    auth_thread.daemon = True  # Set as a daemon thread so it exits when the main program exits
    auth_thread.start()

def ping_and_authenticate(api):
        ## config
        config_json= Utils().read_json_data("Config.json")
        retry_count = 0
        while True:
            try:
                logging.info("Trying to ping the server...")
                ping_result = api.ping_server()["iserver"]["authStatus"]["authenticated"]
                logging.info(f"Server ping result: {ping_result}")

                if not ping_result:
                    logging.info("Re-authenticating...")
                    api.re_authenticate()
                    time.sleep(config_json["sleep_interval"])
                    auth_result = api.get_auth_status()["authenticated"]
                    if auth_result:
                        logging.info(f"Re-authentication is successful. Re-authentication result: {auth_result}")
                    else:
                        logging.info(f"Re-authentication is failing. Re-authentication result: {auth_result}")
                else:              
                    logging.info("Authenticated.")
                retry_count = 0  # Reset retry count on successful operation
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                retry_count += 1
                if retry_count >= config_json["max_retries"]:
                    logging.error(f"Max retries exceeded. Server is not responding. Terminating the program.")
                    raise

            time.sleep(config_json["sleep_interval"])

def operate_browser(account_type="paper", wait_to_confirm=True):
    # Initialize browser session for authentication
    browser_session = IBKRWebPageStateMachine(account_type)
    browser_session.main_controller(type=account_type,wait_to_confirm=wait_to_confirm)
            
    
    
    