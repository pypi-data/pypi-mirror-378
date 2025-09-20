class User:
    def __init__(self, data):
        self.id = data.get('id')
        self.username = data.get('username')
        self.discriminator = data.get('discriminator')
        self.avatar = data.get('avatar')
        self.bot = data.get('bot', False)
        self.email = data.get('email')
        self.verified = data.get('verified', False)
        self.mfa_enabled = data.get('mfa_enabled', False)
        
    def __str__(self):
        return f"{self.username}#{self.discriminator}"
        
class Message:
    def __init__(self, data):
        self.id = data.get('id')
        self.channel_id = data.get('channel_id')
        self.guild_id = data.get('guild_id')
        self.content = data.get('content')
        self.author = User(data['author']) if 'author' in data else None
        self.timestamp = data.get('timestamp')
        self.edited_timestamp = data.get('edited_timestamp')
        self.attachments = data.get('attachments', [])
        self.embeds = data.get('embeds', [])
        self.mentions = [User(mention) for mention in data.get('mentions', [])]
        
    def __str__(self):
        return f"Message({self.id}: {self.content})"
        
class Channel:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.type = data.get('type')
        self.guild_id = data.get('guild_id')
        self.position = data.get('position')
        self.topic = data.get('topic')
        self.nsfw = data.get('nsfw', False)
        
    def __str__(self):
        return f"Channel({self.id}: {self.name})"
        
class Guild:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.icon = data.get('icon')
        self.owner_id = data.get('owner_id')
        self.region = data.get('region')
        self.member_count = data.get('member_count')
        
    def __str__(self):
        return f"Guild({self.id}: {self.name})"