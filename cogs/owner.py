# pyrefly: ignore [missing-import]
import discord
# pyrefly: ignore [missing-import]
from discord.ext import commands
import sys
import os

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="restart", help="Restarts the bot (Admins/Mods only)")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def restart(self, ctx):
        """Restarts the bot."""
        await ctx.send("Restarting bot...")
        print(f"[SYS] Restart command invoked by {ctx.author}. Restarting...")
        
        # Signal the main script to restart the bot internally instead of spawning new processes.
        # This completely fixes the multiple instances and GUI launcher issues!
        self.bot.should_restart = True
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Owner(bot))
