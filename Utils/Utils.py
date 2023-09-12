import os
import json

class Utils:

    def __init__(self):
        pass

    def read_json_data(self, filename: str = "Account.json"):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), filename), 'r') as f:
            return json.load(f)
    
    
        

    