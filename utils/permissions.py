"""
Permission Management Utilities
Handles permission checking for admin and owner commands.
"""

import logging
import discord
from discord.ext import commands
from functools import wraps

logger = logging.getLogger(__name__)

class PermissionChecker:
    def __init__(self, owner_id):
        self.owner_id = owner_id
    
    def is_owner(self, user_id: int) -> bool:
        """Check if user is the bot owner"""
        return user_id == self.owner_id
    
    def has_admin_permissions(self, member: discord.Member) -> bool:
        """Check if member has admin permissions"""
        if self.is_owner(member.id):
            return True
        
        # Check if user has administrator permission
        if member.guild_permissions.administrator:
            return True
        
        # Check if user has manage_guild permission
        if member.guild_permissions.manage_guild:
            return True
        
        return False

def admin_required():
    """Decorator to require admin permissions for a command"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            # Check if user has admin permissions
            if not hasattr(self, 'permissions'):
                logger.error("Command cog missing permissions checker")
                await ctx.send("❌ Internal error: Permission checker not available.")
                return
            
            if not self.permissions.has_admin_permissions(ctx.author):
                embed = discord.Embed(
                    title="❌ Permission Denied",
                    description="This command requires administrator permissions.",
                    color=0xFF0000
                )
                embed.add_field(
                    name="Required Permissions",
                    value="• Administrator\n• Manage Server",
                    inline=False
                )
                await ctx.send(embed=embed)
                logger.warning(f"User {ctx.author} (ID: {ctx.author.id}) attempted to use admin command without permission")
                return
            
            # User has permission, execute the command
            return await func(self, ctx, *args, **kwargs)
        
        return wrapper
    return decorator

def owner_required():
    """Decorator to require bot owner permissions for a command"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            # Check if user is bot owner
            if not hasattr(self, 'permissions'):
                logger.error("Command cog missing permissions checker")
                await ctx.send("❌ Internal error: Permission checker not available.")
                return
            
            if not self.permissions.is_owner(ctx.author.id):
                embed = discord.Embed(
                    title="❌ Access Denied",
                    description="This command is restricted to the bot owner only.",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                logger.warning(f"User {ctx.author} (ID: {ctx.author.id}) attempted to use owner command")
                return
            
            # User is owner, execute the command
            return await func(self, ctx, *args, **kwargs)
        
        return wrapper
    return decorator

# Additional permission checks for specific scenarios
def check_bot_permissions(channel: discord.TextChannel, permissions_needed: list) -> tuple[bool, list]:
    """
    Check if bot has required permissions in a channel
    Returns (has_permissions, missing_permissions)
    """
    bot_permissions = channel.permissions_for(channel.guild.me)
    missing_permissions = []
    
    permission_map = {
        'send_messages': bot_permissions.send_messages,
        'embed_links': bot_permissions.embed_links,
        'attach_files': bot_permissions.attach_files,
        'read_message_history': bot_permissions.read_message_history,
        'use_external_emojis': bot_permissions.use_external_emojis,
        'add_reactions': bot_permissions.add_reactions,
        'manage_messages': bot_permissions.manage_messages
    }
    
    for permission in permissions_needed:
        if permission in permission_map and not permission_map[permission]:
            missing_permissions.append(permission)
    
    return len(missing_permissions) == 0, missing_permissions

def format_permissions(permissions: list) -> str:
    """Format permission names for display"""
    permission_names = {
        'send_messages': 'Send Messages',
        'embed_links': 'Embed Links',
        'attach_files': 'Attach Files',
        'read_message_history': 'Read Message History',
        'use_external_emojis': 'Use External Emojis',
        'add_reactions': 'Add Reactions',
        'manage_messages': 'Manage Messages'
    }
    
    return '\n'.join([f"• {permission_names.get(perm, perm.title())}" for perm in permissions])
