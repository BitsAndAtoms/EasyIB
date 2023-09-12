import os
import json
import time
import logging

class Utils:

    def __init__(self):
        pass

    def read_json_data(self, filename: str = "Account.json"):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), filename), 'r') as f:
            return json.load(f)
    
    def ping_and_authenticate(self, api, sleep_interval=300, MAX_RETRIES=5):
        retry_count = 0
        while True:
            try:
                logging.info("Trying to ping the server...")
                ping_result = api.ping_server()["iserver"]["authStatus"]["authenticated"]
                logging.info(f"Server ping result: {ping_result}")

                if not ping_result:
                    logging.info("Re-authenticating...")
                    api.re_authenticate()
                    time.sleep(sleep_interval)
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
                if retry_count >= MAX_RETRIES:
                    logging.error(f"Max retries exceeded. Server is not responding. Terminating the program.")
                    raise

            time.sleep(sleep_interval)
            
    
    
    
        

    