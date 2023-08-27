from scipy import optimize, stats
from statistics import mean, stdev
from ibkr_rest_api import REST
import numpy as np
import logging

class Stock:
    def __init__(self, symbol: str, api: REST):
        self.api = api
        self.symbol = symbol
        self.conid = self.api.get_conid(symbol)
        try:
            self.update()
        except Exception as e:
            logging.error(f"Failed to update stock data for {symbol}: {e}")

    def update(self):
        """Update stock information."""
        try:
            self.bars = self.api.get_bars(self.symbol)
            self.financials = self.api.get_fundamentals(self.conid)
            self.update_ratios()
        except Exception as e:
            logging.error(f"Failed to update stock data: {e}")
            raise

    def update_ratios(self):
        """Update essential ratios and values."""
        try:
            self.enterprise_value = self.calculate_enterprise_value()
            self.free_cash_flow = self.calculate_free_cash_flow()
            self.ebitda = float(self.financials.get('EBITDA', 0))
            self.ev_to_ebitda = self.enterprise_value / self.ebitda if self.ebitda else 0
            self.intrinsic_value = self.calculate_intrinsic_value()
        except Exception as e:
            logging.error(f"Failed to update ratios: {e}")
            raise

    def calculate_enterprise_value(self) -> float:
        market_cap = float(self.financials.get('MarketCap', 0))
        debt = float(self.financials.get('TotalDebt', 0))
        cash = float(self.financials.get('Cash', 0))
        return market_cap - cash + debt

    def calculate_free_cash_flow(self) -> float:
        cash_from_operations = float(self.financials.get('CashFromOperations', 0))
        capital_expenditures = float(self.financials.get('CapitalExpenditures', 0))
        return cash_from_operations - capital_expenditures

    def calculate_intrinsic_value(self) -> float:
        discount_rate = mean(self.api.get_industry_discount_rates(self.symbol))
        growth_rate = self.calculate_dynamic_growth_rate()
        
        def dfcf(years: int) -> float:
            return self.free_cash_flow * ((1 + growth_rate) ** years) / ((1 + discount_rate) ** years)

        intrinsic_value, _ = optimize.fixed_point(dfcf, [20])
        return intrinsic_value.item()

    def calculate_dynamic_growth_rate(self) -> float:
        return mean(self.api.get_historical_growth_rates(self.symbol))

    def is_near_52_week_low(self) -> bool:
        last_close_price = self.bars[-1]['close']
        fifty_two_week_low = min(bar['low'] for bar in self.bars[-252:])
        margin_of_safety = 0.85
        return last_close_price <= fifty_two_week_low / margin_of_safety

    def is_out_of_favor(self) -> bool:
        industry_sentiment = self.api.get_industry_sentiment(self.symbol)
        return industry_sentiment < 0


    def meets_criteria(self) -> bool:
        return self.is_undervalued() and self.within_price_range() and self.is_low_debt() and self.is_near_52_week_low()


    def calculate_sharpe_ratio(self) -> float:
        returns = np.array([bar['close'] for bar in self.bars])[:-1] / np.array([bar['close'] for bar in self.bars])[1:] - 1
        return mean(returns) / stdev(returns)

    def calculate_alpha_beta(self) -> (float, float):
        market_returns = np.array(self.api.get_market_returns(self.symbol))
        stock_returns = np.array([bar['close'] for bar in self.bars])[:-1] / np.array([bar['close'] for bar in self.bars])[1:] - 1
        beta, alpha, _ = stats.linregress(market_returns, stock_returns)
        return alpha, beta