"""
RoQuick API - Main module containing the RoQuick class and RoQuickError exception.
"""

import requests
import json
import random
import time
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlencode
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Package information - moved here to avoid circular import
PACKAGE_INFO = {
    "name": "roquick-api",
    "version": "0.0.3b0",
    "description": "Official RoQuick API wrapper for Roblox group management with advanced features",
    "author": "bluezly",
    "email": "hotelc229@gmail.com",
    "license": "MIT",
    "discord": "https://discord.gg/GwxzWg9Cbh",
    "keywords": ["roblox", "api", "group", "management", "roquick", "discord", "bot"],
}


class RoQuickError(Exception):
    """Custom exception class for RoQuick API errors."""
    
    def __init__(self, message: str, status: Optional[int] = None):
        """
        Initialize RoQuickError.
        
        Args:
            message (str): Error message
            status (int, optional): HTTP status code
        """
        super().__init__(message)
        self.message = message
        self.status = status
        self.name = 'RoQuickError'


class RoQuick:
    """
    Official RoQuick API wrapper for Roblox group management.
    
    This class provides comprehensive methods for managing Roblox groups including
    user information, group details, role management, member management, and
    join request handling.
    """
    
    def __init__(self, options: Dict[str, Any]):
        """
        Initialize RoQuick API client.
        
        Args:
            options (dict): Configuration options containing 'apiKey'
            
        Raises:
            RoQuickError: If API key is not provided
        """
        if not options or not options.get('apiKey'):
            print(f"{Fore.RED}{Style.BRIGHT}RoQuick Error: API Key is required!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{Style.BRIGHT}How to get API Key:{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}   1. Join Discord: {Fore.CYAN}{PACKAGE_INFO['discord']}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}   2. Use the bot command: /get-api-key{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}   3. Subscribe in Roblox game for features{Style.RESET_ALL}")
            raise RoQuickError(f'API Key is required! Join Discord to get one: {PACKAGE_INFO["discord"]}')

        self.api_key = options['apiKey']
        self.base_url = 'https://api.roqu.exid.me'
        self.version = PACKAGE_INFO['version']
        self.timeout = 25

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': f'roquick-api-python v{self.version}'
        })

        self.show_welcome_message()
        self.check_version()

    def show_welcome_message(self):
        """Display welcome message with package information."""
        print(f"{Fore.CYAN}{Style.BRIGHT}RoQuick API v{self.version}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}Official Roblox API Wrapper{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Successfully initialized RoQuick API{Style.RESET_ALL}")
        
        tips = [
            f"Join Discord for support: {PACKAGE_INFO['discord']}",
            f"Check examples and documentation in Discord: {PACKAGE_INFO['discord']}",
        ]
        
        random_tip = random.choice(tips)
        print(f"{Fore.LIGHTBLACK_EX}Tip:{Style.RESET_ALL} {Fore.CYAN}{random_tip}{Style.RESET_ALL}")
        print()

    def check_version(self):
        """Check for package updates and display version information."""
        try:
            response = requests.get('https://pypi.org/pypi/roquick-api/json', timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data['info']['version']
                current_version = self.version
                
                def parse_version(version):
                    # Handle beta versions like "0.0.1b0"
                    if 'b' in version:
                        main_version, beta = version.split('b')
                        return tuple(map(int, main_version.split('.'))) + (int(beta),)
                    return tuple(map(int, version.split('.')))
                
                current_parsed = parse_version(current_version)
                latest_parsed = parse_version(latest_version)
                
                if latest_parsed > current_parsed:
                    # Calculate version difference
                    version_diff = sum((l - c) * (100 ** (len(latest_parsed) - i - 1)) 
                                     for i, (l, c) in enumerate(zip(latest_parsed, current_parsed)))
                    
                    if version_diff >= 35:
                        print(f"{Fore.RED}{Style.BRIGHT}CRITICAL: Your RoQuick version is extremely outdated!{Style.RESET_ALL}")
                        print(f"{Fore.RED}Current: v{current_version} | Latest: v{latest_version}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}Update required! Run: pip install --upgrade roquick-api{Style.RESET_ALL}")
                        raise RoQuickError(f"Version too old! Current: v{current_version}, Required: v{latest_version}. Update with: pip install --upgrade roquick-api")
                    else:
                        print(f"{Fore.YELLOW}New version available: v{latest_version} (you have v{current_version}){Style.RESET_ALL}")
                        print(f"{Fore.LIGHTBLACK_EX}Update with: pip install --upgrade roquick-api{Style.RESET_ALL}")
        except Exception as error:
            if isinstance(error, RoQuickError):
                raise error
            # Silently ignore version check errors

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to RoQuick API.
        
        Args:
            method (str): HTTP method (GET, POST, PATCH, PUT, DELETE)
            endpoint (str): API endpoint
            data (dict, optional): Request data for POST/PATCH/PUT requests
            
        Returns:
            dict: API response data
            
        Raises:
            RoQuickError: For various API errors
        """
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=self.timeout)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data, timeout=self.timeout)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=self.timeout)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=self.timeout)
            else:
                raise RoQuickError(f"Unsupported HTTP method: {method}")
            
            if response.status_code >= 200 and response.status_code < 300:
                try:
                    return response.json()
                except ValueError:
                    return {"success": True, "message": "Request completed successfully"}
            
            # Handle error responses
            status = response.status_code
            try:
                error_data = response.json()
                message = error_data.get('error') or error_data.get('message') or response.text
            except ValueError:
                message = response.text or f"HTTP {status} Error"
            
            if status == 400:
                print(f"{Fore.RED}Bad Request: {message}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}Check your request parameters and data format{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Join Discord for help: {Fore.CYAN}{PACKAGE_INFO['discord']}{Style.RESET_ALL}")
            elif status in [401, 403]:
                print(f"{Fore.RED}Authentication Error: {message}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Join Discord to get valid API key: {Fore.CYAN}{PACKAGE_INFO['discord']}{Style.RESET_ALL}")
            elif status == 402:
                print(f"{Fore.YELLOW}Subscription Required: {message}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}Subscribe in Roblox game for premium features{Style.RESET_ALL}")
            elif status == 429:
                print(f"{Fore.YELLOW}Rate Limited: {message}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}Wait a moment or upgrade your subscription{Style.RESET_ALL}")
            elif status == 404:
                print(f"{Fore.RED}Not Found: {message}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}Check if the group/user ID exists{Style.RESET_ALL}")
            
            raise RoQuickError(message, status)
            
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}Connection Error: Cannot reach RoQuick API{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}Check your internet connection or try again later{Style.RESET_ALL}")
            raise RoQuickError('Cannot connect to RoQuick API', 500)
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}Timeout Error: Request took too long{Style.RESET_ALL}")
            raise RoQuickError('Request timeout', 408)
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Request Error: {str(e)}{Style.RESET_ALL}")
            raise RoQuickError(str(e), 500)

    def get_user_info(self, identifier: Union[str, int]) -> Dict[str, Any]:
        """
        Get user information by username or user ID.
        
        Args:
            identifier (str|int): Username or user ID
            
        Returns:
            dict: User information including userId, username, displayName, etc.
            
        Raises:
            RoQuickError: If identifier is not provided or user not found
        """
        if not identifier:
            raise RoQuickError('User identifier is required')
        
        print(f"{Fore.LIGHTBLACK_EX}Fetching user info for: {identifier}{Style.RESET_ALL}")
        result = self.make_request('GET', f'/api/users/{identifier}')
        print(f"{Fore.GREEN}Found user: {result['username']} ({result['userId']}){Style.RESET_ALL}")
        return result

    def get_group_info(self, group_id: Union[str, int]) -> Dict[str, Any]:
        """
        Get group information by group ID.
        
        Args:
            group_id (str|int): Group ID
            
        Returns:
            dict: Group information including name, memberCount, roles, etc.
            
        Raises:
            RoQuickError: If group_id is not provided or group not found
        """
        if not group_id:
            raise RoQuickError('Group ID is required')
        
        print(f"{Fore.LIGHTBLACK_EX}Fetching group info for: {group_id}{Style.RESET_ALL}")
        result = self.make_request('GET', f'/api/groups/{group_id}')
        roles_count = len(result.get('roles', []))
        print(f"{Fore.GREEN}Group: {result['name']} ({result['memberCount']} members, {roles_count} roles){Style.RESET_ALL}")
        return result

    def get_group_roles(self, group_id: Union[str, int]) -> Dict[str, Any]:
        """
        Get all roles for a specific group.
        
        Args:
            group_id (str|int): Group ID
            
        Returns:
            dict: Group roles information
            
        Raises:
            RoQuickError: If group_id is not provided
        """
        if not group_id:
            raise RoQuickError('Group ID is required')
        
        print(f"{Fore.LIGHTBLACK_EX}Fetching roles for group: {group_id}{Style.RESET_ALL}")
        result = self.make_request('GET', f'/api/groups/{group_id}/roles')
        roles_count = len(result.get('roles', []))
        print(f"{Fore.GREEN}Found {roles_count} roles{Style.RESET_ALL}")
        return result

    def get_group_members(self, group_id: Union[str, int], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get group members with optional filtering.
        
        Args:
            group_id (str|int): Group ID
            options (dict, optional): Filtering options including:
                - limit (int): Maximum number of members to return
                - cursor (str): Pagination cursor
                - userId (int): Filter by specific user ID
                - rank (int): Filter by rank
                - roleName (str): Filter by role name
                
        Returns:
            dict: Group members information
            
        Raises:
            RoQuickError: If group_id is not provided
        """
        if not group_id:
            raise RoQuickError('Group ID is required')
        
        if options is None:
            options = {}
        
        params = {}
        for key in ['limit', 'cursor', 'userId', 'rank', 'roleName']:
            if key in options and options[key] is not None:
                params[key] = str(options[key])
        
        query_string = f"?{urlencode(params)}" if params else ""
        url = f'/api/groups/{group_id}/members{query_string}'
        
        print(f"{Fore.LIGHTBLACK_EX}Fetching group members...{Style.RESET_ALL}")
        result = self.make_request('GET', url)
        members_count = len(result.get('groupMemberships', []))
        print(f"{Fore.GREEN}Found {members_count} members{Style.RESET_ALL}")
        return result

    def set_user_role(self, group_id: Union[str, int], user_id: Union[str, int], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set a user's role in a group.
        
        Args:
            group_id (str|int): Group ID
            user_id (str|int): User ID
            options (dict): Role options containing either:
                - rank (int): Target rank
                - roleName (str): Target role name
                
        Returns:
            dict: Updated role information
            
        Raises:
            RoQuickError: If required parameters are missing
        """
        if not group_id or not user_id:
            raise RoQuickError('Group ID and User ID are required')
        
        if not options.get('rank') and not options.get('roleName'):
            raise RoQuickError('Either rank or roleName is required')
        
        print(f"{Fore.LIGHTBLACK_EX}Setting role for user {user_id} in group {group_id}...{Style.RESET_ALL}")
        
        request_data = {}
        if options.get('rank'):
            request_data['rank'] = options['rank']
        if options.get('roleName'):
            request_data['roleName'] = options['roleName']
        
        result = self.make_request('PATCH', f'/api/groups/{group_id}/members/{user_id}/role', request_data)
        
        updated_role = result.get('updatedRole', {})
        role_name = updated_role.get('name', 'Unknown')
        role_rank = updated_role.get('rank', 'Unknown')
        print(f"{Fore.GREEN}Role updated: {role_name} (Rank {role_rank}){Style.RESET_ALL}")
        return result

    def bulk_set_user_role(self, group_id: Union[str, int], users: List[Union[str, int]], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set role for multiple users in bulk.
        
        Args:
            group_id (str|int): Group ID
            users (list): List of user IDs
            options (dict): Role options containing either:
                - rank (int): Target rank
                - roleName (str): Target role name
                
        Returns:
            dict: Bulk operation results
            
        Raises:
            RoQuickError: If required parameters are missing
        """
        if not group_id or not users or not isinstance(users, list) or len(users) == 0:
            raise RoQuickError('Group ID and users array are required')
        
        if not options.get('rank') and not options.get('roleName'):
            raise RoQuickError('Either rank or roleName is required')
        
        print(f"{Fore.LIGHTBLACK_EX}Bulk setting roles for {len(users)} users...{Style.RESET_ALL}")
        
        request_data = {'users': users}
        if options.get('rank'):
            request_data['rank'] = options['rank']
        if options.get('roleName'):
            request_data['roleName'] = options['roleName']
        
        result = self.make_request('PATCH', f'/api/groups/{group_id}/members/bulk-role', request_data)
        
        results = result.get('results', [])
        success_count = len([r for r in results if r.get('success')])
        fail_count = len(results) - success_count
        
        print(f"{Fore.GREEN}Bulk role update complete: {success_count} success, {fail_count} failed{Style.RESET_ALL}")
        
        target_role = result.get('targetRole')
        if target_role:
            print(f"{Fore.LIGHTBLACK_EX}Target role: {target_role['name']} (Rank {target_role['rank']}){Style.RESET_ALL}")
        
        return result

    def get_join_requests(self, group_id: Union[str, int], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get pending join requests for a group.
        
        Args:
            group_id (str|int): Group ID
            options (dict, optional): Options including:
                - limit (int): Maximum number of requests to return
                - cursor (str): Pagination cursor
                - userId (int): Filter by specific user ID
                
        Returns:
            dict: Join requests information
            
        Raises:
            RoQuickError: If group_id is not provided
        """
        if not group_id:
            raise RoQuickError('Group ID is required')
        
        if options is None:
            options = {}
        
        params = {}
        for key in ['limit', 'cursor', 'userId']:
            if key in options and options[key] is not None:
                params[key] = str(options[key])
        
        query_string = f"?{urlencode(params)}" if params else ""
        url = f'/api/groups/{group_id}/join-requests{query_string}'
        
        print(f"{Fore.LIGHTBLACK_EX}Fetching join requests for group {group_id}...{Style.RESET_ALL}")
        result = self.make_request('GET', url)
        requests_count = len(result.get('groupJoinRequests', []))
        print(f"{Fore.GREEN}Found {requests_count} join requests{Style.RESET_ALL}")
        return result

    def accept_join_request(self, group_id: Union[str, int], user_id: Union[str, int]) -> Dict[str, Any]:
        """
        Accept a join request for a user.
        
        Args:
            group_id (str|int): Group ID
            user_id (str|int): User ID
            
        Returns:
            dict: Operation result
            
        Raises:
            RoQuickError: If required parameters are missing
        """
        if not group_id or not user_id:
            raise RoQuickError('Group ID and User ID are required')
        
        print(f"{Fore.LIGHTBLACK_EX}Accepting join request for user {user_id}...{Style.RESET_ALL}")
        result = self.make_request('POST', f'/api/groups/{group_id}/join-requests/{user_id}/accept')
        print(f"{Fore.GREEN}Join request accepted{Style.RESET_ALL}")
        return result

    def decline_join_request(self, group_id: Union[str, int], user_id: Union[str, int]) -> Dict[str, Any]:
        """
        Decline a join request for a user.
        
        Args:
            group_id (str|int): Group ID
            user_id (str|int): User ID
            
        Returns:
            dict: Operation result
            
        Raises:
            RoQuickError: If required parameters are missing
        """
        if not group_id or not user_id:
            raise RoQuickError('Group ID and User ID are required')
        
        print(f"{Fore.LIGHTBLACK_EX}Declining join request for user {user_id}...{Style.RESET_ALL}")
        result = self.make_request('POST', f'/api/groups/{group_id}/join-requests/{user_id}/decline')
        print(f"{Fore.GREEN}Join request declined{Style.RESET_ALL}")
        return result

    def bulk_join_request_action(self, group_id: Union[str, int], users: List[Union[str, int]], action: str) -> Dict[str, Any]:
        """
        Perform bulk action on join requests.
        
        Args:
            group_id (str|int): Group ID
            users (list): List of user IDs
            action (str): Action to perform ('accept' or 'decline')
            
        Returns:
            dict: Bulk operation results
            
        Raises:
            RoQuickError: If required parameters are missing or invalid
        """
        if not group_id or not users or not isinstance(users, list) or len(users) == 0:
            raise RoQuickError('Group ID and users array are required')
        
        if action not in ['accept', 'decline']:
            raise RoQuickError('Action must be "accept" or "decline"')
        
        print(f"{Fore.LIGHTBLACK_EX}Bulk {action}ing {len(users)} join requests...{Style.RESET_ALL}")
        result = self.make_request('POST', f'/api/groups/{group_id}/join-requests/bulk/{action}', {'users': users})
        
        results = result.get('results', [])
        success_count = len([r for r in results if r.get('success')])
        fail_count = len(results) - success_count
        
        print(f"{Fore.GREEN}Bulk {action} complete: {success_count} success, {fail_count} failed{Style.RESET_ALL}")
        return result

    def set_open_cloud_key(self, open_key: str) -> Dict[str, Any]:
        """
        Set Open Cloud API key for enhanced features.
        
        Args:
            open_key (str): Open Cloud API key
            
        Returns:
            dict: Operation result
            
        Raises:
            RoQuickError: If open_key is not provided
        """
        if not open_key:
            raise RoQuickError('Open Cloud key is required')
        
        print(f"{Fore.LIGHTBLACK_EX}Setting Open Cloud API key...{Style.RESET_ALL}")
        result = self.make_request('POST', '/api/set-openkey', {'openKey': open_key})
        print(f"{Fore.GREEN}Open Cloud key saved successfully{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}You can now use group operations{Style.RESET_ALL}")
        return result

    def get_api_key_status(self) -> Dict[str, Any]:
        """
        Get API key status and subscription information.
        
        Returns:
            dict: API key status including user info, subscription details, etc.
        """
        print(f"{Fore.LIGHTBLACK_EX}Checking API key status...{Style.RESET_ALL}")
        result = self.make_request('GET', '/api/key-status')
        
        print(f"{Fore.GREEN}API Key Status:{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}   User: {result['robloxUsername']} ({result['robloxUserId']}){Style.RESET_ALL}")
        
        subscription = result.get('subscription', {})
        is_active = subscription.get('isActive', False)
        tier = subscription.get('tier', 'free').upper()
        requests_per_minute = subscription.get('requestsPerMinute', 0)
        
        print(f"{Fore.LIGHTBLACK_EX}   Subscription: {'Active' if is_active else 'Inactive'} {tier}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}   Requests/min: {requests_per_minute}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}   This minute: {result.get('requestCount', 0)} requests{Style.RESET_ALL}")
        
        if result.get('isBlacklisted'):
            print(f"{Fore.RED}Account is blacklisted: {result.get('blacklistReason', 'Unknown reason')}{Style.RESET_ALL}")
        
        if not is_active:
            print(f"{Fore.YELLOW}Subscribe for premium features in Discord: {Fore.CYAN}{PACKAGE_INFO['discord']}{Style.RESET_ALL}")
        
        return result