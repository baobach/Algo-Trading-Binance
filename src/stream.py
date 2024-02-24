import websockets
import asyncio
import json

class StreamData:
    def __init__(self, symbol):
        self.symbol = symbol
        self.websocket_url = f'wss://stream.binance.com:9443/ws/{symbol.lower()}@trade'

    async def handle_socket_message(self, msg):
        data = json.loads(msg)
        print(data)

    async def connect_to_websocket(self):
        async with websockets.connect(self.websocket_url) as websocket:
            while True:
                message = await websocket.recv()
                await self.handle_socket_message(message)

    def start_streaming(self):
        asyncio.run(self.connect_to_websocket())
        
if __name__ == "__main__":
    symbol = 'BTCUSDT'
    stream = StreamData(symbol)
    stream.start_streaming()