import pytest
import sys
from unittest.mock import patch
from discord_selfbot.utils import is_termux, get_user_agent, validate_token

def test_is_termux(monkeypatch):
    """Test Termux detection"""
    # Test when running in Termux
    with patch('sys.executable', '/data/data/com.termux/files/usr/bin/python'):
        assert is_termux() is True
    
    # Test when ANDROID_ROOT is set and contains termux
    with patch.dict('os.environ', {'ANDROID_ROOT': '/data/data/com.termux'}):
        assert is_termux() is True
    
    # Test when not in Termux
    with patch('sys.executable', '/usr/bin/python3'), \
         patch.dict('os.environ', {}, clear=True):
        assert is_termux() is False

def test_get_user_agent(monkeypatch):
    """Test user agent generation"""
    # Test Termux user agent
    with patch('discord_selfbot.utils.is_termux', return_value=True):
        user_agent = get_user_agent()
        assert "Mozilla" in user_agent
        assert "Android" in user_agent
    
    # Test non-Termux user agent
    with patch('discord_selfbot.utils.is_termux', return_value=False):
        user_agent = get_user_agent()
        assert "Mozilla" in user_agent
        assert "Windows" in user_agent

def test_validate_token():
    """Test token validation"""
    # Valid user token
    user_token = "NDczNzQ4MjI1MTA2MjU4NDIw.Gq7e4B.7qCqCqCqCqCqCqCqCqCqCqCqCqCqCqCqCqCqCqCqC"
    assert validate_token(user_token) == user_token
    
    # Bot token should raise error
    bot_token = "Bot NDczNzQ4MjI1MTA2MjU4NDIw.Gq7e4B.7qCqCqCqCqCqCqCqCqCqCqCqCqCqCqCqCqCqCqC"
    with pytest.raises(ValueError, match="This is a bot token"):
        validate_token(bot_token)