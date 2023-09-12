import requests
import logging

logging.basicConfig(level=logging.INFO)

class REST:
    def __init__(self, url="https://localhost:5000", ssl=False) -> None:
        self.session = requests.Session()
        self.url = f"{url}/v1/api/"
        self.ssl = ssl
        self.id = self.get_accounts()[0]["accountId"]
    
    def _send_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Helper function to send HTTP request and return JSON response."""
        url = f"{self.url}{endpoint}"
        try:
            response = self.session.request(method, url, verify=self.ssl, **kwargs)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Failed API request. URL: {url}, Error: {str(e)}")
            raise
        return response.json()

    def get_accounts(self) -> dict:
        return self._send_request('GET', 'portfolio/accounts')

    def switch_account(self, accountId: str) -> dict:
        return self._send_request('POST', 'iserver/account', json={"acctId": accountId})

    def get_cash(self) -> float:
        return self._send_request('GET', f'portfolio/{self.id}/ledger')["USD"]["cashbalance"]

    def get_netvalue(self) -> float:
        return self._send_request('GET', f'portfolio/{self.id}/ledger')["USD"]["netliquidationvalue"]

    def get_conid(self, symbol: str, instrument_filters: dict = {}, contract_filters: dict = {"isUS": True}) -> int:
        response = self._send_request('GET', 'trsrv/stocks', params={"symbols": symbol})

        dic = response

        if instrument_filters or contract_filters:

            def filter_instrument(instrument: dict) -> bool:
                def apply_filters(x: dict, filters: dict) -> list:
                    positives = list(
                        filter(
                            lambda x: x,
                            [x.get(key) == val for key, val in filters.items()],
                        )
                    )
                    return [len(positives) == len(filters)]

                if instrument_filters:
                    valid = apply_filters(instrument, instrument_filters)

                    if not valid:
                        return False

                if contract_filters:
                    instrument["contracts"] = list(
                        filter(
                            lambda x: apply_filters(x, contract_filters),
                            instrument["contracts"],
                        )
                    )

                return len(instrument["contracts"]) > 0

            dic[symbol] = list(filter(filter_instrument, dic[symbol]))

        return response[symbol][0]["contracts"][0]["conid"]

    def get_portfolio(self) -> dict:
        positions = self._send_request('GET', f'portfolio/{self.id}/positions/0')
        return {item["contractDesc"]: item["position"] for item in positions}

    def reply_yes(self, id: str) -> dict:
        return self._send_request('POST', f'iserver/reply/{id}', json={"confirmed": True})

    def submit_orders(self, list_of_orders: list, reply_yes=True) -> dict:
        return self._send_request('POST', f'iserver/account/{self.id}/orders', json={"orders": list_of_orders})

    def get_order(self, orderId: str) -> dict:
        return self._send_request('GET', f'iserver/account/order/status/{orderId}')

    def get_live_orders(self, filters: list = [None]) -> dict:
        return self._send_request('GET', 'iserver/account/orders', params={"filters": filters or []})

    def cancel_order(self, orderId: str) -> dict:
        return self._send_request('DELETE', f'iserver/account/{self.id}/order/{orderId}')

    def modify_order(self, orderId: str, order: dict, reply_yes=True) -> dict:
        if not orderId or not order:
            raise ValueError("Input parameters (orderId or order) are missing")
        return self._send_request('POST', f'iserver/account/{self.id}/order/{orderId}', json=order)

    def ping_server(self) -> dict:
        return self._send_request('POST', 'tickle')

    def get_auth_status(self) -> dict:
        return self._send_request('POST', 'iserver/auth/status')

    def re_authenticate(self) -> None:
        self._send_request('POST', 'iserver/reauthenticate')
        logging.info("Reauthenticating ...")

    def log_out(self) -> None:
        self._send_request('POST', 'logout')

    def get_bars(self, symbol: str, period="1w", bar="1d", outsideRth=False, conid="default") -> dict:
        if conid == "default":
            conid = self.get_conid(symbol)
        
        query = {
            "conid": int(conid),
            "period": period,
            "bar": bar,
            "outsideRth": outsideRth,
        }
        
        return self._send_request('GET', 'iserver/marketdata/history', params=query)

    def get_fut_conids(self, symbol: str) -> list:
        return self._send_request('GET', 'trsrv/futures', params={"symbols": symbol})[symbol]
  
    def get_fyi_unreadnumber(self) -> dict:
        return self._send_request('GET', 'fyi/unreadnumber')

    def get_fyi_settings(self) -> dict:
        return self._send_request('GET', 'fyi/settings')

    def post_fyi_settings(self, typecode: str, payload: dict) -> dict:
        return self._send_request('POST', f'fyi/settings/{typecode}', json=payload)

    # trsrv Methods
    def post_trsrv_secdef(self, payload: dict) -> dict:
        return self._send_request('POST', 'trsrv/secdef', json=payload)

    def get_trsrv_secdef_schedule(self) -> dict:
        return self._send_request('GET', 'trsrv/secdef/schedule')

    # ccp Methods
    def post_ccp_auth_init(self, payload: dict) -> dict:
        return self._send_request('POST', 'ccp/auth/init', json=payload)

    def get_ccp_status(self) -> dict:
        return self._send_request('GET', 'ccp/status')

    # hmds Methods
    def get_hmds_history(self, params: dict) -> dict:
        return self._send_request('GET', 'hmds/history', params=params)
   
    # Fundamental Analysis
    def get_fundamentals_financials(self, conid: str) -> dict:
        return self._send_request('GET', f'fundamentals/financials/{conid}')

    def get_fundamentals_summary(self, conid: str) -> dict:
        return self._send_request('GET', f'fundamentals/summary/{conid}')

    def get_fundamentals_ownership(self, conid: str) -> dict:
        return self._send_request('GET', f'fundamentals/ownership/{conid}')

    # iserver Methods
    def post_iserver_portfolio_alter(self, payload: dict) -> dict:
        return self._send_request('POST', 'iserver/portfolio/alter', json=payload)

    def get_iserver_account_summary(self) -> dict:
        return self._send_request('GET', 'iserver/account/summary')

    def post_iserver_rebalance_portfolio(self, payload: dict) -> dict:
        return self._send_request('POST', 'iserver/portfolio/rebalance', json=payload)

    # Scanner Methods
    def get_scanner_params(self, scanner_id: str) -> dict:
        return self._send_request('GET', f'scanner/params/{scanner_id}')

    def run_scanner_plain(self, scanner_id: str, params: dict) -> dict:
        return self._send_request('POST', f'scanner/run/{scanner_id}', json=params)

    # Market Data Methods
    def get_market_data_data(self, conid: str, fields: list) -> dict:
        return self._send_request('GET', f'marketdata/{conid}/data', params={"fields": fields})

    def get_market_data_snapshot(self, conids: list) -> dict:
        return self._send_request('GET', 'marketdata/snapshot', params={"conids": conids})

    # News Methods
    def get_news_briefs(self) -> dict:
        return self._send_request('GET', 'news/briefs')

    def get_news_headlines(self, conid: str, count: int = 10) -> dict:
        return self._send_request('GET', f'news/{conid}', params={"count": count})

    # Rates Methods
    def get_rates_fx(self) -> dict:
        return self._send_request('GET', 'rates/fx')

    # Sectors Methods
    def get_sectors_subsectors(self) -> dict:
        return self._send_request('GET', 'sectors/subsectors')

    # Streaming Methods
    def post_streaming_accounts(self) -> dict:
        return self._send_request('POST', 'streaming/accounts')

    def post_streaming_alerts(self, ids: list) -> dict:
        return self._send_request('POST', 'streaming/alerts', json={"ids": ids})

    def scanner_parameters(self) -> dict:
        return self._send_request('GET', 'iserver/scanner/parameters')
        
    def scanner_parameters_custom(self, scan_code: str) -> dict:
        return self._send_request('GET', f'iserver/scanner/parameters/{scan_code}')
        
    def run_scanner(self, scanner_data: dict) -> dict:
        return self._send_request('POST', 'iserver/scanner/scan', json=scanner_data)
        
    def unsubscribe_scanner(self, subscription_id: str) -> dict:
        return self._send_request('DELETE', f'iserver/scanner/unsubscribe/{subscription_id}')
        
    def get_account_info(self) -> dict:
        return self._send_request('GET', 'portfolio/{self.id}/meta')
        
    def get_account_summary(self) -> dict:
        return self._send_request('GET', 'portfolio/{self.id}/summary')
        
    def get_account_allocation(self) -> dict:
        return self._send_request('GET', 'portfolio/{self.id}/allocation')
        
    def get_account_lod(self) -> dict:
        return self._send_request('GET', 'portfolio/{self.id}/lod')
        
    def get_account_positions(self) -> dict:
        return self._send_request('GET', 'portfolio/{self.id}/positions')
        
    def get_account_trades(self) -> dict:
        return self._send_request('GET', 'portfolio/{self.id}/trades')
        
    def get_account_transaction(self, transaction_id: str) -> dict:
        return self._send_request('GET', f'portfolio/{self.id}/transaction/{transaction_id}')
        
    def get_account_transactions(self, date: str) -> dict:
        return self._send_request('GET', f'portfolio/{self.id}/transactions/{date}')
