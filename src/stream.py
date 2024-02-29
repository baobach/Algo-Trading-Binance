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
        self.test_net = test_net
        self.client = Client(self.api_key, self.secret_key, testnet=self.test_net)
        self.bsm = BinanceSocketManager(self.client)

    async def start_stream(self):
        symbol = self.symbol
        socket = self.bsm.kline_socket(symbol)
        engine = create_engine(f'sqlite:///data/raw/{symbol}_stream.db')
        current_event = pd.Series(pd.to_datetime(0))
        while True:
            await socket.__aenter__()
            msg = await socket.recv()
            await socket.__aexit__(None, None, None)
            df = self._transform_data(msg)
            if df.Time.values > current_event.values:
                await self._save_to_database(df, symbol, engine)
                current_event = df.Time
                print(df)

    async def _save_to_database(self, df, symbol, engine):
        df.to_sql(f'{symbol}', engine, if_exists='append', index=False)

    def _transform_data(self, data):
        df = pd.DataFrame({'Time':data['E'], 'Open':data['k']['o'], 'High':data['k']['h'], 'Low':data['k']['l'] ,'Close':data['k']['c'], 'Volume':data['k']['v']}, index=[0])
        df.Close = df.Close.astype(float)
        df.Open = df.Open.astype(float)
        df.High = df.High.astype(float)
        df.Low = df.Low.astype(float)
        df.Volume = df.Volume.astype(float)
        df.Time = pd.to_datetime(df.Time, unit='ms')
        return df                        

if __name__ == "__main__":
    stream = StreamData('BTCUSDT')
    asyncio.run(stream.start_stream())