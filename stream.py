import asyncio
import json
import os
from binance import AsyncClient, BinanceSocketManager
from config import settings

class StreamData:
    def __init__(self, symbol, data_folder='data', save_interval_seconds=60):
        self.api_key = settings.api_key
        self.api_secret = settings.secret_key
        self.symbol = symbol
        self.data_folder = data_folder
        self.save_interval_seconds = save_interval_seconds
        self.miniticker_socket_list = []

    async def start_streaming(self):
        # Create the 'data' folder if it doesn't exist
        os.makedirs(self.data_folder, exist_ok=True)

        # Create an AsyncClient
        self.client = await AsyncClient.create(api_key=self.api_key, api_secret=self.api_secret)

        # Create a BinanceSocketManager
        self.bm = BinanceSocketManager(self.client)

        # Start a miniticker socket for the specified symbol
        miniticker_socket = self.bm.symbol_miniticker_socket(self.symbol)

        try:
            # Start receiving messages
            async with miniticker_socket as kline_stream:
                while True:
                    # Receive kline data
                    kline_data = await kline_stream.recv()
                    print(f"{self.symbol} Kline Data:", kline_data)

                    # Append data to the list
                    self.miniticker_socket_list.append(kline_data)

                    # Check if it's time to save the data to the JSON file
                    if len(self.miniticker_socket_list) % (self.save_interval_seconds / 60) == 0:
                        asyncio.create_task(self.save_to_json())

                    # Sleep for a short duration before fetching the next data
                    await asyncio.sleep(60)

        except KeyboardInterrupt:
            # Handle KeyboardInterrupt to gracefully close the connection
            pass

        finally:
            # Close the connection
            await self.client.close_connection()

    async def save_to_json(self):
        # Save the list to a JSON file
        file_path = os.path.join(self.data_folder, f'{self.symbol}_stream.json')
        print("File Path:", file_path)
        with open(file_path, 'w') as json_file:
            json.dump(self.miniticker_socket_list, json_file)

if __name__ == "__main__":
    # Example usage
    symbol_streamer = SymbolStreamer(symbol='btcusdt')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(symbol_streamer.start_streaming())
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt to allow for a graceful exit
        pass
    finally:
        loop.close()
