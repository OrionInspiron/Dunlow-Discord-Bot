import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://api.spotifydown.com/metadata/playlist/37i9dQZF1DXcBWIGoYBM5M"
try:
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Origin': 'https://spotifydown.com',
        'Referer': 'https://spotifydown.com/'
    })
    html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
    data = json.loads(html)
    print("Success! Tracks:", len(data.get('trackList', [])))
    if data.get('trackList'):
        print("First track:", data['trackList'][0]['title'], "by", data['trackList'][0]['artists'])
except Exception as e:
    print(e)
