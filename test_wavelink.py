import wavelink
import asyncio

async def test():
    n = wavelink.Node(uri="http://0.0.0.0", password="123", identifier="test")
    wavelink.Pool._Pool__nodes["test"] = n
    print("Keys:", wavelink.Pool.nodes.keys())
    
    # Clean up
    del wavelink.Pool._Pool__nodes["test"]
    print("Keys:", wavelink.Pool.nodes.keys())
    await n.close()

asyncio.run(test())
