import wavelink
import asyncio
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

async def test():
    n = wavelink.Node(uri="http://0.0.0.0:1234", password="123", identifier="test")
    try:
        await wavelink.Pool.connect(nodes=[n], client=bot, cache_capacity=100)
    except Exception as e:
        print(f"Connection failed: {e}")
        # Wait, if we don't n.close(), it will leak!
        # await n.close()

asyncio.run(test())
