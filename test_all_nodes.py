import asyncio
import aiohttp
import json

async def check(session, node):
    try:
        url = f"http://{node['host']}:{node['port']}/version" if not node['secure'] else f"https://{node['host']}:{node['port']}/version"
        async with session.get(url, timeout=4.0) as r:
            return (node, r.status, await r.text())
    except Exception as e:
        return (node, False, str(e))

async def test():
    async with aiohttp.ClientSession() as session:
        # Fetch Darren's node list
        async with session.get("https://lavalink.darrennathanael.com/api/v1/nodes") as r:
            try:
                nodes = await r.json()
            except:
                nodes = []
        
        # Or from ajieblogs
        if not nodes:
             async with session.get("https://lavalink-list.ajieblogs.eu.org/All") as r:
                try:
                    nodes = (await r.json()).get('nodes', [])
                except:
                    nodes = []

        v4_nodes = [n for n in nodes if str(n.get('version')).startswith('4')]
        
        tasks = [check(session, node) for node in v4_nodes]
        results = await asyncio.gather(*tasks)
        
        working_nodes = []
        for node, status, text in results:
            if status == 200:
                print(f"WORKING: {node['host']}:{node['port']}")
                working_nodes.append(node)
            else:
                pass
                # print(f"FAILED: {node['host']}:{node['port']} - {text}")

