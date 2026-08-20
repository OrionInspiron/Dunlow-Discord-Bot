import asyncio
import aiohttp
import json

async def test():
    async with aiohttp.ClientSession() as session:
        url = "https://lavalink.darrennathanael.com/api/v1/nodes"
        async with session.get(url) as r:
            data = await r.json()
            
            for d in data:
                if str(d.get('version')).startswith('4'):
                    print(d.get('host'), d.get('port'), d.get('password'), d.get('secure'))
