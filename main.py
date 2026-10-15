import os
import sys
import asyncio
import aiohttp
# pyrefly: ignore [missing-import]
import discord
# pyrefly: ignore [missing-import]
from discord.ext import commands
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

from keep_alive import start_server

load_dotenv()


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="f#", intents=intents, help_command=None)
        self.should_restart = False

    async def close(self):
        # Gracefully disconnect any active voice clients
        for vc in list(self.voice_clients):
            try:
                await vc.disconnect(force=True)
            except Exception:
                pass
        await super().close()

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
        
        # Load cogs dynamically
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog_name = f"cogs.{filename[:-3]}"
                if cog_name in sys.modules:
                    del sys.modules[cog_name]
                await self.load_extension(cog_name)
                print(f"\033[32m  [+]\033[0m Loaded extension: \033[36m{filename}\033[0m")
        print("\033[90m====================================================\033[0m")

    async def on_ready(self):
        print(f"\033[35m[BOT]\033[0m Logged in securely as \033[1m{self.user}\033[0m (ID: {self.user.id})")
        print(f"\033[35m[BOT]\033[0m Status: \033[32mONLINE\033[0m | Prefix: \033[36mf#\033[0m")
        print("\033[90m====================================================\033[0m")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="Soothing Melodies 📻 | f#help"
            )
        )


async def main():
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token or discord_token == "your_discord_bot_token_here":
        print("Please provide a valid DISCORD_TOKEN in the .env file.")
        return

    # Start healthcheck web server for 24/7 uptime monitoring
    start_server()

    retry_delay = 5
    while True:
        bot = Bot()
        try:
            async with bot:
                await bot.start(discord_token)
        except (discord.ConnectionClosed, discord.GatewayNotFound, aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"[SYS] Connection dropped ({type(e).__name__}: {e}). Reconnecting in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(int(retry_delay * 1.5), 30)
            continue
        except Exception as e:
            print(f"[SYS] Unexpected bot exception ({type(e).__name__}: {e}). Reconnecting in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(int(retry_delay * 1.5), 30)
            continue
        else:
            retry_delay = 5

        if bot.should_restart:
            print("[SYS] Bot is restarting internally... Please wait.")
            await asyncio.sleep(2)
            continue
        else:
            print("[SYS] Bot session disconnected. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
            continue


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n[SYS] Bot stopped gracefully.")
