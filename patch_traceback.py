import json

with open("cogs/music.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the print statement in the except block to print traceback
new_content = content.replace('print(f"Error in play command: {repr(e)}")', 'import traceback\ntraceback.print_exc()')

with open("cogs/music.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Patched music.py to print full traceback")
