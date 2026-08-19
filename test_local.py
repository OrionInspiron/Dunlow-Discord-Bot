import re
import urllib.request
import asyncio
import aiohttp

def parse_md(filename):
    nodes = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if '|' in line and not '---' in line and not 'Host' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 3:
                    host = parts[0].replace('`', '')
                    port = parts[1].replace('`', '')
                    pwd = parts[2].replace('`', '')
                    if host and port and pwd and not host.startswith('['):
                        nodes.append((host, port, pwd))
    return nodes

async def check(uri, pwd, identifier):
    base_uri = uri.replace('wss://', 'https://').replace('ws://', 'http://')
    info_uri = f'{base_uri}/v4/info'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(info_uri, headers={'Authorization': pwd}, timeout=3) as resp:
                if resp.status == 200:
                    with open('working_nodes.txt', 'a') as w:
                        w.write(f'WORKING: {uri} | pwd: {pwd} | id: {identifier}\n')
    except:
        pass

async def main():
    nodes = parse_md('lavalink-ssl.md')
    ssl_tasks = [check(f'https://{h}:{p}', pwd, f"{h} (SSL)") for h, p, pwd in nodes]
    nodes2 = parse_md('lavalink-nossl.md')
    nossl_tasks = [check(f'http://{h}:{p}', pwd, f"{h} (HTTP)") for h, p, pwd in nodes2]
    await asyncio.gather(*(ssl_tasks + nossl_tasks))

if __name__ == '__main__':
    asyncio.run(main())
