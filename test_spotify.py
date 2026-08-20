import yt_dlp

def extract_flat(search):
    class DummyLogger:
        def debug(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): pass
        
    ydl_opts = {'extract_flat': True, 'quiet': True, 'logger': DummyLogger()}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(search, download=False)

try:
    print("Testing Spotify...")
    info = extract_flat("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
    print("Entries:", len(info.get('entries', [])))
    if info.get('entries'):
        print(info['entries'][0])
except Exception as e:
    import traceback
    traceback.print_exc()
