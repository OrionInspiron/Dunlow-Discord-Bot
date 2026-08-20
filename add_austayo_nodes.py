import urllib.request
import json
import re

url = "https://raw.githubusercontent.com/Austayo/lavalink-list/main/nodes.json"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    data = json.loads(html)
    
    with open("cogs/music.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    for node in data:
        if node.get('version', 'v3') == 'v4':
            uri = f"{"https" if node.get('secure') else "http"}://{node['host']}:{node['port']}"
            password = node['password']
            identifier = f"Austayo ({node['host']})"
            
            node_str = f'{{"uri": "{uri}", "password": "{password}", "identifier": "{identifier}", "retries": 3}}'
            print("Adding:", node_str)
            
            # Insert right before the end of the list
            content = content.replace("        ]\n        \n        # Connect nodes concurrently", f"            {node_str},\n        ]\n        \n        # Connect nodes concurrently")

    with open("cogs/music.py", "w", encoding="utf-8") as f:
        f.write(content)
    
except Exception as e:
    print(e)
