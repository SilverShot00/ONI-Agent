"""
Discord Bot Entry Point
Initializes and runs the Discord bot with Twitch monitoring capabilities.
"""

import asyncio
import logging
import os
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

async def main():
    """Main entry point for the bot"""
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

        # Check if bot has already started (simple flag)
        if hasattr(bot, 'has_started') and bot.has_started:
            logger.warning("Bot already running, exiting duplicate instance.")
            return
        bot.has_started = True
        
        logger.info("Starting Discord bot...")
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
