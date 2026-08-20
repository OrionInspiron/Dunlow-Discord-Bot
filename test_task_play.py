import json

with open("cogs/music.py", "r", encoding="utf-8") as f:
    content = f.read()

new_content = content.replace('async def play(self, ctx, *, search: str):', 'async def play(self, ctx, *, search: str):\n        import asyncio\n        print(f"IS TASK? {asyncio.current_task() is not None}")')

with open("cogs/music.py", "w", encoding="utf-8") as f:
    f.write(new_content)

