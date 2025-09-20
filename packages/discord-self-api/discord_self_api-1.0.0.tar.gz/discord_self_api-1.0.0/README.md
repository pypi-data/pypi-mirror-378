# Discord Selfbot API

⚠️ **WARNING**: Selfbots violate Discord's Terms of Service. Using selfbots may result in your account being terminated. This library is for educational purposes only. Use at your own risk.

A cross-platform Discord selfbot API wrapper that works on Termux and other platforms.

## Installation

```bash
pip install discord-selfbot-api
```
# Ouick Start

import asyncio
import os
from discord_selfbot import Client

# Get your Discord token (see instructions below)
TOKEN = os.getenv('DISCORD_TOKEN') or "your_token_here"

client = Client(TOKEN)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print("Selfbot is ready!")

async def main():
    await client.start()
    
    # Keep the client running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
    
# How to Get Your Discord Token

1. Open Discord in your web browser

2. Press F12 to open Developer Tools

3. Go to the Network tab

4. Reload the page and look for any request

5. Find the Authorization header in request headers

6. Copy the token (starts with letters)

▲ **Important:** Never share your token with anyone!

# Basic Usage Examples 

**Sending Messages**
  
  from discord_selfbot import Client

client = Client("your_token")

@client.event
async def on_ready():
    # Send a message to a channel
    channel_id = "1234567890"  # Replace with actual channel ID
    await client.send_message(channel_id, "Hello from selfbot!")

**Reading Messages**

@client.event
async def on_ready():
    # Get recent messages from a channel
    channel_id = "1234567890"
    messages = await client.get_messages(channel_id, limit=10)
    
    for message in messages:
        print(f"{message.author}: {message.content}")
        
**User Information**

@client.event
async def on_ready():
    # Get current user info
    user = await client.get_current_user()
    print(f"Username: {user.username}#{user.discriminator}")
    print(f"User ID: {user.id}")
    
    # Get user's servers
    guilds = await client.get_guilds()
    print(f"Joined {len(guilds)} servers")
 
# Advanced Examples 

**Autoresponder**

from discord_selfbot import Client

client = Client("your_token")

@client.event
async def on_ready():
    print("Auto responder started!")
    
    # Check messages periodically
    while True:
        channel_id = "1234567890"
        messages = await client.get_messages(channel_id, limit=5)
        
        for message in messages:
            if "hello" in message.content.lower():
                await client.send_message(channel_id, "Hello there!")
        
        await asyncio.sleep(30)  # Check every 30 seconds     
        
**Message Logger**

from datetime import datetime

@client.event
async def on_ready():
    print("Message logger started!")
    
    channels = ["1234567890", "0987654321"]  # Your channel IDs
    
    for channel_id in channels:
        messages = await client.get_messages(channel_id, limit=20)
        
        for message in messages:
            timestamp = datetime.fromisoformat(message.timestamp.replace('Z', '+00:00'))
            print(f"[{timestamp}] {message.author}: {message.content}")
            
# API References

**Client Class**

client = Client(token, intents=0)
await client.start()          # Start the client
await client.close()          # Close connections
await client.get_current_user()  # Get current user info
await client.get_guilds()     # Get user's servers     
**Message Methods**

await client.send_message(channel_id, content)      # Send message
await client.get_messages(channel_id, limit=50)     # Get messages
await client.edit_message(channel_id, message_id, new_content)  # Edit message
await client.delete_message(channel_id, message_id) # Delete message

**User Methods**

await client.get_current_user()     # Get current user
await client.modify_current_user(username="new_name")  # Change username   

# Common Issues

**Token Not Working**

Make sure you're using a user token, not bot token

Token should NOT start with "Bot "

Check if token has expired

**Rate Limiting**

The library handles basic rate limiting automatically

Avoid making too many requests too quickly
 
**Import Errors**

# If you get import errors, check installation
pip uninstall discord-selfbot-api
pip install discord-selfbot-api --upgrade

# Disclaimer

This project is for educational purposes only. I am not responsible for any actions taken against your Discord account for using selfbots. Use at your own risk.

# Support

**If you encounter issues:**

1. Check this README first

2. Ensure you're using the latest version

3. Verify your token is correct