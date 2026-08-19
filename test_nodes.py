import urllib.request
try:
    req = urllib.request.Request('https://raw.githubusercontent.com/Nonsen-Production/Free-Nodelink-List/main/nodelink.json', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        with open('nodelink.json', 'wb') as f:
            f.write(response.read())
except Exception as e:
    print(f"Error: {e}")
