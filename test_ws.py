import asyncio
import aiohttp

async def test():
    url = "wss://lavalinkv4.serenetia.com:443/v4/websocket"
    headers = {
        "Authorization": "https://seretia.link/discord",
        "Client-Name": "Wavelink/3.1.2"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.ws_connect(url, headers=headers) as ws:
                print("WS Connected!")
                await ws.close()
        except Exception as e:
            print(f"WS Failed: {e}")

asyncio.run(test())
