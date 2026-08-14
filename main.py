import os
import asyncio
# pyrefly: ignore [missing-import]
import discord
# pyrefly: ignore [missing-import]
from discord.ext import commands
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="f#", intents=intents, help_command=None)

    async def setup_hook(self):
        # Enable ANSI colors on Windows CMD
        os.system("")
        print("\033[36m" + r"""
   ___               __             ___       __ 
  / _ \__ _____  ___/ /__ _    __  / _ )___  / /_
 / // / // / _ \/ _  / _ \ |/|/ / / _  / _ \/ __/
/____/\_,_/_//_/\_,_/\___/__,__/ /____/\___/\__/ 
                                                 
        """ + "\033[0m")
        print("\033[90m====================================================\033[0m")
        print("\033[33m[SYS]\033[0m Booting up modules...")
        
        # Load cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"\033[32m  [+]\033[0m Loaded extension: \033[36m{filename}\033[0m")
        # Sync slash commands removed as requested
        print("\033[90m====================================================\033[0m")

    async def on_ready(self):
        print(f"\033[35m[BOT]\033[0m Logged in securely as \033[1m{self.user}\033[0m (ID: {self.user.id})")
        print(f"\033[35m[BOT]\033[0m Status: \033[32mONLINE\033[0m | Prefix: \033[36mf#\033[0m")
        print("\033[90m====================================================\033[0m")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='f#help'))

from keep_alive import start_server

async def main():
    bot = Bot()
    discord_token = os.getenv("DISCORD_TOKEN")
    
    if not discord_token or discord_token == "your_discord_bot_token_here":
        print("Please provide a valid DISCORD_TOKEN in the .env file.")
        return

    # Start the dummy web server
    start_server()

    async with bot:
        await bot.start(discord_token)

if __name__ == "__main__":
    asyncio.run(main())
