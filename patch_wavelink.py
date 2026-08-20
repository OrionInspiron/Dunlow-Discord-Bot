import json
import os

# Create a patch for wavelink player to print errors
patch_code = """
import wavelink
import traceback

old_dispatch = wavelink.Player._dispatch_voice_update

async def new_dispatch(self):
    print(f"\033[33m[DEBUG] _dispatch_voice_update called!\033[0m")
    try:
        await old_dispatch(self)
        print(f"\033[32m[DEBUG] _dispatch_voice_update succeeded! Event set: {self._connection_event.is_set()}\033[0m")
    except Exception as e:
        print(f"\033[31m[DEBUG] _dispatch_voice_update FAILED:\033[0m {e}")
        traceback.print_exc()

wavelink.Player._dispatch_voice_update = new_dispatch
"""

with open("main.py", "r") as f:
    content = f.read()

if "old_dispatch" not in content:
    new_content = content.replace("import asyncio", "import asyncio\n" + patch_code)
    with open("main.py", "w") as f:
        f.write(new_content)
    print("Patched main.py")
else:
    print("Already patched")
