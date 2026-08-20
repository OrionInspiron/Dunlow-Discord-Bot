import async_timeout
import asyncio

async def test():
    try:
        async with async_timeout.timeout(None):
            pass
    except Exception as e:
        print(type(e), e)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(test())
