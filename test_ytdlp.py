import yt_dlp
import sys

def extract_flat(search):
    ydl_opts = {'extract_flat': True, 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(search, download=False)

try:
    print("Testing extraction...")
    info = extract_flat("https://www.youtube.com/playlist?list=PLkgWPvg0RClr27zowatUY2YN_FsGUJTbv")
    print("Success. Entries:", len(info.get('entries', [])))
except Exception as e:
    import traceback
    traceback.print_exc()
