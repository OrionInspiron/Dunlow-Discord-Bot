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
        # Load cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded extension: {filename}")
        
        # Sync slash commands
        await self.tree.sync()
        print("Slash commands synced.")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

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
