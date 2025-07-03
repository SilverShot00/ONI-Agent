"""
Discord Bot Entry Point
Initializes and runs the Discord bot with Twitch monitoring capabilities.
"""

import asyncio
import logging
import os
import socket
import sys
from bot import TwitchMonitorBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def is_already_running(port=12345):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        s.listen(1)
        return False, s
    except OSError:
        return True, None

async def main():
    running, lock_socket = is_already_running()
    if running:
        logger.warning("Bot instance already running. Exiting.")
        sys.exit()

    try:
        # Get required tokens from environment variables
        discord_token = os.getenv('DISCORD_TOKEN')
        twitch_client_id = os.getenv('TWITCH_CLIENT_ID')
        twitch_client_secret = os.getenv('TWITCH_CLIENT_SECRET')
        owner_id = int(os.getenv('OWNER_ID', '0'))
        
        if not discord_token:
            logger.error("DISCORD_TOKEN environment variable is required")
            return
        
        if not twitch_client_id or not twitch_client_secret:
            logger.error("TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET environment variables are required")
            return
        
        if owner_id == 0:
            logger.error("OWNER_ID environment variable is required")
            return
        
        # Initialize bot instance
        bot = TwitchMonitorBot(
            discord_token=discord_token,
            twitch_client_id=twitch_client_id,
            twitch_client_secret=twitch_client_secret,
            owner_id=owner_id
        )
        
        logger.info("Starting Discord bot...")
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        if lock_socket:
            lock_socket.close()

if __name__ == '__main__':
    asyncio.run(main())
