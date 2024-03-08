import sys
sys.path.append("/Users/baobach/Algo-Trading-Binance")
import os
import sys
import pandas as pd
from openbb import obb
from src.config import get_api_key

# Load equities list
pat = get_api_key()
obb.account.login(pat=pat)

# Create an instance of the datawrangler class
start_date = '2020-01-01'
end_date = '2024-01-01'

historical_data = obb.crypto.price.historical("BTCUSD", provider="yfinance", interval="15m").to_df()
print(historical_data.tail())



