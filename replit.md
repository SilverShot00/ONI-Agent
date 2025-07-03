# Twitch Monitor Discord Bot

## Overview

This is a Discord bot designed to monitor Twitch streamers and send notifications when they go live. The bot uses the Twitch Helix API to check stream status and provides administrative commands for managing streamer monitoring and notification settings.

## System Architecture

The application follows a modular, service-oriented architecture with clear separation of concerns:

- **Event-driven architecture**: Built on Discord.py's command and event system
- **Service layer pattern**: Separate services for Twitch API and database operations
- **Command pattern**: Organized commands into logical groups (admin, owner)
- **In-memory storage**: Currently uses in-memory data structures for simplicity
- **Asynchronous design**: Fully async/await implementation for optimal performance

## Key Components

### Core Components
- **`bot.py`**: Main bot class that orchestrates all components and handles Discord events
- **`main.py`**: Entry point that manages environment variables and bot initialization
- **`config.py`**: Centralized configuration with constants, rate limits, and message templates

### Services
- **`TwitchService`**: Handles OAuth authentication and API calls to Twitch Helix API
- **`DatabaseService`**: Manages in-memory storage of guild settings and streamer lists

### Commands
- **`AdminCommands`**: Commands for managing streamers (requires admin permissions)
- **`OwnerCommands`**: Bot management commands (owner only)

### Utilities
- **`PermissionChecker`**: Handles role-based access control with decorators

## Data Flow

1. **Initialization**: Bot authenticates with Discord and Twitch APIs
2. **Command Processing**: Users invoke commands through Discord chat
3. **Permission Validation**: Commands are validated against user permissions
4. **API Interactions**: Bot communicates with Twitch API for stream data
5. **Data Storage**: Guild settings stored in in-memory database
6. **Notifications**: Background task monitors streams and sends Discord notifications

## External Dependencies

### APIs
- **Discord API**: Core bot functionality and message sending
- **Twitch Helix API**: Stream monitoring and user data retrieval

### Libraries
- **discord.py**: Discord bot framework with commands extension
- **aiohttp**: Async HTTP client for API requests
- **asyncio**: Async programming support

### Authentication
- OAuth 2.0 client credentials flow for Twitch API access
- Discord bot token authentication

## Deployment Strategy

### Environment Variables Required
- `DISCORD_TOKEN`: Discord bot authentication token
- `TWITCH_CLIENT_ID`: Twitch application client ID
- `TWITCH_CLIENT_SECRET`: Twitch application client secret
- `OWNER_ID`: Discord user ID of the bot owner

### Current State
- In-memory storage (data lost on restart)
- Single-instance deployment
- File-based logging to `bot.log`

### Future Considerations
- Database migration path ready (Drizzle ORM can be integrated)
- Horizontal scaling support needed for multiple guilds
- Persistent storage for configuration and monitoring lists

## Changelog
- July 03, 2025: Complete Discord bot implementation with all requested features
  - Bot successfully connects to Discord and Twitch APIs
  - All admin commands implemented (add/remove streamers, set channels, custom messages)
  - All owner commands implemented (status, avatar, username management)
  - Background stream monitoring every 2 minutes
  - Rich embed notifications with thumbnails and stream info
  - Fixed duplicate response issue by removing redundant workflow
  - Updated command names: removed underscores (e.g., !addstreamer instead of !add_streamer)
  - Added MongoDB integration with automatic fallback to in-memory database
  - Created database wrapper for seamless switching between storage types
  - Added MONGODB_URL secret support for persistent storage
  - Successfully connected to MongoDB - bot now has permanent data storage

## User Preferences

Preferred communication style: Simple, everyday language.