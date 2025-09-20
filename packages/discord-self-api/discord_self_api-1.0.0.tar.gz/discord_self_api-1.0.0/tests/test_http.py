import pytest
import aiohttp
from unittest.mock import AsyncMock, patch
from discord_selfbot.http import HTTPClient

@pytest.mark.asyncio
async def test_http_client_initialization():
    """Test HTTP client initialization"""
    client = HTTPClient("test_token")
    assert client.token == "test_token"
    assert client.session is None
    assert "Mozilla" in client.user_agent

@pytest.mark.asyncio
async def test_http_request_success():
    """Test successful HTTP request"""
    with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'success': True})
        mock_request.return_value.__aenter__.return_value = mock_response
        
        client = HTTPClient("test_token")
        result = await client.request('GET', '/test')
        
        assert result == {'success': True}
        mock_request.assert_called_once()

@pytest.mark.asyncio
async def test_http_request_rate_limit():
    """Test HTTP request with rate limiting"""
    with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request, \
         patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        
        # First response: rate limited
        mock_response1 = AsyncMock()
        mock_response1.status = 429
        mock_response1.headers = {'Retry-After': '1'}
        
        # Second response: success
        mock_response2 = AsyncMock()
        mock_response2.status = 200
        mock_response2.json = AsyncMock(return_value={'success': True})
        
        mock_request.side_effect = [
            mock_response1.__aenter__(),
            mock_response2.__aenter__()
        ]
        
        client = HTTPClient("test_token")
        result = await client.request('GET', '/test')
        
        assert result == {'success': True}
        assert mock_request.call_count == 2
        mock_sleep.assert_called_once_with(1.0)

@pytest.mark.asyncio
async def test_http_methods():
    """Test HTTP convenience methods"""
    with patch('discord_selfbot.http.HTTPClient.request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {'success': True}
        
        client = HTTPClient("test_token")
        
        # Test GET
        await client.get('/test')
        mock_request.assert_called_with('GET', '/test')
        
        # Test POST
        await client.post('/test', json={'data': 'test'})
        mock_request.assert_called_with('POST', '/test', json={'data': 'test'})
        
        # Test PATCH
        await client.patch('/test', json={'data': 'test'})
        mock_request.assert_called_with('PATCH', '/test', json={'data': 'test'})
        
        # Test DELETE
        await client.delete('/test')
        mock_request.assert_called_with('DELETE', '/test')
        
        # Test PUT
        await client.put('/test', json={'data': 'test'})
        mock_request.assert_called_with('PUT', '/test', json={'data': 'test'})