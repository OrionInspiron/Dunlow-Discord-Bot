import asyncio
import aiohttp

nodes = [
    {"uri": "http://node.itzrandom.cloud:9000", "password": "lavalink@itzrandomcloud", "identifier": "itzrandom"},
    {"uri": "http://v4.bloggertasher.ru:26040", "password": "apexnodes.xyz", "identifier": "bloggertasher"},
    {"uri": "http://LavaLink4.lightsout.in:40069", "password": "LightsoutOwnsElves", "identifier": "lightsout"},
    {"uri": "https://v4.lavalink.rocks:443", "password": "horizxon.tech", "identifier": "lavalink.rocks"}
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
