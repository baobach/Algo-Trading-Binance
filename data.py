
"""This is for all the code used to interact with the Binance API. 
Remember that the API relies on keys that is stored in your `.env` 
file and imported via the `config` module.
"""

import pandas as pd
from binance.client import Client
from config import settings
import datetime


class BinanceAPI:
    def __init__(self, api_key = settings.api_key, secret_key = settings.secret_key):
        self.__api_key = api_key
        self.__secret_key = secret_key
        self.bclient = Client(api_key=self.__api_key, api_secret=self.__secret_key)

    def minute_bar(self, symbol, begin = '1 Oct 2023', end = None):
        """Download 1 Minute trading data from Binance.

        Parameters
        ----------
        symbol : str
            The symbol of the trading pair.
        begin : str
            Choose the start date. Default is '1 Oct 2023'.
        end : str, optional
            Choose the end date. Default is today.

        Returns
        -------
        {Symbol}_MinuteBars.csv
            Columns are 'open', 'high', 'low', 'close', and 'volume'.
            All are numeric.
            Store in the './data/' folder.
        """
        
        print('Downloading...')

        # Specify start day and end date
        start_date = datetime.datetime.strptime(begin, '%d %b %Y')
        if end is None:
            end_date = datetime.datetime.today()
        elif isinstance(end, str):
            end_date = datetime.datetime.strptime(end, '%d %b %Y')
        else:
            end_date = end
        end_date_str = end_date.strftime('%d %b %Y %H:%M:%S')
        end_date = datetime.datetime.strptime(end_date_str, '%d %b %Y %H:%M:%S')   

        # Specify file name
        filename = '{}_1Min.parq'.format(symbol)

        # Download 1_Min trading data
        klines = self.bclient.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, start_date.strftime("%d %b %Y %H:%M:%S"), end_date.strftime("%d %b %Y %H:%M:%S"), 1000)
        data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)

        # Drop unused columns
        data = data[['open', 'high', 'low', 'close', 'volume']]

        # Save to `.parquet` format
        data.to_parquet(f"./data/{filename}")

        print('Completed!')
        
