"""
Configuration Settings
Contains all configuration constants and default values.
"""

# Bot Configuration
COMMAND_PREFIX = "!"

# Twitch API Configuration
STREAM_CHECK_INTERVAL = 2  # Minutes between stream checks
DEFAULT_NOTIFICATION_MESSAGE = "🔴 {streamer} is now live! Playing {game} - {title} {url}"

# Discord Configuration
MAX_EMBED_FIELDS = 25  # Discord embed field limit
MAX_MESSAGE_LENGTH = 2000  # Discord message character limit
MAX_EMBED_DESCRIPTION = 4096  # Discord embed description limit

# Rate Limiting
TWITCH_API_REQUESTS_PER_MINUTE = 800  # Twitch Helix API rate limit
DISCORD_API_REQUESTS_PER_SECOND = 50  # Discord API rate limit

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Feature Toggles
ENABLE_STREAM_THUMBNAILS = True
ENABLE_VIEWER_COUNT = True
ENABLE_GAME_CATEGORY = True

# Error Messages
ERROR_MESSAGES = {
    'no_permission': "❌ You don't have permission to use this command.",
    'command_not_found': "❌ Command not found. Use `!help` for available commands.",
    'missing_argument': "❌ Missing required argument.",
    'invalid_channel': "❌ Invalid channel specified.",
    'streamer_not_found': "❌ Twitch streamer not found.",
    'already_monitoring': "⚠️ This streamer is already being monitored.",
    'not_monitoring': "❌ This streamer is not currently being monitored.",
    'no_notification_channel': "❌ No notification channel set. Use `!set_channel #channel` first.",
    'api_error': "❌ An error occurred while contacting the API. Please try again later.",
    'database_error': "❌ A database error occurred. Please contact the bot owner.",
    'rate_limited': "⚠️ Rate limited. Please try again in a few moments."
}

# Success Messages
SUCCESS_MESSAGES = {
    'streamer_added': "✅ Streamer successfully added to monitoring list!",
    'streamer_removed': "✅ Streamer successfully removed from monitoring list!",
    'channel_set': "✅ Notification channel successfully set!",
    'message_set': "✅ Custom message successfully set!",
    'status_updated': "✅ Bot status successfully updated!",
    'avatar_updated': "✅ Bot avatar successfully updated!",
    'name_updated': "✅ Bot name successfully updated!"
}

# Help Text
HELP_TEXT = {
    'admin_commands': [
        "**!add_streamer <username>** - Add a Twitch streamer to monitor",
        "**!remove_streamer <username>** - Remove a streamer from monitoring",
        "**!list_streamers** - Show all monitored streamers",
        "**!set_channel <#channel>** - Set notification channel",
        "**!set_message <username> <message>** - Customize notification message",
        "**!test_notification <username>** - Test notification for a streamer"
    ],
    'owner_commands': [
        "**!set_status <status>** - Change bot status",
        "**!set_avatar <url>** - Change bot avatar",
        "**!set_name <name>** - Change bot username",
        "**!bot_info** - Display bot information",
        "**!shutdown** - Shutdown the bot"
    ],
    'message_variables': [
        "**{streamer}** - Streamer name",
        "**{title}** - Stream title",
        "**{game}** - Game/Category being played",
        "**{url}** - Direct link to the stream"
    ]
}

# Default Values
DEFAULT_VALUES = {
    'notification_message': DEFAULT_NOTIFICATION_MESSAGE,
    'stream_check_interval': STREAM_CHECK_INTERVAL,
    'max_streamers_per_guild': 50,  # Reasonable limit to prevent spam
    'max_custom_message_length': 1000
}

# API Endpoints
API_ENDPOINTS = {
    'twitch_oauth': "https://id.twitch.tv/oauth2/token",
    'twitch_helix': "https://api.twitch.tv/helix",
    'twitch_validate': "https://id.twitch.tv/oauth2/validate"
}

# Colors (for Discord embeds)
COLORS = {
    'success': 0x00FF00,
    'error': 0xFF0000,
    'warning': 0xFF9900,
    'info': 0x0099FF,
    'twitch': 0x9146FF,
    'default': 0x36393F
}
