"""
discord_selfbot - A cross-platform Discord selfbot API wrapper

This package provides a Python interface for Discord user accounts (selfbots).
It supports both HTTP API calls and real-time events via WebSocket.

Warning: Selfbots violate Discord's Terms of Service. Use at your own risk.

Example:
    >>> from discord_selfbot import Client
    >>> client = Client("your_token")
    >>> await client.start()

Version: 1.0.0
Author: Zombie
License: MIT
"""

from .client import Client
from .models import User, Message, Channel, Guild

__version__ = "1.0.0"
__author__ = "Zombie"
__license__ = "MIT"

__all__ = ['Client', 'User', 'Message', 'Channel', 'Guild']
