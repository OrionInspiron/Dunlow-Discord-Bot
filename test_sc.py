import asyncio
import aiohttp

async def test():
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": "youshallnotpass"}
        url = "http://lava2.kasawa.pro:2334/v4/loadtracks?identifier=scsearch:loser"
        async with session.get(url, headers=headers) as r:
            print("Kasawa Pro (SoundCloud):", r.status, (await r.text())[:200])

loop = asyncio.new_event_loop()
loop.run_until_complete(test())
