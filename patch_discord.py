import json

patch_code = """
import discord
old_on_socket_raw_receive = discord.Client.on_socket_raw_receive

async def new_on_socket_raw_receive(self, msg):
    if not isinstance(msg, str):
        decoded = msg.decode('utf-8')
    else:
        decoded = msg
    try:
        data = __import__('json').loads(decoded)
        if data.get('t') in ('VOICE_STATE_UPDATE', 'VOICE_SERVER_UPDATE'):
            print(f"\033[36m[DEBUG EVENT]\033[0m Received {data['t']}")
    except:
        pass
    if old_on_socket_raw_receive:
        await old_on_socket_raw_receive(self, msg)

discord.Client.on_socket_raw_receive = new_on_socket_raw_receive
"""

with open("main.py", "r") as f:
    content = f.read()

if "old_on_socket_raw_receive" not in content:
    new_content = content.replace("wavelink.Player._dispatch_voice_update = new_dispatch", "wavelink.Player._dispatch_voice_update = new_dispatch\n" + patch_code)
    with open("main.py", "w") as f:
        f.write(new_content)
    print("Patched main.py for gateway events")
else:
    print("Already patched")
