"""
Twitch API Service
Handles interactions with the Twitch Helix API for stream and user data.
"""

import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TwitchService:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
        self.session = None
        
        # API endpoints
        self.oauth_url = "https://id.twitch.tv/oauth2/token"
        self.helix_url = "https://api.twitch.tv/helix"
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _get_app_access_token(self):
        """Get application access token from Twitch"""
        try:
            session = await self._get_session()
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            async with session.post(self.oauth_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    # Set expiration time (subtract 60 seconds for safety)
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    logger.info("Successfully obtained Twitch access token")
                    return True
                else:
                    logger.error(f"Failed to get Twitch access token: {response.status}")
                    return False
        
        except Exception as e:
            logger.error(f"Error getting Twitch access token: {e}")
            return False
    
    async def _ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if (not self.access_token or 
            not self.token_expires_at or 
            datetime.now() >= self.token_expires_at):
            return await self._get_app_access_token()
        return True
    
    async def _make_api_request(self, endpoint, params=None):
        """Make authenticated request to Twitch API"""
        if not await self._ensure_valid_token():
            logger.error("Failed to ensure valid Twitch token")
            return None
        
        try:
            session = await self._get_session()
            
            headers = {
                'Client-ID': self.client_id,
                'Authorization': f'Bearer {self.access_token}'
            }
            
            url = f"{self.helix_url}/{endpoint}"
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    # Token might be invalid, try to refresh
                    logger.warning("Twitch token invalid, attempting to refresh")
                    if await self._get_app_access_token():
                        # Retry the request with new token
                        headers['Authorization'] = f'Bearer {self.access_token}'
                        async with session.get(url, headers=headers, params=params) as retry_response:
                            if retry_response.status == 200:
                                return await retry_response.json()
                            else:
                                logger.error(f"Twitch API error after token refresh: {retry_response.status}")
                                return None
                    else:
                        logger.error("Failed to refresh Twitch token")
                        return None
                elif response.status == 429:
                    # Rate limited
                    logger.warning("Twitch API rate limited")
                    return None
                else:
                    logger.error(f"Twitch API error: {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error making Twitch API request: {e}")
            return None
    
    async def get_user_data(self, username):
        """Get user data for a Twitch username"""
        try:
            response = await self._make_api_request('users', {'login': username.lower()})
            
            if response and response.get('data'):
                return response['data'][0]
            return None
        
        except Exception as e:
            logger.error(f"Error getting user data for {username}: {e}")
            return None
    
    async def get_stream_data(self, username):
        """Get stream data for a Twitch username"""
        try:
            response = await self._make_api_request('streams', {'user_login': username.lower()})
            
            if response and response.get('data'):
                if len(response['data']) > 0:
                    return response['data'][0]
            return None
        
        except Exception as e:
            logger.error(f"Error getting stream data for {username}: {e}")
            return None
    
    async def get_multiple_streams(self, usernames):
        """Get stream data for multiple usernames (up to 100)"""
        try:
            if not usernames:
                return []
            
            # Twitch API supports up to 100 usernames per request
            username_chunks = [usernames[i:i+100] for i in range(0, len(usernames), 100)]
            all_streams = []
            
            for chunk in username_chunks:
                params = {'user_login': [username.lower() for username in chunk]}
                response = await self._make_api_request('streams', params)
                
                if response and response.get('data'):
                    all_streams.extend(response['data'])
            
            return all_streams
        
        except Exception as e:
            logger.error(f"Error getting multiple stream data: {e}")
            return []
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
