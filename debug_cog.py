import json
from discord.ext import commands

async def setup(bot):
    @bot.listen('on_socket_raw_receive')
    async def debug_voice(msg):
        if not isinstance(msg, str):
            msg = msg.decode('utf-8')
        try:
            data = json.loads(msg)
            if data.get('t') in ('VOICE_STATE_UPDATE', 'VOICE_SERVER_UPDATE'):
                print(f"\033[33m[DEBUG DISCORD GATEWAY]\033[0m Received {data['t']}: {data['d']}")
        except:
            pass
