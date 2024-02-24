import pandas as pd
from binance.client import Client
from binance import ThreadedWebsocketManager, BinanceSocketManager
from config import settings
from sqlalchemy import create_engine
import asyncio
class StreamData():

    def __init__(self, symbol, test_net=True):
        self.symbol = symbol
        self.api_key = settings.api_key
        self.secret_key = settings.secret_key
        self.bsm = BinanceSocketManager(self.Client)
        self.test_net = test_net


    async def main(self):
        symbol = self.symbol
        client = Client(self.api_key, self.secret_key, testnet=self.test_net)
        bsm = BinanceSocketManager(client)
        socket = bsm.kline_socket(symbol)
        engine = create_engine('sqlite:///BTCUSDTstream.db')
        current_event = pd.Series(pd.to_datetime(0))
        while True:
            await socket.__aenter__()
            msg = await socket.recv()
            await socket.__aexit__()
            df = self._transform_data(msg)  # Fix: Added self reference to _transform_data method
            if df.Time.values > current_event.values:
                df.to_sql('BTCUSDT', engine, if_exists='append', index=False)
                current_event = df.Time
                print(df)
    
    def _transform_data(self, data):
        df = pd.DataFrame({'Time':data['E'], 'Price':data['k']['c']}, index=[0])
        df.Price = df.Price.astype(float)
        df.Time = pd.to_datetime(df.Time, unit='ms')
        return df
                          


if __name__ == "__main__":
    stream = StreamData('btcusdt')
    stream.main()