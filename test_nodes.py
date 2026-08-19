import asyncio
import aiohttp

async def test():
    urls = [
        "https://lavalinkv4.serenetia.com:443/version",
        "http://lava2.kasawa.pro:2334/version",
        "http://188.245.207.225:2333/version",
        "http://lavalinkv4.serenetia.com:80/version",
        "https://lavalink.jirayu.net:443/version"
    ]
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                async with session.get(url, timeout=5) as resp:
                    print(f"{url}: {resp.status} - {await resp.text()}")
            except Exception as e:
                print(f"{url}: Failed - {e}")

asyncio.run(test())
