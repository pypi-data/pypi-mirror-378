import asyncio
from .http import HTTPClient
from .models import User, Message, Channel, Guild
from .gateway import Gateway

class Client:
    """
    Main client class for Discord selfbot functionality.
    
    Args:
        token (str): Your Discord user token
        intents (int): Gateway intents (default: 0)
    
    Example:
        >>> client = Client("your_token")
        >>> await client.start()
    
    Warning: Using selfbots may violate Discord's Terms of Service.
    """
    
    def __init__(self, token, intents=0):
        self.token = token
        self.http = HTTPClient(token)
        self.gateway = Gateway(token, intents)
        self.user = None
        self.guilds = []
        self.event_handlers = {}
        
    def event(self, func):
        """
        Decorator to register event handlers.
        
        Args:
            func: The event handler function
            
        Example:
            >>> @client.event
            >>> async def on_ready():
            >>>     print("Bot is ready!")
        """
        self.event_handlers[func.__name__] = func
        return func
        
    async def start(self):
        """Start the client with both HTTP and Gateway connections."""
        await self.http.init()
        self.user = await self.get_current_user()
        
        # Start gateway connection in background
        asyncio.create_task(self.gateway.connect())
        
        # Call on_ready event if defined
        if 'on_ready' in self.event_handlers:
            await self.event_handlers['on_ready']()
            
        return self
        
    async def close(self):
        """Close all connections."""
        await self.http.close()
        await self.gateway.close()
        
    async def get_current_user(self):
        """Get the current user information."""
        data = await self.http.get('/users/@me')
        return User(data)
        
    async def modify_current_user(self, username=None, avatar=None):
        """Modify the current user's profile."""
        payload = {}
        if username:
            payload['username'] = username
        if avatar:
            payload['avatar'] = avatar
            
        data = await self.http.patch('/users/@me', json=payload)
        return User(data)
        
    async def get_channel(self, channel_id):
        """Get a channel by ID."""
        data = await self.http.get(f'/channels/{channel_id}')
        return Channel(data)
        
    async def send_message(self, channel_id, content, **kwargs):
        """Send a message to a channel."""
        payload = {'content': content}
        payload.update(kwargs)
        
        data = await self.http.post(
            f'/channels/{channel_id}/messages',
            json=payload
        )
        return Message(data)
        
    async def edit_message(self, channel_id, message_id, content, **kwargs):
        """Edit a message."""
        payload = {'content': content}
        payload.update(kwargs)
        
        data = await self.http.patch(
            f'/channels/{channel_id}/messages/{message_id}',
            json=payload
        )
        return Message(data)
        
    async def delete_message(self, channel_id, message_id):
        """Delete a message."""
        await self.http.delete(f'/channels/{channel_id}/messages/{message_id}')
        
    async def get_messages(self, channel_id, limit=50):
        """Get messages from a channel."""
        data = await self.http.get(
            f'/channels/{channel_id}/messages',
            params={'limit': limit}
        )
        return [Message(msg) for msg in data]
        
    async def get_guilds(self):
        """Get user's guilds/servers."""
        data = await self.http.get('/users/@me/guilds')
        self.guilds = [Guild(guild) for guild in data]
        return self.guilds
        
    async def get_guild(self, guild_id):
        """Get a specific guild/server."""
        data = await self.http.get(f'/guilds/{guild_id}')
        return Guild(data)
        
    async def create_dm(self, user_id):
        """Create a DM channel with a user."""
        data = await self.http.post('/users/@me/channels', json={'recipient_id': user_id})
        return Channel(data)
        
    async def get_dms(self):
        """Get user's DM channels."""
        data = await self.http.get('/users/@me/channels')
        return [Channel(channel) for channel in data if channel['type'] == 1]