import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://lavalink-list-api.ajieblogs.eu.org/v4"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
    data = json.loads(html)
    
    print("Found nodes:", len(data))
    for node in data[:10]:
        print(f'{{"uri": "{"https" if node.get("secure") else "http"}://{node["host"]}:{node["port"]}", "password": "{node["password"]}", "identifier": "{node["host"]}"}}')
except Exception as e:
    print("API 1 Failed:", e)
