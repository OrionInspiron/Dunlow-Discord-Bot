import inspect
import asyncio

async def test_task():
    print("Is task?", asyncio.current_task() is not None)

asyncio.run(test_task())
