import urllib.request
import json
try:
    req = urllib.request.Request('https://lavalink-list.ajieblogs.eu.org/All', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        found_working = 0
        for item in data:
            if item.get('version') == 'v4':
                protocol = 'https' if item.get('secure') else 'http'
                uri = f"{protocol}://{item['host']}:{item['port']}/v4/info"
                pwd = item['password']
                try:
                    r2 = urllib.request.Request(uri, headers={'Authorization': pwd, 'User-Agent': 'Mozilla/5.0'})
                    res = urllib.request.urlopen(r2, timeout=3)
                    if res.status == 200:
                        print('✅', uri.replace('/v4/info', ''), pwd)
                        found_working += 1
                        if found_working >= 5:
                            break
                except Exception as ex:
                    pass
except Exception as e:
    print(e)
