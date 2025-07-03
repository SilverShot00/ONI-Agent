"""
Main Discord Bot Class
Handles bot initialization, command registration, and background tasks.
"""

import asyncio
import logging
import discord
from discord.ext import commands, tasks
from services.twitch import TwitchService
from services.mongodb import MongoDBService
from services.database import DatabaseService
from services.database_wrapper import DatabaseWrapper
from commands.admin import AdminCommands
from commands.owner import OwnerCommands
from utils.permissions import PermissionChecker
import config

logger = logging.getLogger(__name__)

class TwitchMonitorBot:
    def __init__(self, discord_token, twitch_client_id, twitch_client_secret, owner_id):
        self.discord_token = discord_token
        self.owner_id = owner_id
        
        # Configure bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        # Initialize bot
        self.bot = commands.Bot(
            command_prefix=config.COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )
        
        # Initialize services
        self.mongodb = MongoDBService()
        self.fallback_db = DatabaseService()
        self.db = DatabaseWrapper(self.mongodb, self.fallback_db)
        self.twitch = TwitchService(twitch_client_id, twitch_client_secret)
        self.permissions = PermissionChecker(owner_id)
        
        # Track live streams to avoid duplicate notifications
        self.live_streams = set()
        
        # Setup bot events and commands
        self.setup_events()
        self.setup_commands()
    
    def setup_events(self):
        """Setup Discord bot events"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f'{self.bot.user} has connected to Discord!')
            logger.info(f'Bot is in {len(self.bot.guilds)} guilds')
            
            # Initialize database wrapper
            await self.db.initialize()
            
            # Start background tasks
            if not self.check_streams.is_running():
                self.check_streams.start()
        
        @self.bot.event
        async def on_guild_join(guild):
            logger.info(f'Joined guild: {guild.name} (ID: {guild.id})')
            # Initialize guild settings
            await self.db.create_guild(guild.id)
        
        @self.bot.event
        async def on_guild_remove(guild):
            logger.info(f'Left guild: {guild.name} (ID: {guild.id})')
            # Clean up guild data
            await self.db.delete_guild(guild.id)
        
        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.MissingPermissions):
                await ctx.send("❌ You don't have permission to use this command.")
            elif isinstance(error, commands.CommandNotFound):
                return  # Ignore unknown commands
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(f"❌ Missing required argument: {error.param}")
            else:
                logger.error(f"Command error: {error}")
                await ctx.send("❌ An error occurred while executing the command.")
    
    def setup_commands(self):
        """Setup bot commands"""
        # Add admin commands
        admin_cog = AdminCommands(self.bot, self.db, self.twitch, self.permissions)
        asyncio.create_task(self.bot.add_cog(admin_cog))
        
        # Add owner commands
        owner_cog = OwnerCommands(self.bot, self.permissions)
        asyncio.create_task(self.bot.add_cog(owner_cog))
        
        # Add help command
        @self.bot.command(name='help')
        async def help_command(ctx):
            """Display bot commands and usage"""
            embed = discord.Embed(
                title="🤖 Agent *redacted* reporting",
                description="Permission to leave the station Sir?",
                color=0x9146FF
            )
            
            # Admin commands
            admin_commands = [
                "`!addstreamer <username>` - Add a Twitch streamer to monitor",
                "`!removestreamer <username>` - Remove a streamer from monitoring",
                "`!liststreamers` - Show all monitored streamers",
                "`!setchannel <#channel>` - Set notification channel",
                "`!setmessage <username> <message>` - Customize notification message",
                "`!testnotification <username>` - Test notification for a streamer"
            ]
            
            embed.add_field(
                name="👑 Admin Commands (Requires Admin Permission)",
                value="\n".join(admin_commands),
                inline=False
            )
            
            # Owner commands
            if ctx.author.id == self.owner_id:
                owner_commands = [
                    "`!setstatus <status>` - Change bot status",
                    "`!setavatar <url>` - Change bot avatar",
                    "`!setname <name>` - Change bot username",
                    "`!info` - Display bot information",
                    "`!shutdown` - Shutdown the bot"
                ]
                
                embed.add_field(
                    name="🔧 Owner Commands",
                    value="\n".join(owner_commands),
                    inline=False
                )
            
            embed.add_field(
                name="📝 Message Variables",
                value="`{streamer}` - Streamer name\n`{title}` - Stream title\n`{game}` - Game/Category\n`{url}` - Stream URL",
                inline=False
            )
            
            embed.set_footer(text=f"Bot Owner: {self.bot.get_user(self.owner_id)}")
            
            await ctx.send(embed=embed)
    
    @tasks.loop(minutes=config.STREAM_CHECK_INTERVAL)
    async def check_streams(self):
        """Background task to check for live streams"""
        try:
            # Get all guilds and their monitored streamers
            guild_ids = await self.db.get_all_guilds()
            for guild_id in guild_ids:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    continue
                
                guild_data = await self.db.get_guild_data(guild_id)
                if not guild_data or not guild_data.get('streamers'):
                    continue
                
                notification_channel_id = guild_data.get('notification_channel')
                if not notification_channel_id:
                    continue
                
                channel = guild.get_channel(notification_channel_id)
                if not channel:
                    continue
                
                # Check each streamer
                for streamer_name in guild_data['streamers']:
                    try:
                        stream_data = await self.twitch.get_stream_data(streamer_name)
                        stream_key = f"{guild_id}_{streamer_name}"
                        
                        if stream_data and stream_data.get('type') == 'live':
                            # Stream is live
                            if stream_key not in self.live_streams:
                                # New live stream - send notification
                                self.live_streams.add(stream_key)
                                await self.send_live_notification(
                                    channel, streamer_name, stream_data, guild_data
                                )
                        else:
                            # Stream is offline - remove from live streams
                            self.live_streams.discard(stream_key)
                    
                    except Exception as e:
                        logger.error(f"Error checking stream for {streamer_name}: {e}")
        
        except Exception as e:
            logger.error(f"Error in stream check task: {e}")
    
    async def send_live_notification(self, channel, streamer_name, stream_data, guild_data):
        """Send live stream notification to Discord channel"""
        try:
            # Get custom message or use default
            custom_messages = guild_data.get('custom_messages', {})
            message_template = custom_messages.get(
                streamer_name, 
                config.DEFAULT_NOTIFICATION_MESSAGE
            )
            
            # Replace variables in message
            message = message_template.format(
                streamer=streamer_name,
                title=stream_data.get('title', 'No title'),
                game=stream_data.get('game_name', 'No category'),
                url=f"https://twitch.tv/{streamer_name}"
            )
            
            # Create embed
            embed = discord.Embed(
                title=f"🔴 {streamer_name} is now live!",
                description=stream_data.get('title', 'No title'),
                color=0x9146FF,
                url=f"https://twitch.tv/{streamer_name}"
            )
            
            if stream_data.get('game_name'):
                embed.add_field(name="Category", value=stream_data['game_name'], inline=True)
            
            if stream_data.get('viewer_count') is not None:
                embed.add_field(name="Viewers", value=str(stream_data['viewer_count']), inline=True)
            
            if stream_data.get('thumbnail_url'):
                # Replace template variables in thumbnail URL
                thumbnail_url = stream_data['thumbnail_url'].replace('{width}', '640').replace('{height}', '360')
                embed.set_image(url=thumbnail_url)
            
            embed.set_footer(text="*Redacted*")
            embed.timestamp = discord.utils.utcnow()
            
            await channel.send(content=message, embed=embed)
            logger.info(f"Sent live notification for {streamer_name} in guild {channel.guild.id}")
        
        except Exception as e:
            logger.error(f"Error sending notification for {streamer_name}: {e}")
    
    async def run(self):
        """Start the Discord bot"""
        try:
            await self.bot.start(self.discord_token)
        except KeyboardInterrupt:
            logger.info("Bot shutdown requested")
        except Exception as e:
            logger.error(f"Bot error: {e}")
            raise
        finally:
            await self.bot.close()
