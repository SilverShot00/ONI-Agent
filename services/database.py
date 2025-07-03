"""
Database Service
In-memory storage for guild settings and streamer configurations.
This can be easily upgraded to a persistent database later.
"""

import logging
import json
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        """Initialize in-memory database"""
        # Structure: {guild_id: {streamers: [], notification_channel: int, custom_messages: {}}}
        self.guilds: Dict[int, Dict] = {}
        logger.info("Database service initialized (in-memory)")
    
    def create_guild(self, guild_id: int) -> bool:
        """Create or ensure guild exists in database"""
        try:
            if guild_id not in self.guilds:
                self.guilds[guild_id] = {
                    'streamers': [],
                    'notification_channel': None,
                    'custom_messages': {}
                }
                logger.info(f"Created guild entry for {guild_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error creating guild {guild_id}: {e}")
            return False
    
    def delete_guild(self, guild_id: int) -> bool:
        """Delete guild and all its data"""
        try:
            if guild_id in self.guilds:
                del self.guilds[guild_id]
                logger.info(f"Deleted guild {guild_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting guild {guild_id}: {e}")
            return False
    
    def get_guild_data(self, guild_id: int) -> Optional[Dict]:
        """Get all data for a guild"""
        return self.guilds.get(guild_id)
    
    def get_all_guilds(self) -> List[int]:
        """Get list of all guild IDs"""
        return list(self.guilds.keys())
    
    def add_streamer(self, guild_id: int, streamer_name: str) -> bool:
        """Add a streamer to a guild's monitoring list"""
        try:
            self.create_guild(guild_id)  # Ensure guild exists
            
            streamer_name = streamer_name.lower()
            
            if streamer_name not in self.guilds[guild_id]['streamers']:
                self.guilds[guild_id]['streamers'].append(streamer_name)
                logger.info(f"Added streamer {streamer_name} to guild {guild_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding streamer {streamer_name} to guild {guild_id}: {e}")
            return False
    
    def remove_streamer(self, guild_id: int, streamer_name: str) -> bool:
        """Remove a streamer from a guild's monitoring list"""
        try:
            if guild_id not in self.guilds:
                return False
            
            streamer_name = streamer_name.lower()
            
            if streamer_name in self.guilds[guild_id]['streamers']:
                self.guilds[guild_id]['streamers'].remove(streamer_name)
                # Also remove custom message if it exists
                if streamer_name in self.guilds[guild_id]['custom_messages']:
                    del self.guilds[guild_id]['custom_messages'][streamer_name]
                logger.info(f"Removed streamer {streamer_name} from guild {guild_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing streamer {streamer_name} from guild {guild_id}: {e}")
            return False
    
    def get_streamers(self, guild_id: int) -> List[str]:
        """Get list of monitored streamers for a guild"""
        if guild_id in self.guilds:
            return self.guilds[guild_id]['streamers'].copy()
        return []
    
    def set_notification_channel(self, guild_id: int, channel_id: int) -> bool:
        """Set the notification channel for a guild"""
        try:
            self.create_guild(guild_id)  # Ensure guild exists
            self.guilds[guild_id]['notification_channel'] = channel_id
            logger.info(f"Set notification channel {channel_id} for guild {guild_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting notification channel for guild {guild_id}: {e}")
            return False
    
    def get_notification_channel(self, guild_id: int) -> Optional[int]:
        """Get the notification channel for a guild"""
        if guild_id in self.guilds:
            return self.guilds[guild_id]['notification_channel']
        return None
    
    def set_custom_message(self, guild_id: int, streamer_name: str, message: str) -> bool:
        """Set a custom notification message for a streamer"""
        try:
            self.create_guild(guild_id)  # Ensure guild exists
            streamer_name = streamer_name.lower()
            self.guilds[guild_id]['custom_messages'][streamer_name] = message
            logger.info(f"Set custom message for {streamer_name} in guild {guild_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting custom message for {streamer_name} in guild {guild_id}: {e}")
            return False
    
    def get_custom_message(self, guild_id: int, streamer_name: str) -> Optional[str]:
        """Get custom notification message for a streamer"""
        if guild_id in self.guilds:
            return self.guilds[guild_id]['custom_messages'].get(streamer_name.lower())
        return None
    
    def export_data(self) -> str:
        """Export all data as JSON string (for backup purposes)"""
        try:
            return json.dumps(self.guilds, indent=2)
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return "{}"
    
    def import_data(self, json_data: str) -> bool:
        """Import data from JSON string (for restore purposes)"""
        try:
            imported_data = json.loads(json_data)
            # Convert string keys back to integers
            self.guilds = {int(k): v for k, v in imported_data.items()}
            logger.info("Successfully imported data")
            return True
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            total_guilds = len(self.guilds)
            total_streamers = sum(len(guild_data['streamers']) for guild_data in self.guilds.values())
            total_custom_messages = sum(len(guild_data['custom_messages']) for guild_data in self.guilds.values())
            
            return {
                'total_guilds': total_guilds,
                'total_streamers': total_streamers,
                'total_custom_messages': total_custom_messages
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
