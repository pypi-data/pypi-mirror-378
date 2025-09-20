import pytest
from discord_selfbot.models import User, Message, Channel, Guild

def test_user_model():
    """Test User model creation"""
    user_data = {
        'id': '1234567890',
        'username': 'testuser',
        'discriminator': '1234',
        'avatar': 'test_avatar',
        'bot': False,
        'email': 'test@example.com',
        'verified': True,
        'mfa_enabled': False
    }
    
    user = User(user_data)
    
    assert user.id == '1234567890'
    assert user.username == 'testuser'
    assert user.discriminator == '1234'
    assert user.avatar == 'test_avatar'
    assert user.bot is False
    assert user.email == 'test@example.com'
    assert user.verified is True
    assert user.mfa_enabled is False
    assert str(user) == 'testuser#1234'

def test_message_model():
    """Test Message model creation"""
    message_data = {
        'id': '9876543210',
        'channel_id': '1111111111',
        'guild_id': '2222222222',
        'content': 'Hello world!',
        'author': {
            'id': '1234567890',
            'username': 'testuser',
            'discriminator': '1234',
            'avatar': None,
            'bot': False
        },
        'timestamp': '2023-01-01T00:00:00.000000+00:00',
        'edited_timestamp': None,
        'attachments': [],
        'embeds': [],
        'mentions': []
    }
    
    message = Message(message_data)
    
    assert message.id == '9876543210'
    assert message.channel_id == '1111111111'
    assert message.guild_id == '2222222222'
    assert message.content == 'Hello world!'
    assert message.author is not None
    assert message.author.username == 'testuser'
    assert str(message) == 'Message(9876543210: Hello world!)'

def test_channel_model():
    """Test Channel model creation"""
    channel_data = {
        'id': '1111111111',
        'name': 'general',
        'type': 0,
        'guild_id': '2222222222',
        'position': 1,
        'topic': 'General discussion',
        'nsfw': False
    }
    
    channel = Channel(channel_data)
    
    assert channel.id == '1111111111'
    assert channel.name == 'general'
    assert channel.type == 0
    assert channel.guild_id == '2222222222'
    assert channel.position == 1
    assert channel.topic == 'General discussion'
    assert channel.nsfw is False
    assert str(channel) == 'Channel(1111111111: general)'

def test_guild_model():
    """Test Guild model creation"""
    guild_data = {
        'id': '2222222222',
        'name': 'Test Guild',
        'icon': 'test_icon',
        'owner_id': '1234567890',
        'region': 'us-west',
        'member_count': 100
    }
    
    guild = Guild(guild_data)
    
    assert guild.id == '2222222222'
    assert guild.name == 'Test Guild'
    assert guild.icon == 'test_icon'
    assert guild.owner_id == '1234567890'
    assert guild.region == 'us-west'
    assert guild.member_count == 100
    assert str(guild) == 'Guild(2222222222: Test Guild)'