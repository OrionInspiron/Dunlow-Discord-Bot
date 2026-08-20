import json

with open("cogs/music.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "cls=wavelink.Player" in line:
        print(f"Line {i+1}: {line.strip()}")
