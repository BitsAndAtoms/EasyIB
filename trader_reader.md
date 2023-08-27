1. Conda envionment is called ibkrv1
2. Download the latest version of api gateway from: https://interactivebrokers.github.io/cpwebapi/quickstart
3. Make sure you have Java installed using the following command
```jave --version```
3. Unzip the file and run the following command to install the gateway
```
bin/run.sh root/conf.yaml
```
4. Make sure the gateway is running by going to the following url: http://localhost:5000/v1/api/iserver/auth/status
5. Login to the gateway using the following url: http://localhost:5000 and authenticate using your IBKR credentials

6. Documentation of available functions is at https://easyib.readthedocs.io/en/latest/reference.html.

7. See the official documentation of the End Point at https://www.interactivebrokers.com/api/doc.html.



```
from wrapper  import EWrapper
from client import EClient
sidobj = EClient(EWrapper()) 
```


Mobile app -> account --> settings --> secutiry (generate reposinbse for 2FA)


# Selenium Web Automation with IBKRWebPage

This Python project demonstrates web automation using Selenium for interacting with a webpage.

## Features

1. **Automatic Login**: Provides methods for logging into a server with a username and password.
2. **Page Navigation**: Navigates between different pages or performs actions based on given arguments.
3. **Retry Mechanism**: Retries page loading in case of failure.

## Code Overview

### Dependencies

- Selenium
- Chrome WebDriver

### Core Components

#### `wait_for_page_to_load` Function

A decorator function that waits for a webpage to load and retries up to a specified number of times before throwing an exception.

#### `IBKRWebPage` Class

A class that encapsulates the Selenium WebDriver and provides methods for web interactions.

- `__init__`: Initializes the Chrome WebDriver.
- `setup_chrome_driver`: Configures Chrome with specific options.
- `login_to_ibkr_server`: Logs into a server with a username and password.

##### `page_navigation_between_links` Method

This method navigates between different pages or performs actions based on the action argument.

```python
def page_navigation_between_links(self, action: int, **kwargs):
    def default_action():
        raise ValueError("Invalid action provided")
    
    actions = {
        -1: lambda: self.driver.get("https://localhost:5000"),
        0: lambda: self.login_to_ibkr_server(kwargs["username"], kwargs["password"]),
        1: lambda: self.driver.find_element(By.PARTIAL_LINK_TEXT, "Log in with QR Code").click(),
        2: lambda: self.driver.find_element(By.PARTIAL_LINK_TEXT, "Log in with Challenge/Response").click(),
        3: lambda: self.driver.find_element(By.CLASS_NAME, "xyz-goldchallenge"),
        4: lambda: self.driver.find_element(By.ID, "xyz-field-gold-response"),
        5: lambda: self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click(),
    }
    
    actions.get(action, default_action)()
```

## Usage

1. Install dependencies.
2. Instantiate `IBKRWebPage` class.
3. Use the available methods to perform web operations.

## Author

[Your Name]

## License

MIT License