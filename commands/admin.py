"""
Admin Commands for Discord Bot
Commands for managing streamers and notifications (requires admin permissions).
"""

import logging
import discord
from discord.ext import commands
from utils.permissions import admin_required

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    def __init__(self, bot, db, twitch, permissions):
        self.bot = bot
        self.db = db
        self.twitch = twitch
        self.permissions = permissions

    @commands.command(name='addstreamer')
    @admin_required()
    async def addstreamer(self, ctx, streamer_name: str):
        """Add a Twitch streamer to monitor"""
        try:
            user_data = await self.twitch.get_user_data(streamer_name)
            if not user_data:
                await ctx.send(f"❌ Twitch user '{streamer_name}' not found.")
                return

            actual_username = user_data['login']
            await self.db.create_guild(ctx.guild.id)

            if await self.db.add_streamer(ctx.guild.id, actual_username):
                embed = discord.Embed(
                    title="✅ Streamer Added",
                    description=f"Now monitoring **{actual_username}** for live streams!",
                    color=0x00FF00
                )
                embed.set_thumbnail(url=user_data.get('profile_image_url'))
                await ctx.send(embed=embed)
                logger.info(f"Added streamer {actual_username} to guild {ctx.guild.id}")
            else:
                await ctx.send(f"⚠️ **{actual_username}** is already being monitored.")

        except Exception as e:
            logger.error(f"Error adding streamer {streamer_name}: {e}")
            await ctx.send("❌ An error occurred while adding the streamer.")

    @commands.command(name='removestreamer')
    @admin_required()
    async def removestreamer(self, ctx, streamer_name: str):
        """Remove a Twitch streamer from monitoring"""
        try:
            if await self.db.remove_streamer(ctx.guild.id, streamer_name.lower()):
                embed = discord.Embed(
                    title="✅ Streamer Removed",
                    description=f"No longer monitoring **{streamer_name}**.",
                    color=0xFF9900
                )
                await ctx.send(embed=embed)
                logger.info(f"Removed streamer {streamer_name} from guild {ctx.guild.id}")
            else:
                await ctx.send(f"❌ **{streamer_name}** is not currently being monitored.")

        except Exception as e:
            logger.error(f"Error removing streamer {streamer_name}: {e}")
            await ctx.send("❌ An error occurred while removing the streamer.")

    @commands.command(name='liststreamers')
    @admin_required()
    async def liststreamers(self, ctx):
        """List all monitored streamers in this guild"""
        try:
            guild_data = await self.db.get_guild_data(ctx.guild.id)
            streamers = guild_data.get('streamers', []) if guild_data else []

            if not streamers:
                embed = discord.Embed(
                    title="📋 Monitored Streamers",
                    description="No streamers are currently being monitored.",
                    color=0x999999
                )
            else:
                embed = discord.Embed(
                    title="📋 Monitored Streamers",
                    description=f"Currently monitoring {len(streamers)} streamer(s):",
                    color=0x9146FF
                )
                for i, streamer in enumerate(streamers[:25]):
                    custom_messages = guild_data.get('custom_messages', {})
                    custom_msg = custom_messages.get(streamer, "Default message")
                    if len(custom_msg) > 100:
                        custom_msg = custom_msg[:97] + "..."
                    embed.add_field(
                        name=f"{i+1}. {streamer}",
                        value=f"Message: {custom_msg}",
                        inline=False
                    )
                if len(streamers) > 25:
                    embed.set_footer(text=f"... and {len(streamers) - 25} more streamers")

            notification_channel_id = guild_data.get('notification_channel') if guild_data else None
            if notification_channel_id:
                channel = ctx.guild.get_channel(notification_channel_id)
                if channel:
                    embed.add_field(
                        name="📢 Notification Channel",
                        value=channel.mention,
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="⚠️ Notification Channel",
                        value="Channel not found (may have been deleted)",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="❌ Notification Channel",
                    value="Not set (use `!set_channel #channel`)",
                    inline=False
                )

            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Error listing streamers: {e}")
            await ctx.send("❌ An error occurred while retrieving the streamer list.")

    @commands.command(name='setchannel')
    @admin_required()
    async def setchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel for stream notifications"""
        try:
            await self.db.create_guild(ctx.guild.id)

            permissions = channel.permissions_for(ctx.guild.me)
            if not permissions.send_messages or not permissions.embed_links:
                await ctx.send(f"❌ I don't have permission to send messages and embeds in {channel.mention}.")
                return

            await self.db.set_notification_channel(ctx.guild.id, channel.id)

            embed = discord.Embed(
                title="✅ Notification Channel Set",
                description=f"Stream notifications will be sent to {channel.mention}",
                color=0x00FF00
            )
            await ctx.send(embed=embed)
            logger.info(f"Set notification channel to {channel.id} for guild {ctx.guild.id}")

        except Exception as e:
            logger.error(f"Error setting notification channel: {e}")
            await ctx.send("❌ An error occurred while setting the notification channel.")

    @commands.command(name='setmessage')
    @admin_required()
    async def setmessage(self, ctx, streamer_name: str, *, message: str):
        """Set a custom notification message for a specific streamer"""
        try:
            guild_data = await self.db.get_guild_data(ctx.guild.id)
            streamers = guild_data.get('streamers', []) if guild_data else []

            if streamer_name.lower() not in [s.lower() for s in streamers]:
                await ctx.send(f"❌ **{streamer_name}** is not currently being monitored. Add them first with `!add_streamer {streamer_name}`.")
                return

            if len(message) > 1000:
                await ctx.send("❌ Custom message cannot exceed 1000 characters.")
                return

            await self.db.set_custom_message(ctx.guild.id, streamer_name.lower(), message)

            embed = discord.Embed(
                title="✅ Custom Message Set",
                description=f"Custom notification message set for **{streamer_name}**",
                color=0x00FF00
            )
            embed.add_field(name="Message Preview", value=message, inline=False)
            embed.add_field(
                name="Available Variables",
                value="`{streamer}` `{title}` `{game}` `{url}`",
                inline=False
            )
            await ctx.send(embed=embed)
            logger.info(f"Set custom message for {streamer_name} in guild {ctx.guild.id}")

        except Exception as e:
            logger.error(f"Error setting custom message: {e}")
            await ctx.send("❌ An error occurred while setting the custom message.")

    @commands.command(name='testnotification')
    @admin_required()
    async def testnotification(self, ctx, streamer_name: str):
        """Send a test notification for a streamer"""
        try:
            guild_data = await self.db.get_guild_data(ctx.guild.id)
            streamers = guild_data.get('streamers', []) if guild_data else []

            if streamer_name.lower() not in [s.lower() for s in streamers]:
                await ctx.send(f"❌ **{streamer_name}** is not currently being monitored.")
                return

            notification_channel_id = guild_data.get('notification_channel')
            if not notification_channel_id:
                await ctx.send("❌ No notification channel set. Use `!set_channel #channel` first.")
                return

            channel = ctx.guild.get_channel(notification_channel_id)
            if not channel:
                await ctx.send("❌ Notification channel not found.")
                return

            custom_messages = guild_data.get('custom_messages', {})
            message_template = custom_messages.get(streamer_name.lower(), "🔴 {streamer} is now live! Playing {game} - {title} {url}")

            message = message_template.format(
                streamer=streamer_name,
                title="Test Stream Title",
                game="Test Game",
                url=f"https://twitch.tv/{streamer_name}"
            )

            embed = discord.Embed(
                title=f"🔴 {streamer_name} is now live! (TEST)",
                description="Test Stream Title",
                color=0x9146FF,
                url=f"https://twitch.tv/{streamer_name}"
            )
            embed.add_field(name="Category", value="Test Game", inline=True)
            embed.add_field(name="Viewers", value="1337", inline=True)
            embed.set_footer(text="-# Notification Authorized by *Redacted*")
            embed.timestamp = discord.utils.utcnow()

            await channel.send(content=message, embed=embed)
            await ctx.send(f"✅ Test notification sent to {channel.mention}")
            logger.info(f"Sent test notification for {streamer_name} in guild {ctx.guild.id}")

        except Exception as e:
            logger.error(f"Error sending test notification: {e}")
            await ctx.send("❌ An error occurred while sending the test notification.")
