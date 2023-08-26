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