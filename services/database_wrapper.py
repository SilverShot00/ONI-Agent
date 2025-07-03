"""
Database Wrapper
Provides a unified interface for both MongoDB and in-memory database services.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class DatabaseWrapper:
    def __init__(self, mongodb_service, fallback_service):
        self.mongodb = mongodb_service
        self.fallback = fallback_service
        self.active_db = None
        self.is_async = False
    
    async def initialize(self):
        """Initialize the database connection"""
        try:
            if await self.mongodb.connect():
                self.active_db = self.mongodb
                self.is_async = True
                logger.info("Using MongoDB database")
                return True
        except Exception as e:
            logger.error(f"MongoDB initialization failed: {e}")
        
        self.active_db = self.fallback
        self.is_async = False
        logger.info("Using in-memory database")
        return True
    
    async def create_guild(self, guild_id: int) -> bool:
        """Create or ensure guild exists in database"""
        if self.is_async:
            return await self.active_db.create_guild(guild_id)
        else:
            return self.active_db.create_guild(guild_id)
    
    async def delete_guild(self, guild_id: int) -> bool:
        """Delete guild and all its data"""
        if self.is_async:
            return await self.active_db.delete_guild(guild_id)
        else:
            return self.active_db.delete_guild(guild_id)
    
    async def get_guild_data(self, guild_id: int) -> Optional[Dict]:
        """Get all data for a guild"""
        if self.is_async:
            return await self.active_db.get_guild_data(guild_id)
        else:
            return self.active_db.get_guild_data(guild_id)
    
    async def get_all_guilds(self) -> List[int]:
        """Get list of all guild IDs"""
        if self.is_async:
            return await self.active_db.get_all_guilds()
        else:
            return self.active_db.get_all_guilds()
    
    async def add_streamer(self, guild_id: int, streamer_name: str) -> bool:
        """Add a streamer to a guild's monitoring list"""
        if self.is_async:
            return await self.active_db.add_streamer(guild_id, streamer_name)
        else:
            return self.active_db.add_streamer(guild_id, streamer_name)
    
    async def remove_streamer(self, guild_id: int, streamer_name: str) -> bool:
        """Remove a streamer from a guild's monitoring list"""
        if self.is_async:
            return await self.active_db.remove_streamer(guild_id, streamer_name)
        else:
            return self.active_db.remove_streamer(guild_id, streamer_name)
    
    async def get_streamers(self, guild_id: int) -> List[str]:
        """Get list of monitored streamers for a guild"""
        if self.is_async:
            return await self.active_db.get_streamers(guild_id)
        else:
            return self.active_db.get_streamers(guild_id)
    
    async def set_notification_channel(self, guild_id: int, channel_id: int) -> bool:
        """Set the notification channel for a guild"""
        if self.is_async:
            return await self.active_db.set_notification_channel(guild_id, channel_id)
        else:
            return self.active_db.set_notification_channel(guild_id, channel_id)
    
    async def get_notification_channel(self, guild_id: int) -> Optional[int]:
        """Get the notification channel for a guild"""
        if self.is_async:
            return await self.active_db.get_notification_channel(guild_id)
        else:
            return self.active_db.get_notification_channel(guild_id)
    
    async def set_custom_message(self, guild_id: int, streamer_name: str, message: str) -> bool:
        """Set a custom notification message for a streamer"""
        if self.is_async:
            return await self.active_db.set_custom_message(guild_id, streamer_name, message)
        else:
            return self.active_db.set_custom_message(guild_id, streamer_name, message)
    
    async def get_custom_message(self, guild_id: int, streamer_name: str) -> Optional[str]:
        """Get custom notification message for a streamer"""
        if self.is_async:
            return await self.active_db.get_custom_message(guild_id, streamer_name)
        else:
            return self.active_db.get_custom_message(guild_id, streamer_name)
    
    async def get_stats(self) -> Dict:
        """Get database statistics"""
        if self.is_async:
            return await self.active_db.get_stats()
        else:
            return self.active_db.get_stats()