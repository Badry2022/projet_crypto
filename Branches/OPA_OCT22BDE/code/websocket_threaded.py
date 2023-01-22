from threading import Thread
import asyncio
import websockets
import ssl

context = ssl._create_unverified_context()

class WebsocketThreaded(Thread):
    def __init__(self, url, callback):
        self._url = url
        self._callback = callback
        super().__init__()
    
    def stop(self):
        self._status = False
    
    def start(self):
        self._status = True
        super().start()

    def run(self):
        async def ws_loop(self):
            async with websockets.connect(self._url, ssl=context) as websocket:
                while self._status:
                    received = await websocket.recv()
                    self._callback(received)

        asyncio.run(ws_loop(self))
