import asyncio

async def no_task():
    task = asyncio.create_task(asyncio.sleep(2))
    done, pending = await asyncio.wait([task], timeout=1.0)
    print("Done:", len(done), "Pending:", len(pending))

async def test():
    await no_task()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(test())
finally:
    loop.close()
