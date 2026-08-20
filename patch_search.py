import json

with open("cogs/music.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """                try:
                    tracks = await wavelink.Playable.search(search)
                    if not tracks:
                        await ctx.send(f"? **No Tracks Found**\\nCould not find any tracks for: {search}")
                        return"""

replacement = """                try:
                    tracks = await wavelink.Playable.search(search)
                    if not tracks:
                        tracks = await wavelink.Playable.search(search, source=wavelink.TrackSource.SoundCloud)
                    if not tracks:
                        await ctx.send(f"? **No Tracks Found**\\nCould not find any tracks for: {search}")
                        return"""

new_content = content.replace(target, replacement)

if new_content == content:
    print("Failed to replace!")
else:
    with open("cogs/music.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Patched successfully!")
