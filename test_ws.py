import asyncio
import aiohttp

async def test_node(uri, pwd):
    ws_uri = uri.replace('http://', 'ws://').replace('https://', 'wss://') + '/v4/websocket'
    headers = {
        'Authorization': pwd,
        'User-Id': '123456789',
        'Client-Name': 'Wavelink/3.2.0'
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_uri, headers=headers, timeout=5) as ws:
                print(f'? {uri} - WS CONNECTED SUCCESSFULLY!')
                await ws.close()
    except aiohttp.WSServerHandshakeError as e:
        print(f'Handshake Error {uri}: {e.status}')
    except Exception as e:
        print(f'Error {uri}: {e}')

async def main():
    await test_node('http://lava2.kasawa.pro:2334', 'youshallnotpass')
    await test_node('http://lavalink.jirayu.net:13592', 'youshallnotpass')

asyncio.run(main())
