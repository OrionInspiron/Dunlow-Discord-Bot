import asyncio
import aiohttp
import json

nodes = [
    {"uri": "https://v4.lavalink.info:443", "password": "try_lavalink.info", "identifier": "Lavalink.info"},
    {"uri": "http://lava.link:80", "password": "youshallnotpass", "identifier": "Lava.link"},
    {"uri": "https://lava.link:443", "password": "youshallnotpass", "identifier": "Lava.link HTTPS"},
    {"uri": "http://lavalink.oops.wtf:2000", "password": "www.freelavalink.com", "identifier": "freelavalink"}
]

async def check(session, node):
    try:
        async with session.get(f"{node['uri']}/version", timeout=3.0) as r:
            return f"{node['identifier']}: {r.status} {await r.text()}"
    except Exception as e:
        return f"{node['identifier']}: FAILED - {e}"

async def test():
    async with aiohttp.ClientSession() as session:
        tasks = [check(session, node) for node in nodes]
        results = await asyncio.gather(*tasks)
        for r in results:
            print(r)

loop = asyncio.new_event_loop()
loop.run_until_complete(test())
