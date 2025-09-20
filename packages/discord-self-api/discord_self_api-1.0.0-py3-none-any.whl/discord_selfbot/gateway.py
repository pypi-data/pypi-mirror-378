import websockets
import asyncio
import json
import zlib
from .utils import is_termux  # IMPORT ADDED

class Gateway:
    def __init__(self, token, intents=0):
        self.token = token
        self.intents = intents
        self.ws = None
        self.sequence = None
        self.session_id = None
        self.heartbeat_interval = None
        
    async def connect(self):
        """Connect to Discord Gateway"""
        gateway_url = "wss://gateway.discord.gg/?v=9&encoding=json"
        
        try:
            self.ws = await websockets.connect(gateway_url)
            await self.identify()
            await self.listen()
        except Exception as e:
            print(f"Gateway connection failed: {e}")
            raise
            
    async def identify(self):
        """Send identify payload"""
        identify_payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": "linux" if is_termux() else "windows",
                    "$browser": "chrome",
                    "$device": "discord-selfbot"
                },
                "intents": self.intents
            }
        }
        
        await self.ws.send(json.dumps(identify_payload))
        
    async def listen(self):
        """Listen for events from gateway"""
        async for message in self.ws:
            data = json.loads(message)
            
            op = data.get('op')
            event_type = data.get('t')
            event_data = data.get('d')
            sequence = data.get('s')
            
            if sequence:
                self.sequence = sequence
                
            if op == 10:  # Hello
                self.heartbeat_interval = event_data['heartbeat_interval'] / 1000
                asyncio.create_task(self.heartbeat())
            elif op == 0:  # Dispatch
                await self.handle_event(event_type, event_data)
            elif op == 11:  # Heartbeat ACK
                pass  # Heartbeat acknowledged
                
    async def heartbeat(self):
        """Send heartbeat at regular intervals"""
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            heartbeat_payload = {
                "op": 1,
                "d": self.sequence
            }
            await self.ws.send(json.dumps(heartbeat_payload))
            
    async def handle_event(self, event_type, data):
        """Handle different gateway events"""
        if event_type == "READY":
            self.session_id = data['session_id']
            print("✅ Connected to Discord Gateway")
            print(f"📋 Session ID: {self.session_id}")
        elif event_type == "MESSAGE_CREATE":
            # Handle incoming messages
            print(f"📨 Message received: {data['content']}")
        elif event_type == "TYPING_START":
            print(f"✍️  User is typing in channel {data['channel_id']}")
            
    async def close(self):
        """Close the gateway connection"""
        if self.ws:
            await self.ws.close()
            print("🔌 Gateway connection closed")