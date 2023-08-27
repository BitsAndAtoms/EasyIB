import numpy as np
from scipy.optimize import minimize
import logging
from ibkr_rest_api import REST  # Assuming the REST class is in a file named 'rest.py'
from stock import Stock  # Assuming the Stock class is in a file named 'stock.py'

class Portfolio:
    def __init__(self, api: REST):
        self.api = api
        self.stocks = {}  # Dictionary to store Stock objects
        self.cash = self.api.get_cash()
        self.net_value = self.api.get_netvalue()

    def add_stock(self, symbol: str):
        if symbol not in self.stocks:
            self.stocks[symbol] = Stock(symbol, self.api)

    def remove_stock(self, symbol: str):
        if symbol in self.stocks:
            del self.stocks[symbol]

    def buy_stock(self, symbol: str, quantity: int):
        if self.stocks[symbol].meets_criteria():
            order = {
                'conid': self.stocks[symbol].conid,
                'quantity': quantity
            }
            self.api.submit_orders([order])
            self.cash -= self.stocks[symbol].bars[-1]['close'] * quantity  # Assuming we buy at the latest close price

    def sell_stock(self, symbol: str, quantity: int):
        if symbol in self.stocks:
            order = {
                'conid': self.stocks[symbol].conid,
                'quantity': -quantity
            }
            self.api.submit_orders([order])
            self.cash += self.stocks[symbol].bars[-1]['close'] * quantity  # Assuming we sell at the latest close price

    def optimize(self):
        """Optimize the portfolio using Sharpe ratio."""
        stock_list = list(self.stocks.values())
        num_stocks = len(stock_list)
        
        def objective(weights): 
            returns = np.array([stock.sharpe_ratio for stock in stock_list])
            return -np.sum(returns * weights)
        
        constraint = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
        initial_weights = [1./num_stocks for _ in stock_list]
        bounds = [(0, 1) for _ in stock_list]
        
        solution = minimize(objective, initial_weights, bounds=bounds, constraints=constraint)
        return solution.x

    def apply_burry_strategy(self):
        """Apply Michael Burry's strategy."""
        for symbol, stock in self.stocks.items():
            if stock.is_near_52_week_low() and stock.is_out_of_favor():
                if stock.ev_to_ebitda < 10 and stock.intrinsic_value > stock.bars[-1]['close']:
                    amount = min(self.cash, stock.bars[-1]['close'] * 100)  # Buy 100 shares if possible
                    self.api.submit_orders([{'conid': stock.conid, 'amount': amount}])
                    self.cash -= amount

    def rebalance(self):
        """Rebalance the portfolio based on the optimized weights."""
        optimized_weights = self.optimize()
        for i, (symbol, stock) in enumerate(self.stocks.items()):
            target_value = optimized_weights[i] * self.net_value
            diff_value = target_value - stock.bars[-1]['close'] * stock.financials.get('SharesOutstanding', 1)
            
            if diff_value > 0:
                amount = min(self.cash, diff_value)
                self.api.submit_orders([{'conid': stock.conid, 'amount': amount}])
                self.cash -= amount
            elif diff_value < 0:
                self.api.submit_orders([{'conid': stock.conid, 'amount': diff_value}])
        self.update()

    def update(self):
        for stock in self.stocks.values():
            stock.update()
        self.cash = self.api.get_cash()
        self.net_value = self.api.get_netvalue()
