"""
MongoDB Database Service
Handles persistent storage for guild settings and streamer configurations using MongoDB.
"""

import logging
import os
from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self):
        """Initialize MongoDB connection"""
        # Get MongoDB connection string from environment or use default
        self.mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
        self.database_name = os.getenv('DATABASE_NAME', 'twitch_bot')
        
        self.client = None
        self.db = None
        self.guilds_collection = None
        
        logger.info(f"MongoDB service initialized with URL: {self.mongo_url}")
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.database_name]
            self.guilds_collection = self.db.guilds
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def create_guild(self, guild_id: int) -> bool:
        """Create or ensure guild exists in database"""
        try:
            # Check if guild already exists
            existing = await self.guilds_collection.find_one({"guild_id": guild_id})
            if existing:
                return False
            
            # Create new guild document
            guild_doc = {
                "guild_id": guild_id,
                "streamers": [],
                "notification_channel": None,
                "custom_messages": {}
            }
            
            await self.guilds_collection.insert_one(guild_doc)
            logger.info(f"Created guild entry for {guild_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating guild {guild_id}: {e}")
            return False
    
    async def delete_guild(self, guild_id: int) -> bool:
        """Delete guild and all its data"""
        try:
            result = await self.guilds_collection.delete_one({"guild_id": guild_id})
            if result.deleted_count > 0:
                logger.info(f"Deleted guild {guild_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting guild {guild_id}: {e}")
            return False
    
    async def get_guild_data(self, guild_id: int) -> Optional[Dict]:
        """Get all data for a guild"""
        try:
            guild_doc = await self.guilds_collection.find_one({"guild_id": guild_id})
            if guild_doc:
                # Remove MongoDB's _id field
                guild_doc.pop('_id', None)
                return guild_doc
            return None
        except Exception as e:
            logger.error(f"Error getting guild data {guild_id}: {e}")
            return None
    
    async def get_all_guilds(self) -> List[int]:
        """Get list of all guild IDs"""
        try:
            cursor = self.guilds_collection.find({}, {"guild_id": 1})
            guild_ids = []
            async for doc in cursor:
                guild_ids.append(doc["guild_id"])
            return guild_ids
        except Exception as e:
            logger.error(f"Error getting all guilds: {e}")
            return []
    
    async def add_streamer(self, guild_id: int, streamer_name: str) -> bool:
        """Add a streamer to a guild's monitoring list"""
        try:
            await self.create_guild(guild_id)  # Ensure guild exists
            
            streamer_name = streamer_name.lower()
            
            # Check if streamer already exists
            guild_doc = await self.guilds_collection.find_one({
                "guild_id": guild_id,
                "streamers": streamer_name
            })
            
            if guild_doc:
                return False  # Already exists
            
            # Add streamer to array
            result = await self.guilds_collection.update_one(
                {"guild_id": guild_id},
                {"$addToSet": {"streamers": streamer_name}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Added streamer {streamer_name} to guild {guild_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding streamer {streamer_name} to guild {guild_id}: {e}")
            return False
    
    async def remove_streamer(self, guild_id: int, streamer_name: str) -> bool:
        """Remove a streamer from a guild's monitoring list"""
        try:
            streamer_name = streamer_name.lower()
            
            # Remove streamer from array and custom message
            result = await self.guilds_collection.update_one(
                {"guild_id": guild_id},
                {
                    "$pull": {"streamers": streamer_name},
                    "$unset": {f"custom_messages.{streamer_name}": ""}
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Removed streamer {streamer_name} from guild {guild_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing streamer {streamer_name} from guild {guild_id}: {e}")
            return False
    
    async def get_streamers(self, guild_id: int) -> List[str]:
        """Get list of monitored streamers for a guild"""
        try:
            guild_doc = await self.guilds_collection.find_one(
                {"guild_id": guild_id},
                {"streamers": 1}
            )
            
            if guild_doc and "streamers" in guild_doc:
                return guild_doc["streamers"].copy()
            return []
        except Exception as e:
            logger.error(f"Error getting streamers for guild {guild_id}: {e}")
            return []
    
    async def set_notification_channel(self, guild_id: int, channel_id: int) -> bool:
        """Set the notification channel for a guild"""
        try:
            await self.create_guild(guild_id)  # Ensure guild exists
            
            result = await self.guilds_collection.update_one(
                {"guild_id": guild_id},
                {"$set": {"notification_channel": channel_id}}
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                logger.info(f"Set notification channel {channel_id} for guild {guild_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting notification channel for guild {guild_id}: {e}")
            return False
    
    async def get_notification_channel(self, guild_id: int) -> Optional[int]:
        """Get the notification channel for a guild"""
        try:
            guild_doc = await self.guilds_collection.find_one(
                {"guild_id": guild_id},
                {"notification_channel": 1}
            )
            
            if guild_doc and "notification_channel" in guild_doc:
                return guild_doc["notification_channel"]
            return None
        except Exception as e:
            logger.error(f"Error getting notification channel for guild {guild_id}: {e}")
            return None
    
    async def set_custom_message(self, guild_id: int, streamer_name: str, message: str) -> bool:
        """Set a custom notification message for a streamer"""
        try:
            await self.create_guild(guild_id)  # Ensure guild exists
            
            streamer_name = streamer_name.lower()
            
            result = await self.guilds_collection.update_one(
                {"guild_id": guild_id},
                {"$set": {f"custom_messages.{streamer_name}": message}}
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                logger.info(f"Set custom message for {streamer_name} in guild {guild_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting custom message for {streamer_name} in guild {guild_id}: {e}")
            return False
    
    async def get_custom_message(self, guild_id: int, streamer_name: str) -> Optional[str]:
        """Get custom notification message for a streamer"""
        try:
            streamer_name = streamer_name.lower()
            
            guild_doc = await self.guilds_collection.find_one(
                {"guild_id": guild_id},
                {"custom_messages": 1}
            )
            
            if guild_doc and "custom_messages" in guild_doc:
                return guild_doc["custom_messages"].get(streamer_name)
            return None
        except Exception as e:
            logger.error(f"Error getting custom message for {streamer_name} in guild {guild_id}: {e}")
            return None
    
    async def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            total_guilds = await self.guilds_collection.count_documents({})
            
            # Aggregate streamers count
            pipeline = [
                {"$project": {"streamer_count": {"$size": "$streamers"}}},
                {"$group": {"_id": None, "total_streamers": {"$sum": "$streamer_count"}}}
            ]
            
            result = await self.guilds_collection.aggregate(pipeline).to_list(1)
            total_streamers = result[0]["total_streamers"] if result else 0
            
            # Aggregate custom messages count
            pipeline = [
                {"$project": {"message_count": {"$size": {"$objectToArray": "$custom_messages"}}}},
                {"$group": {"_id": None, "total_messages": {"$sum": "$message_count"}}}
            ]
            
            result = await self.guilds_collection.aggregate(pipeline).to_list(1)
            total_custom_messages = result[0]["total_messages"] if result else 0
            
            return {
                'total_guilds': total_guilds,
                'total_streamers': total_streamers,
                'total_custom_messages': total_custom_messages
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}