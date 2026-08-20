import urllib.request
import re
import ssl
import json
import base64

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')

# The tracks might be embedded in a <script type="application/json"> tag?
# Or maybe the tracks are in a meta tag
tracks = re.findall(r'<meta property="music:song" content="https://open.spotify.com/track/([^"]+)"', html)
print(f"Found {len(tracks)} tracks via meta tag")

# How about the script tags?
for script in re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
    if "Spotify.Entity" in script or "Spotify.I18n" in script or "initialState" in script:
        print("Found possible state block")
