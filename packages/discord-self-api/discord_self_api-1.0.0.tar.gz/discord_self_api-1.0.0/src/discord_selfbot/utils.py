import sys
import platform
import aiohttp
import asyncio
import os

def is_termux():
    """Check if running on Termux"""
    return 'termux' in sys.executable or ('ANDROID_ROOT' in os.environ and 'com.termux' in os.environ)

def get_user_agent():
    """Get appropriate user agent for the platform that mimics official client"""
    system = platform.system()
    if is_termux():
        return "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36"
    else:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def create_session():
    """Create a session with appropriate configuration for selfbot"""
    if is_termux():
        # Termux might need different SSL configuration
        connector = aiohttp.TCPConnector(ssl=False)
    else:
        connector = aiohttp.TCPConnector()
    
    return aiohttp.ClientSession(connector=connector)

def validate_token(token):
    """Validate if token looks like a user token"""
    if token.startswith("Bot "):
        raise ValueError("This is a bot token. Selfbots require user account tokens.")
    return token