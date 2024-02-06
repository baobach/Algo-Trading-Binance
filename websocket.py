import asyncio
import json
import os
from binance import AsyncClient
from config import settings

class WebSocket:
    def __init__(self, symbol, data_folder='data', trade_value_threshold=100_000_000):
        self.api_key = settings.api_key
        self.api_secret = settings.secret_key
        self.symbol = symbol
        self.data_folder = data_folder
        self.trade_value_threshold = trade_value_threshold
        self.total_dollar_value = 0
        self.current_trade = []

    async def start_streaming(self):
        # Create the 'data' folder if it doesn't exist
        os.makedirs(self.data_folder, exist_ok=True)

        # Create an AsyncClient
        self.client = await AsyncClient.create(api_key=self.api_key, api_secret=self.api_secret)

        try:
            # Start receiving kline data
            while True:
                kline_data = await self.get_kline_data()
                print(f"{self.symbol} Kline Data:", kline_data)

                # Compute the dollar value of the trade
                volume = float(kline_data[5])
                close_price = float(kline_data[4])
                dollar_value = volume * close_price

                # Add the dollar value of the current trade to the total dollar value
                self.total_dollar_value += dollar_value

                # Append data to the current trade
                self.current_trade.append({
                    "timestamp": kline_data[0],
                    "open": kline_data[1],
                    "high": kline_data[2],
                    "low": kline_data[3],
                    "close": kline_data[4],
                    "volume": kline_data[5]
                })

                # Check if the total dollar value exceeds the threshold
                if self.total_dollar_value >= self.trade_value_threshold:
                    # Save the current trade to a JSON file
                    await self.save_to_json(self.current_trade)

                    # Reset the total dollar value
                    self.total_dollar_value = 0
                    # Clear the current trade
                    self.current_trade.clear()

        except KeyboardInterrupt:
            # Handle KeyboardInterrupt to gracefully close the connection
            pass

        finally:
            # Close the connection
            await self.client.close_connection()

    async def get_kline_data(self):
        # Fetch 1-minute kline data for the specified symbol
        kline_data = await self.client.get_klines(symbol=self.symbol, interval=AsyncClient.KLINE_INTERVAL_1MINUTE)
        # Return the latest kline data
        return kline_data[-1]

    async def save_to_json(self, trade_data):
        # File path for the JSON file
        file_path = os.path.join(self.data_folder, f'{self.symbol}_stream.json')
        print("File Path:", file_path)

        # Check if the JSON file already exists
        if os.path.exists(file_path):
            # Load existing data from the JSON file
            with open(file_path, 'r') as json_file:
                existing_data = json.load(json_file)

            # Append only the latest trade data to the existing data
            existing_data.append(trade_data)

            # Write the combined data to the JSON file
            with open(file_path, 'w') as json_file:
                json.dump(existing_data, json_file)
        else:
            # If the file doesn't exist, create it and write the current data to it
            with open(file_path, 'w') as json_file:
                json.dump([trade_data], json_file)


if __name__ == "__main__":
    # Example usage
    symbol_streamer = WebSocket(symbol='BTCUSDT')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(symbol_streamer.start_streaming())
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt to allow for a graceful exit
        pass
    finally:
        loop.close()
