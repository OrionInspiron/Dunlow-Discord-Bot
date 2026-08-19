import urllib.request, json
try:
    req = urllib.request.Request('https://lavalink-list.ajieblogs.eu.org/All', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        v4_nodes = [n for n in data if n.get('version') == 'v4']
        for i, n in enumerate(v4_nodes[:10]):
            protocol = 'https' if n.get('secure') else 'http'
            print(f"{protocol}://{n['host']}:{n['port']} ({n['password']})")
except Exception as e:
    print(e)
