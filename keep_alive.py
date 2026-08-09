from aiohttp import web
import asyncio

async def handle(request):
    return web.Response(text="Bot is alive!")

async def run_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render assigns a port dynamically via the PORT environment variable. Defaults to 8080.
    import os
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

def start_server():
    loop = asyncio.get_event_loop()
    loop.create_task(run_server())
