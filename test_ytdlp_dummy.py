import sys
import yt_dlp

class DummyLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def extract_flat(search):
    ydl_opts = {
        'extract_flat': True, 
        'quiet': True,
        'logger': DummyLogger()
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(search, download=False)
