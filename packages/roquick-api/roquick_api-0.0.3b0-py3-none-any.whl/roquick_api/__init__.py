"""
RoQuick API - Official Roblox Group Management API Wrapper

A comprehensive Python wrapper for the RoQuick API, providing advanced
Roblox group management features including member management, role assignment,
join request handling, and bulk operations.

Author: bluezly
License: MIT
Discord: https://discord.gg/GwxzWg9Cbh
"""

from .roquick_api import RoQuick, RoQuickError, PACKAGE_INFO

__version__ = PACKAGE_INFO["version"]
__author__ = PACKAGE_INFO["author"]
__email__ = PACKAGE_INFO["email"]
__license__ = PACKAGE_INFO["license"]
__discord__ = PACKAGE_INFO["discord"]

__all__ = ["RoQuick", "RoQuickError"]

# Display welcome message when package is imported
import sys
from colorama import init, Fore, Style
init(autoreset=True)

print(f"{Fore.CYAN}{Style.BRIGHT}RoQuick API - The Ultimate Roblox Group Management Solution{Style.RESET_ALL}")
print(f"{Fore.CYAN}IMPORTANT: Join our Discord to get your API key and learn how to use RoQuick!{Style.RESET_ALL}")
print(f"{Fore.BLUE}{Style.BRIGHT}Discord: {Fore.CYAN}{__discord__}{Style.RESET_ALL}")
print(f"{Fore.LIGHTBLACK_EX}Features:{Style.RESET_ALL}")
print(f"{Fore.LIGHTBLACK_EX}   User & Group information fetching{Style.RESET_ALL}")
print(f"{Fore.LIGHTBLACK_EX}   Role management & bulk operations{Style.RESET_ALL}")
print(f"{Fore.LIGHTBLACK_EX}   Join request handling{Style.RESET_ALL}")
print(f"{Fore.LIGHTBLACK_EX}   Group member filtering{Style.RESET_ALL}")
print(f"{Fore.LIGHTBLACK_EX}   Premium features with subscription{Style.RESET_ALL}")
print()