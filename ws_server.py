import asyncio
import websockets
import json
from photon128 import photon128

class WebSocketHashServer:
    def __init__(self):
        self.clients = set()
        self.messages = []

    async def register(self, websocket):
        self.clients.add(websocket)
        await websocket.send(json.dumps({
            'type': 'history',
            'messages': self.messages
        }))

    async def unregister(self, websocket):
        self.clients.remove(websocket)

    async def broadcast(self, message, sender=None):
        for client in self.clients:
            if client != sender:
                try:
                    await client.send(message)
                except:
                    await self.unregister(client)

    async def handle_message(self, websocket, message):
        data = json.loads(message)
        
        if data['type'] == 'message':
            hash_value = photon128(data['message'].encode('utf-8'))
            
            message_data = {
                'type': 'message',
                'message': data['message'],
                'hash': hash_value.hex(),
                'timestamp': data.get('timestamp', '')
            }
            
            self.messages.append(message_data)
            
            await self.broadcast(json.dumps(message_data), websocket)
        
        elif data['type'] == 'request_history':
            await websocket.send(json.dumps({
                'type': 'history',
                'messages': self.messages
            }))

    async def handler(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        finally:
            await self.unregister(websocket)

async def main():
    server = WebSocketHashServer()
    async with websockets.serve(server.handler, "localhost", 8765):
        await asyncio.Future()  

if __name__ == "__main__":
    asyncio.run(main())