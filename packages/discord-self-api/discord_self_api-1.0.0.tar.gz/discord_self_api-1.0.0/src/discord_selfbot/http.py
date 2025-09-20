import aiohttp
import asyncio
import json
from .utils import get_user_agent, create_session, validate_token

class HTTPClient:
    def __init__(self, token):
        self.token = validate_token(token)
        self.session = None
        self.user_agent = get_user_agent()
        self.base_url = "https://discord.com/api/v9"
        
    async def init(self):
        self.session = create_session()
        
    async def close(self):
        if self.session:
            await self.session.close()
            
    async def request(self, method, endpoint, **kwargs):
        if not self.session:
            await self.init()
            
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            'Authorization': self.token,
            'User-Agent': self.user_agent,
            'Content-Type': 'application/json'
        }
        
        # Add custom headers if provided
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
            
        # Handle different data types
        if 'json' in kwargs:
            kwargs['data'] = json.dumps(kwargs.pop('json'))
            
        try:
            async with self.session.request(method, url, headers=headers, **kwargs) as response:
                # Check for rate limits
                if response.status == 429:
                    retry_after = float(response.headers.get('Retry-After', 1))
                    print(f"Rate limited. Retrying after {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    return await self.request(method, endpoint, **kwargs)
                    
                # Handle other errors
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"HTTP Error {response.status}: {error_text}")
                
                # Try to parse JSON, return text if it fails
                try:
                    data = await response.json()
                    return data
                except:
                    return await response.text()
        except Exception as e:
            print(f"HTTP request failed: {e}")
            raise
            
    async def get(self, endpoint, **kwargs):
        return await self.request('GET', endpoint, **kwargs)
        
    async def post(self, endpoint, **kwargs):
        return await self.request('POST', endpoint, **kwargs)
        
    async def patch(self, endpoint, **kwargs):
        return await self.request('PATCH', endpoint, **kwargs)
        
    async def delete(self, endpoint, **kwargs):
        return await self.request('DELETE', endpoint, **kwargs)
        
    async def put(self, endpoint, **kwargs):
        return await self.request('PUT', endpoint, **kwargs)