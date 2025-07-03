"""
Owner Commands for Discord Bot
Commands for managing bot settings (owner only).
"""

import logging
import discord
from discord.ext import commands
from utils.permissions import owner_required
import aiohttp

logger = logging.getLogger(__name__)

class OwnerCommands(commands.Cog):
    def __init__(self, bot, permissions):
        self.bot = bot
        self.permissions = permissions
    
    @commands.command(name='setstatus')
    @owner_required()
    async def setstatus(self, ctx, *, status: str):
        """Set the bot's status message"""
        try:
            await self.bot.change_presence(activity=discord.Game(name=status))
            
            embed = discord.Embed(
                title="✅ Status Updated",
                description=f"Bot status changed to: **{status}**",
                color=0x00FF00
            )
            await ctx.send(embed=embed)
            logger.info(f"Bot status changed to: {status}")
        
        except Exception as e:
            logger.error(f"Error setting bot status: {e}")
            await ctx.send("❌ An error occurred while setting the bot status.")
    
    @commands.command(name='setavatar')
    @owner_required()
    async def setavatar(self, ctx, url: str):
        """Set the bot's avatar from a URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        await ctx.send("❌ Could not download image from the provided URL.")
                        return
                    
                    if response.content_type not in ['image/jpeg', 'image/png', 'image/gif']:
                        await ctx.send("❌ Invalid image format. Please use JPEG, PNG, or GIF.")
                        return
                    
                    # Check file size (Discord limit is 8MB, but let's keep it reasonable)
                    content_length = response.headers.get('content-length')
                    if content_length and int(content_length) > 8 * 1024 * 1024:
                        await ctx.send("❌ Image file is too large. Please use an image smaller than 8MB.")
                        return
                    
                    avatar_data = await response.read()
            
            await self.bot.user.edit(avatar=avatar_data)
            
            embed = discord.Embed(
                title="✅ Avatar Updated",
                description="Bot avatar has been successfully changed!",
                color=0x00FF00
            )
            embed.set_image(url=url)
            await ctx.send(embed=embed)
            logger.info("Bot avatar updated successfully")
        
        except discord.HTTPException as e:
            if e.status == 400:
                await ctx.send("❌ Invalid image data or format.")
            elif e.status == 429:
                await ctx.send("❌ Rate limited. Please try again later.")
            else:
                await ctx.send(f"❌ Discord API error: {e}")
            logger.error(f"Discord HTTP error setting avatar: {e}")
        
        except Exception as e:
            logger.error(f"Error setting bot avatar: {e}")
            await ctx.send("❌ An error occurred while setting the bot avatar.")
    
    @commands.command(name='setname')
    @owner_required()
    async def setname(self, ctx, *, name: str):
        """Set the bot's username"""
        try:
            if len(name) < 2 or len(name) > 32:
                await ctx.send("❌ Username must be between 2 and 32 characters long.")
                return
            
            old_name = self.bot.user.display_name
            await self.bot.user.edit(username=name)
            
            embed = discord.Embed(
                title="✅ Username Updated",
                description=f"Bot username changed from **{old_name}** to **{name}**",
                color=0x00FF00
            )
            await ctx.send(embed=embed)
            logger.info(f"Bot username changed from {old_name} to {name}")
        
        except discord.HTTPException as e:
            if e.status == 400:
                await ctx.send("❌ Invalid username. Username may be taken or contain invalid characters.")
            elif e.status == 429:
                await ctx.send("❌ Rate limited. You can only change the username twice per hour.")
            else:
                await ctx.send(f"❌ Discord API error: {e}")
            logger.error(f"Discord HTTP error setting username: {e}")
        
        except Exception as e:
            logger.error(f"Error setting bot username: {e}")
            await ctx.send("❌ An error occurred while setting the bot username.")
    
    @commands.command(name='info')
    @owner_required()
    async def info(self, ctx):
        """Display bot information and statistics"""
        try:
            embed = discord.Embed(
                title="🤖 Bot Information",
                color=0x9146FF
            )
            
            embed.add_field(name="Bot Name", value=self.bot.user.display_name, inline=True)
            embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
            embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
            
            total_members = sum(guild.member_count for guild in self.bot.guilds)
            embed.add_field(name="Total Members", value=total_members, inline=True)
            
            embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
            
            # Get current status
            activity = self.bot.activity
            status_text = activity.name if activity else "None"
            embed.add_field(name="Current Status", value=status_text, inline=True)
            
            embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            embed.set_footer(text=f"Owner: {ctx.author}")
            embed.timestamp = discord.utils.utcnow()
            
            await ctx.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            await ctx.send("❌ An error occurred while retrieving bot information.")
    
    @commands.command(name='shutdown')
    @owner_required()
    async def shutdown(self, ctx):
        """Shutdown the bot (owner only)"""
        embed = discord.Embed(
            title="🔴 Bot Shutting Down",
            description="Bot is shutting down...",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        logger.info(f"Bot shutdown requested by owner {ctx.author}")
        await self.bot.close()
