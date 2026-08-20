import discord
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
        
        # We use sys.executable to ensure we restart with the exact same python interpreter
        # sys.argv contains the original arguments passed to the script
        os.execv(sys.executable, ['python'] + sys.argv)

async def setup(bot):
    await bot.add_cog(Owner(bot))
