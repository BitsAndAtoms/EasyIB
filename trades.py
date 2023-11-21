
import time
import logging
from portfolio import Portfolio  # The Portfolio class we developed

import threading

# Existing code here...

def start_trading_logic(api):
    thread = threading.Thread(target=trading_logic, args=(api,))
    thread.daemon = True  # Set as a daemon thread so it exits when the main program exits
    thread.start()

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
