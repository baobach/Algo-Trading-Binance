import sys
sys.path.append("/Users/baobach/Algo-Trading-Binance")
import os
import sys
import pandas as pd
from openbb import obb
from src.config import Settings

# Load equities list
settings = Settings()
pat = settings.pat_token
obb.account.login(pat=pat)

# Create an instance of the datawrangler class
start_date = '2020-01-01'
end_date = '2024-01-01'
ticker = 'BTCUSD'
interval = '15m'

print("Downloading data...")
data = obb.crypto.price.historical(symbol = ticker, interval=interval, end_date=end_date, provider='yfinance').to_dataframe()
data.to_csv(f'data/{ticker}_{interval}.csv')



