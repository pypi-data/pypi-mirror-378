# RoQuick API - Python Wrapper

[![PyPI version](https://badge.fury.io/py/roquick-api.svg)](https://badge.fury.io/py/roquick-api)
[![Python Versions](https://img.shields.io/pypi/pyversions/roquick-api.svg)](https://pypi.org/project/roquick-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Discord](https://img.shields.io/discord/your-discord-server-id.svg?label=Discord&logo=Discord&colorB=7289da&style=flat)](https://discord.gg/GwxzWg9Cbh)

Official Python wrapper for the RoQuick API - The ultimate Roblox group management solution with advanced features for Discord bots and automation scripts.

## 🌟 Features

- **User & Group Information**: Fetch detailed user and group data
- **Role Management**: Advanced role assignment and bulk operations
- **Join Request Handling**: Accept/decline join requests with bulk support
- **Member Filtering**: Advanced member search and filtering
- **Premium Features**: Enhanced functionality with subscription
- **Error Handling**: Comprehensive error handling with detailed messages
- **Type Hints**: Full type hint support for better development experience
- **Async Support**: Built for high-performance applications

## 📋 Requirements

- Python 3.7+
- requests >= 2.25.0
- colorama >= 0.4.4

## 🚀 Installation

```bash
pip install roquick-api
```

## 🔑 Getting Started

### 1. Get Your API Key

1. Join our Discord server: [https://discord.gg/GwxzWg9Cbh](https://discord.gg/GwxzWg9Cbh)
2. Use the bot command: `/get-api-key`
3. Subscribe in the Roblox game for premium features

### 2. Basic Usage

```python
from roquick_api import RoQuick, RoQuickError

# Initialize the client
client = RoQuick({
    'apiKey': 'your-api-key-here'
})

try:
    # Get user information
    user = client.get_user_info('bluezly')
    print(f"User: {user['username']} (ID: {user['userId']})")
    
    # Get group information
    group = client.get_group_info(12345678)
    print(f"Group: {group['name']} ({group['memberCount']} members)")
    
    # Set user role
    result = client.set_user_role(12345678, 987654321, {
        'rank': 10  # or 'roleName': 'Moderator'
    })
    print("Role updated successfully!")
    
except RoQuickError as e:
    print(f"API Error: {e.message}")
    if e.status:
        print(f"Status Code: {e.status}")
```

## 📚 API Reference

### Client Initialization

```python
client = RoQuick(options)
```

**Parameters:**
- `options` (dict): Configuration options
  - `apiKey` (str): Your RoQuick API key

### User Methods

#### get_user_info(identifier)
Get user information by username or user ID.

```python
user = client.get_user_info('bluezly')  # or user ID: 123456789
```

**Returns:** Dict with user information including `userId`, `username`, `displayName`, etc.

### Group Methods

#### get_group_info(group_id)
Get detailed group information.

```python
group = client.get_group_info(12345678)
```

**Returns:** Dict with group information including `name`, `memberCount`, `roles`, etc.

#### get_group_roles(group_id)
Get all roles for a specific group.

```python
roles = client.get_group_roles(12345678)
```

#### get_group_members(group_id, options=None)
Get group members with optional filtering.

```python
members = client.get_group_members(12345678, {
    'limit': 100,
    'rank': 10,
    'roleName': 'Moderator'
})
```

**Options:**
- `limit` (int): Maximum number of members to return
- `cursor` (str): Pagination cursor
- `userId` (int): Filter by specific user ID
- `rank` (int): Filter by rank
- `roleName` (str): Filter by role name

### Role Management

#### set_user_role(group_id, user_id, options)
Set a user's role in a group.

```python
result = client.set_user_role(12345678, 987654321, {
    'rank': 10  # or 'roleName': 'Moderator'
})
```

#### bulk_set_user_role(group_id, users, options)
Set role for multiple users in bulk.

```python
result = client.bulk_set_user_role(12345678, [111, 222, 333], {
    'rank': 5
})
```

### Join Request Management

#### get_join_requests(group_id, options=None)
Get pending join requests for a group.

```python
requests = client.get_join_requests(12345678, {
    'limit': 50
})
```

#### accept_join_request(group_id, user_id)
Accept a join request.

```python
result = client.accept_join_request(12345678, 987654321)
```

#### decline_join_request(group_id, user_id)
Decline a join request.

```python
result = client.decline_join_request(12345678, 987654321)
```

#### bulk_join_request_action(group_id, users, action)
Perform bulk action on join requests.

```python
result = client.bulk_join_request_action(12345678, [111, 222, 333], 'accept')
```

### Utility Methods

#### set_open_cloud_key(open_key)
Set Open Cloud API key for enhanced features.

```python
result = client.set_open_cloud_key('your-open-cloud-key')
```

#### get_api_key_status()
Get API key status and subscription information.

```python
status = client.get_api_key_status()
print(f"Subscription: {status['subscription']['tier']}")
```

## 🔧 Error Handling

The package includes comprehensive error handling with the `RoQuickError` exception:

```python
from roquick_api import RoQuickError

try:
    user = client.get_user_info('invalid-user')
except RoQuickError as e:
    print(f"Error: {e.message}")
    print(f"Status: {e.status}")
    
    # Handle specific error types
    if e.status == 401:
        print("Invalid API key")
    elif e.status == 402:
        print("Subscription required")
    elif e.status == 404:
        print("User/Group not found")
    elif e.status == 429:
        print("Rate limited")
```

## 💎 Premium Features

Unlock advanced features with a subscription:

- Higher rate limits
- Bulk operations
- Priority support
- Advanced filtering options
- Enhanced error reporting

Subscribe in our Roblox game or contact us on Discord!

## 🐛 Troubleshooting

### Common Issues

1. **Invalid API Key**: Join our Discord and use `/get-api-key`
2. **Rate Limiting**: Upgrade your subscription or wait between requests
3. **Permission Errors**: Ensure your Roblox account has the necessary group permissions
4. **Network Issues**: Check your internet connection and firewall settings

### Getting Help

- 📞 **Discord Support**: [https://discord.gg/GwxzWg9Cbh](https://discord.gg/GwxzWg9Cbh)
- 📧 **Email**: hotelc229@gmail.com
- 🐛 **Bug Reports**: Create an issue on GitHub

## 📝 Examples

### Discord Bot Integration

```python
import discord
from discord.ext import commands
from roquick_api import RoQuick, RoQuickError

bot = commands.Bot(command_prefix='!')
roquick = RoQuick({'apiKey': 'your-api-key'})

@bot.command()
async def promote(ctx, user_id: int, rank: int):
    try:
        result = roquick.set_user_role(12345678, user_id, {'rank': rank})
        await ctx.send(f"✅ User promoted to rank {rank}")
    except RoQuickError as e:
        await ctx.send(f"❌ Error: {e.message}")

bot.run('your-bot-token')
```

### Bulk Role Assignment

```python
# Promote multiple users to moderator rank
moderator_candidates = [111111111, 222222222, 333333333]

try:
    result = client.bulk_set_user_role(12345678, moderator_candidates, {
        'roleName': 'Moderator'
    })
    
    successful = len([r for r in result['results'] if r['success']])
    print(f"Successfully promoted {successful}/{len(moderator_candidates)} users")
    
except RoQuickError as e:
    print(f"Bulk promotion failed: {e.message}")
```

### Join Request Management

```python
# Auto-accept all pending join requests
try:
    requests = client.get_join_requests(12345678)
    user_ids = [req['user']['userId'] for req in requests['groupJoinRequests']]
    
    if user_ids:
        result = client.bulk_join_request_action(12345678, user_ids, 'accept')
        print(f"Accepted {len(user_ids)} join requests")
    else:
        print("No pending join requests")
        
except RoQuickError as e:
    print(f"Error processing join requests: {e.message}")
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI Package**: [https://pypi.org/project/roquick-api/](https://pypi.org/project/roquick-api/)
- **Discord Server**: [https://discord.gg/GwxzWg9Cbh](https://discord.gg/GwxzWg9Cbh)
- **Roblox Game**: [Game link](https://www.roblox.com/games/127538764147530)

---

Made with ❤️ by the RoQuick team. Join our Discord for support and updates!
