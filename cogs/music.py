import os
# pyrefly: ignore [missing-import]
import discord
# pyrefly: ignore [missing-import]
import motor.motor_asyncio
import json
# pyrefly: ignore [missing-import]
from discord.ext import commands
# pyrefly: ignore [missing-import]
from discord import app_commands
# pyrefly: ignore [missing-import]
import wavelink
# pyrefly: ignore [missing-import]
import yt_dlp
import asyncio
# pyrefly: ignore [missing-import]
import aiohttp
import urllib.parse
import math
import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

async def get_stream_url(query: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
    }
    def get_info():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                return info['entries'][0]
            return info
            
    info = await asyncio.to_thread(get_info)
    return info['url'], info.get('title', 'Unknown Track')

class QueuePaginationView(discord.ui.View):
    def __init__(self, embeds, timeout=120):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embeds) - 1

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

class PlayerUI(discord.ui.View):
    def __init__(self, music_cog):
        super().__init__(timeout=None)
        self.music_cog = music_cog

    @discord.ui.button(label="⏮️ Previous", style=discord.ButtonStyle.secondary, custom_id="music_previous")
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            return await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
            
        if not interaction.user.voice or interaction.user.voice.channel != player.channel:
            return await interaction.response.send_message("You must be in the same voice channel.", ephemeral=True)

        if not player.queue.history:
            return await interaction.response.send_message("There is no previous song in the history.", ephemeral=True)

        # Re-queue the currently playing song to the front so it's not lost
        if player.current:
            player.queue.put_at(0, player.current)
            
        # Get and remove the most recently played track from history
        previous_track = player.queue.history[-1]
        del player.queue.history[-1]
        
        await player.play(previous_track)
        await interaction.response.send_message("⏮️ Playing previous track.", ephemeral=False)

    @discord.ui.button(label="⏯️ Play/Pause", style=discord.ButtonStyle.primary, custom_id="music_play_pause")
    async def play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            return await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
            
        await player.pause(not player.paused)
        status = "Paused" if player.paused else "Resumed"
        await interaction.response.send_message(f"**{status}** the music.", ephemeral=True)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.secondary, custom_id="music_skip")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player or not getattr(player, "playing", False):
            return await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
            
        if not interaction.user.voice or interaction.user.voice.channel != player.channel:
            return await interaction.response.send_message("You must be in the same voice channel to skip.", ephemeral=True)

        import time
        import math
        last_skip = self.music_cog.last_skip.get(interaction.guild.id, 0)
        if time.time() - last_skip < 4.0:
            return await interaction.response.send_message("⏳ The server is currently buffering the next song. Please wait!", ephemeral=True)

        members = [m for m in player.channel.members if not m.bot]
        required_votes = math.ceil(len(members) / 2)

        is_dj = any(role.name.lower() == "dj" for role in interaction.user.roles)
        
        if len(members) <= 1 or interaction.user.guild_permissions.manage_channels or is_dj:
            self.music_cog.last_skip[interaction.guild.id] = time.time()
            
            await player.skip(force=True)
            await interaction.response.send_message("⏭️ Force-skipped the track.", ephemeral=False)
            return

        if interaction.guild.id not in self.music_cog.skip_votes:
            self.music_cog.skip_votes[interaction.guild.id] = set()

        if interaction.user.id in self.music_cog.skip_votes[interaction.guild.id]:
            return await interaction.response.send_message(f"You have already voted to skip! ({len(self.music_cog.skip_votes[interaction.guild.id])}/{required_votes} votes needed)", ephemeral=True)

        self.music_cog.skip_votes[interaction.guild.id].add(interaction.user.id)
        current_votes = len(self.music_cog.skip_votes[interaction.guild.id])

        if current_votes >= required_votes:
            self.music_cog.skip_votes[interaction.guild.id].clear()
            self.music_cog.last_skip[interaction.guild.id] = time.time()
            
            await player.skip(force=True)
                
            await interaction.response.send_message(f"⏭️ Vote passed ({current_votes}/{required_votes}). Skipped the track!", ephemeral=False)
        else:
            await interaction.response.send_message(f"🗳️ {interaction.user.mention} voted to skip! ({current_votes}/{required_votes} votes needed)", ephemeral=False)

    @discord.ui.button(label="🔁 Loop", style=discord.ButtonStyle.secondary, custom_id="music_loop")
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            return await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
            
        if player.queue.mode == wavelink.QueueMode.loop:
            player.queue.mode = wavelink.QueueMode.normal
            await interaction.response.send_message("🔁 Loop **Disabled**.", ephemeral=True)
        else:
            player.queue.mode = wavelink.QueueMode.loop
            await interaction.response.send_message("🔁 Loop **Enabled**.", ephemeral=True)
            
    @discord.ui.button(label="🔀 Shuffle", style=discord.ButtonStyle.secondary, custom_id="music_shuffle")
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            return await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
            
        if player.queue.is_empty:
            return await interaction.response.send_message("The queue is empty!", ephemeral=True)
            
        player.queue.shuffle()
        await interaction.response.send_message("🔀 Shuffled the queue!", ephemeral=False)
            
    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger, custom_id="music_stop")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            return await interaction.response.send_message("Nothing is playing right now.", ephemeral=True)
            
        is_dj = any(role.name.lower() == "dj" for role in interaction.user.roles)
        if not (interaction.user.guild_permissions.manage_channels or is_dj):
            return await interaction.response.send_message("You need 'Manage Channels' permissions or a 'DJ' role to stop the player.", ephemeral=True)
            
        self.music_cog.intentional_leaves.add(interaction.guild.id)
        player.queue.clear()
        await player.disconnect()
        await interaction.response.send_message("⏹️ Stopped the music and cleared the queue.", ephemeral=False)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ui_messages = {}
        self.text_channels = {}
        self.stay_connected = {} # guild_id -> bool
        self.intentional_leaves = set() # guild_ids that were explicitly told to leave
        self.skip_votes = {} # guild_id -> set(user_ids)
        self.last_skip = {} # guild_id -> timestamp
        self.rejoin_attempts = {} # guild_id -> list of timestamps
        self.ui_messages = {} # guild_id -> discord.Message
        self.db = None

    async def cog_load(self):
        self.bot.loop.create_task(self.start_nodes())
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["music_bot"]["playlists"]
        self.history_col = self.mongo_client["music_bot"]["play_history"]

    async def cog_unload(self):
        if hasattr(self, 'mongo_client'):
            self.mongo_client.close()

    async def start_nodes(self):

        # Node 1 (Jirayu)
        node1 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_1", "http://lavalink.jirayu.net:13592"), 
            password=os.getenv("LAVALINK_PASSWORD_1", "youshallnotpass"),
            retries=3
        )

        # Node 2 (Amane)
        node2 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_2", "http://lavalinkv4.serenetia.com:80"), 
            password=os.getenv("LAVALINK_PASSWORD_2", "https://seretia.link/discord"),
            retries=3
        )

        # Node 3 (Tapao 1)
        node3 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_3", "http://sg1-nodelink.nyxbot.app:3000"), 
            password=os.getenv("LAVALINK_PASSWORD_3", "nyxbot.app/support"),
            retries=3
        )

        # Node 4 (Tapao 2)
        node4 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_4", "http://sg2-nodelink.nyxbot.app:3000"), 
            password=os.getenv("LAVALINK_PASSWORD_4", "nyxbot.app/support"),
            retries=3
        )

        # Node 5 (G3V)
        node5 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_5", "http://lava.g3v.co.uk:9008"), 
            password=os.getenv("LAVALINK_PASSWORD_5", "lavalinklol"),
            retries=3
        )

        # Node 6 (Trinium 1)
        node6 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_6", "http://lavalink.triniumhost.com:4333"), 
            password=os.getenv("LAVALINK_PASSWORD_6", "free"),
            retries=3
        )

        # Node 7 (Trinium 2)
        node7 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_7", "http://lavalink.triniumhost.com:2333"), 
            password=os.getenv("LAVALINK_PASSWORD_7", "kirito"),
            retries=3
        )

        # Node 8 (Trinium 3)
        node8 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_8", "http://lavalink.triniumhost.com:9008"), 
            password=os.getenv("LAVALINK_PASSWORD_8", "free"),
            retries=3
        )

        # Node 9 (Trinium 4)
        node9 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_9", "http://lavalink.triniumhost.com:6000"), 
            password=os.getenv("LAVALINK_PASSWORD_9", "trinium"),
            retries=3
        )

        # Node 10 (Nexcloud)
        node10 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_10", "http://n3.nexcloud.in:2026"), 
            password=os.getenv("LAVALINK_PASSWORD_10", "nexcloud"),
            retries=3
        )

        # Node 11 (VexaNode)
        node11 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_11", "http://omega.vexanode.cloud:2031"), 
            password=os.getenv("LAVALINK_PASSWORD_11", "https://discord.vexanode.cloud"),
            retries=3
        )

        # Node 12 (Kasawa)
        node12 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_12", "http://lava2.kasawa.pro:2334"), 
            password=os.getenv("LAVALINK_PASSWORD_12", "youshallnotpass"),
            retries=3
        )

        # Node 13 (MineCuta)
        node13 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_13", "http://lavav4.minecuta.com:2333"), 
            password=os.getenv("LAVALINK_PASSWORD_13", "discord.gg/gKuXdHs"),
            retries=3
        )

        # Node 14 (East112)
        node14 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_14", "http://157.254.192.15:2333"), 
            password=os.getenv("LAVALINK_PASSWORD_14", "youshallnotpass"),
            retries=3
        )

        # Wavelink will automatically switch to the next available node if one fails/crashes!
        try:
            nodes_list = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14]
            await wavelink.Pool.connect(nodes=nodes_list, client=self.bot, cache_capacity=100)
        except Exception as e:
            print(f"Failed to connect to one or more nodes: {e}")

    async def setup_sponsorblock(self, player: wavelink.Player):
        node = player.node
        url = f"{node.uri}/v4/sessions/{node.session_id}/players/{player.guild.id}/sponsorblock/categories"
        categories = ["sponsor", "interaction", "selfpromo"]
        headers = {"Authorization": node.password}
        try:
            async with node.client.session.put(url, json=categories, headers=headers) as resp:
                pass
        except Exception as e:
            print(f"SponsorBlock error: {e}")

    @commands.Cog.listener()
    async def on_wavelink_extra_event(self, payload: wavelink.ExtraEventPayload):
        if payload.event == "SponsorBlockSegmentSkipped":
            player = payload.player
            if player and hasattr(player, "text_channel") and player.text_channel:
                await player.text_channel.send(embed=self.create_embed("⏭️ Sponsor Skipped", "Automatically skipped a sponsor/promo segment!", discord.Color.green()))

    def create_embed(self, title, description="", color=discord.Color.blurple()):
        return discord.Embed(title=title, description=description, color=color)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Ignore other users
        if member.id != self.bot.user.id:
            return
            
        # If the bot was completely disconnected from a channel
        if before.channel is not None and after.channel is None:
            # Check if it was an intentional disconnect (like using the stop command or empty queue without 24/7)
            if member.guild.id in self.intentional_leaves:
                self.intentional_leaves.discard(member.guild.id)
                return
                
            # Otherwise, Discord or the Node dropped the connection. 
            # If 24/7 mode is enabled, forcefully rejoin!
            is_247 = self.stay_connected.get(member.guild.id, True)
            if is_247:
                import time
                now = time.time()
                attempts = self.rejoin_attempts.get(member.guild.id, [])
                attempts = [t for t in attempts if now - t < 20] # Keep last 20 seconds
                
                if len(attempts) >= 3:
                    self.stay_connected[member.guild.id] = False
                    self.rejoin_attempts[member.guild.id] = []
                    channel = self.bot.get_channel(before.channel.id)
                    if channel and hasattr(channel, "guild"):
                        # Try to send a message to the first text channel we can find if it's a loop
                        for txt in channel.guild.text_channels:
                            if txt.permissions_for(channel.guild.me).send_messages:
                                await txt.send(embed=self.create_embed("⚠️ Loop Detected", "I was kicked or disconnected too many times in a row. 24/7 mode has been temporarily disabled.", discord.Color.red()))
                                break
                    return
                
                attempts.append(now)
                self.rejoin_attempts[member.guild.id] = attempts
                
                try:
                    # Give discord a tiny moment to clean up the old ghost connection
                    await asyncio.sleep(2)
                    player = await before.channel.connect(cls=wavelink.Player)
                    player.autoplay = wavelink.AutoPlayMode.enabled
                    player.inactive_timeout = 0
                    player.inactive_channel_tokens = 0
                    await self.setup_sponsorblock(player)
                    print(f"Auto-rejoined {before.channel.name} due to 24/7 mode.")
                except Exception as e:
                    print(f"Failed to auto-rejoin: {e}")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        print(f"Wavelink Node connected: {payload.node!r} | Resumed: {payload.resumed}")

    @commands.Cog.listener()
    async def on_wavelink_node_disconnected(self, payload: wavelink.NodeDisconnectedEventPayload):
        print(f"Wavelink Node disconnected: {payload.node.identifier}. Attempting player migration...")
        
        for vc in self.bot.voice_clients:
            if isinstance(vc, wavelink.Player) and vc.node == payload.node:
                try:
                    # Get a new healthy node from the pool
                    new_node = wavelink.Pool.get_node()
                    if new_node and new_node != payload.node:
                        print(f"Migrating player for guild {vc.guild.id} to new node: {new_node.identifier}")
                        
                        # Store current playback state
                        current_track = vc.current
                        current_position = vc.position
                        
                        # Actually switch the player to the new healthy node
                        await vc.switch_node(new_node)
                        
                        # Resume exactly where it left off
                        if current_track:
                            await vc.play(current_track, start=current_position)
                            
                        # Send a message to the text channel if available
                        text_channel = getattr(vc, "text_channel", None)
                        if text_channel:
                            await text_channel.send(embed=self.create_embed(
                                "🔄 Server Failover",
                                f"Disconnected from the old server. Now connected to `{new_node.identifier}` to keep the music playing!",
                                discord.Color.orange()
                            ))
                        else:
                            print(f"Could not announce node switch in guild {vc.guild.id} because text_channel was not set.")
                except Exception as e:
                    print(f"Failed to migrate player for guild {vc.guild.id}: {e}")

    def create_player_embed(self, player, track):
        duration_str = "Live Stream"
        
        if track.length:
            position_ms = player.position
            length_ms = track.length
            
            pos_seconds = int(position_ms // 1000)
            len_seconds = int(length_ms // 1000)
            
            pos_str = f"{pos_seconds // 60:02d}:{pos_seconds % 60:02d}"
            len_str = f"{len_seconds // 60:02d}:{len_seconds % 60:02d}"
            
            bar_length = 20
            percent = position_ms / length_ms if length_ms > 0 else 0
            percent = max(0.0, min(1.0, percent))
            
            filled_length = int(bar_length * percent)
            empty_length = max(0, bar_length - filled_length - 1)
            
            bar = "=" * filled_length + "🔘" + "-" * empty_length
            if filled_length == bar_length:
                bar = "=" * bar_length
                
            duration_str = f"`{pos_str}` [{bar}] `{len_str}`"
            
        embed = discord.Embed(
            title="🎧 Now Playing",
            description=f"**[{track.title}]({track.uri})**\n\n👤 **Artist:** {track.author}\n{duration_str}",
            color=discord.Color.from_rgb(114, 137, 218) # Discord Blurple
        )
        if getattr(track, "artwork", None):
            embed.set_thumbnail(url=track.artwork)
            
        return embed

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        player = payload.player
        
        # In Wavelink 3/4, sometimes player custom attributes get wiped on node migrations.
        # So we fetch the text_channel from our dictionary fallback if it's missing on the player itself.
        text_channel = getattr(player, "text_channel", None)
        if not text_channel and player.guild.id in getattr(self, "text_channels", {}):
            text_channel = self.text_channels[player.guild.id]
            player.text_channel = text_channel # Restore it

        if not text_channel:
            # Absolute fallback: Find the first channel the bot can send messages in
            for channel in player.guild.text_channels:
                if channel.permissions_for(player.guild.me).send_messages:
                    text_channel = channel
                    player.text_channel = channel
                    print(f"Used hard fallback channel: {channel.name}")
                    break

        if not text_channel:
            print(f"CRITICAL ERROR: Absolutely no text_channel found for PlayerUI in guild {player.guild.id}")
            return
            
        print(f"DEBUG: on_wavelink_track_start fired for track {payload.track.title}")
        
        # Reset skip votes for the new track
        if player.guild.id in self.skip_votes:
            self.skip_votes[player.guild.id].clear()
            
        track = payload.track
        

        try:
            # Create a premium-looking embed
            embed = self.create_player_embed(player, track)
            
            # Delete old UI message
            old_msg = self.ui_messages.get(player.guild.id)
            if old_msg:
                try:
                    await old_msg.delete()
                except Exception:
                    pass
                    
            # Send new UI
            view = PlayerUI(self)
            msg = await text_channel.send(embed=embed, view=view)
            self.ui_messages[player.guild.id] = msg
        except Exception as e:
            print(f"CRITICAL ERROR Sending Player UI: {e}")

        # Log to MongoDB in the background so it doesn't delay the UI!
        async def log_to_db():
            requester_id = getattr(track.extras, "requester_id", None) if hasattr(track, "extras") else None
            if not requester_id and hasattr(track, "requester"):
                 requester_id = track.requester
                 
            try:
                await self.history_col.insert_one({
                    "guild_id": player.guild.id,
                    "track_title": track.title,
                    "artist": track.author,
                    "requester_id": requester_id,
                    "played_at": datetime.datetime.now(datetime.timezone.utc)
                })
            except Exception as e:
                print(f"Failed to log track to MongoDB: {e}")
                
        self.bot.loop.create_task(log_to_db())

        async def update_player_ui():
            nonlocal msg
            try:
                while True:
                    await asyncio.sleep(5)
                    if not player or not getattr(player, "playing", False):
                        break
                    if player.current != track:
                        break
                        
                    updated_embed = self.create_player_embed(player, track)
                    try:
                        if player.text_channel.last_message_id != msg.id:
                            try:
                                await msg.delete()
                            except:
                                pass
                            view = PlayerUI(self)
                            msg = await player.text_channel.send(embed=updated_embed, view=view)
                            self.ui_messages[player.guild.id] = msg
                        else:
                            await msg.edit(embed=updated_embed)
                    except discord.NotFound:
                        break
                    except discord.HTTPException:
                        pass
            except Exception as e:
                print(f"Error updating UI: {e}")
                
        self.bot.loop.create_task(update_player_ui())

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = payload.player
        if not player:
            return

        # Wavelink 3 natively plays the next song from the queue.
        # We only need to handle disconnecting when the queue is completely finished.
        if payload.reason != "FINISHED":
            return
            
        is_247 = self.stay_connected.get(player.guild.id, True)
        if not is_247 and player.queue.is_empty:
            await asyncio.sleep(5) # Wait 5s before leaving to ensure no new songs were added
            if player.queue.is_empty and not player.playing:
                await player.disconnect()
                if hasattr(player, "text_channel"):
                    await player.text_channel.send(embed=self.create_embed("👋 Disconnected", "Queue is empty. Use `f#247` to make me stay forever!"))

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, payload: wavelink.TrackExceptionEventPayload):
        player = payload.player
        if not player:
            return
            
        track = payload.track
        
        # Prevent infinite loops if this is the only song left in the queue
        if player.queue.is_empty:
            if hasattr(player, "text_channel") and player.text_channel:
                await player.text_channel.send(embed=self.create_embed("⚠️ Track Error", f"Failed to play **{track.title}**. It has been removed from the queue to prevent looping.", discord.Color.red()))
        else:
            player.queue.put(track)
            if hasattr(player, "text_channel") and player.text_channel:
                await player.text_channel.send(embed=self.create_embed("⚠️ Track Error", f"Failed to play **{track.title}** due to a server error. I've moved it to the end of the playlist to try again later!", discord.Color.orange()))

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, payload: wavelink.TrackStuckEventPayload):
        player = payload.player
        if not player:
            return
            
        track = payload.track
        
        # Prevent infinite loops if this is the only song left in the queue
        if player.queue.is_empty:
            if hasattr(player, "text_channel") and player.text_channel:
                await player.text_channel.send(embed=self.create_embed("⚠️ Track Stuck", f"**{track.title}** got stuck loading. It has been removed from the queue to prevent looping.", discord.Color.red()))
        else:
            player.queue.put(track)
            if hasattr(player, "text_channel") and player.text_channel:
                await player.text_channel.send(embed=self.create_embed("⚠️ Track Stuck", f"**{track.title}** got stuck loading. I've moved it to the end of the playlist to try again later!", discord.Color.orange()))



    @commands.command(name="247", help="Toggles 24/7 mode (stay in channel when queue is empty).")
    async def toggle_247(self, ctx):
        # Default is True, toggle it
        current = self.stay_connected.get(ctx.guild.id, True)
        self.stay_connected[ctx.guild.id] = not current
        
        status = "Enabled ✅" if self.stay_connected[ctx.guild.id] else "Disabled ❌"
        await ctx.send(embed=self.create_embed("🕒 24/7 Mode", f"24/7 mode is now **{status}**.", discord.Color.gold()))

    @commands.command(name="join", help="Joins your current voice channel.")
    async def join(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=self.create_embed("❌ Error", "You must be in a voice channel to use this command.", discord.Color.red()))

        vc = ctx.author.voice.channel
        player = ctx.guild.voice_client

        try:
            if not player:
                player = await vc.connect(cls=wavelink.Player)
                player.autoplay = wavelink.AutoPlayMode.disabled
                player.inactive_timeout = 0
                player.inactive_channel_tokens = 0
                await self.setup_sponsorblock(player)
                await ctx.send(embed=self.create_embed("✅ Joined Channel", f"Successfully joined {vc.mention}\n📡 **Connected to server:** `{player.node.identifier}`"))
            elif player.channel.id != vc.id:
                await player.move_to(vc)
                await ctx.send(embed=self.create_embed("✅ Moved Channel", f"Moved to {vc.mention}\n📡 **Current server:** `{player.node.identifier}`"))
            else:
                await ctx.send(embed=self.create_embed("ℹ️ Info", f"I am already in your voice channel.\n📡 **Current server:** `{player.node.identifier}`", discord.Color.gold()))
        except Exception as e:
            if "ChannelTimeoutException" in type(e).__name__ or "timeout" in str(e).lower():
                await ctx.send(embed=self.create_embed("⚠️ Discord Voice Lag", "Discord's voice servers took too long to respond. Try again or change your Voice Channel's region!", discord.Color.orange()))
            else:
                await ctx.send(embed=self.create_embed("❌ Error", f"Failed to join: {e}", discord.Color.red()))

    @commands.command(name="play", help="Plays a track from YouTube or a URL.", aliases=['p'])
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send(embed=self.create_embed("❌ Error", "You must be in a voice channel to use this command.", discord.Color.red()))

        try:
            vc = ctx.author.voice.channel
            player = ctx.guild.voice_client
            
            if not player:
                player = await vc.connect(cls=wavelink.Player)
                player.autoplay = wavelink.AutoPlayMode.partial
                player.inactive_timeout = 0
                player.inactive_channel_tokens = 0
                await self.setup_sponsorblock(player)
                await ctx.send(embed=self.create_embed("✅ Joined Channel", f"Successfully joined {vc.mention}\n📡 **Connected to server:** `{player.node.identifier}`"))
            elif player.channel.id != vc.id:
                await player.move_to(vc)
                await ctx.send(embed=self.create_embed("✅ Moved Channel", f"Moved to {vc.mention}\n📡 **Current server:** `{player.node.identifier}`"))

            player.text_channel = ctx.channel
            self.text_channels[ctx.guild.id] = ctx.channel

            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    tracks = await wavelink.Playable.search(search)
                    if not tracks:
                        return await ctx.send(embed=self.create_embed("❌ No Tracks Found", f"Could not find any tracks for: `{search}`", discord.Color.red()))

                    if isinstance(tracks, wavelink.Playlist):
                        added = list(tracks)
                        
                        # Filter out duplicates within the playlist and those already in queue
                        existing_uris = set()
                        if player.current:
                            existing_uris.add(player.current.uri)
                        for q_track in player.queue:
                            existing_uris.add(q_track.uri)
                            
                        unique_tracks = []
                        for t in added:
                            if t.uri not in existing_uris:
                                unique_tracks.append(t)
                                existing_uris.add(t.uri)
                
                        if not unique_tracks:
                            return await ctx.send(embed=self.create_embed("ℹ️ Already in Queue", "All songs from this playlist are already in your queue!", discord.Color.gold()))

                        # If idle, play the first track explicitly and queue the rest
                        if not player.playing:
                            await player.set_volume(30)
                            await player.play(unique_tracks[0])
                            for t in unique_tracks[1:]:
                                player.queue.put(t)
                        else:
                            for t in unique_tracks:
                                player.queue.put(t)
                        
                        skipped = len(added) - len(unique_tracks)
                        skipped_msg = f" (Skipped {skipped} duplicates)" if skipped > 0 else ""
                        
                        # Wavelink 3 Playlist doesn't have a name attribute, so we just say "A playlist"
                        playlist_name = getattr(tracks, "name", "A playlist")
                        await ctx.send(embed=self.create_embed("✅ Playlist Added", f"Added **{playlist_name}** ({len(unique_tracks)} new tracks) to the queue.{skipped_msg}", discord.Color.green()))
                    else:
                        track = tracks[0]
                        
                        # Check if the track is currently playing or in the queue
                        is_duplicate = False
                        if player.current and player.current.uri == track.uri:
                            is_duplicate = True
                        else:
                            for q_track in player.queue:
                                if q_track.uri == track.uri:
                                    is_duplicate = True
                                    break
                                    
                        if is_duplicate:
                            return await ctx.send(embed=self.create_embed("ℹ️ Already in Queue", f"The song **{track.title}** is already in your queue! You can use `f#skipto {track.title}` to play that song.", discord.Color.gold()))

                        if not player.playing:
                            await player.set_volume(30)
                            await player.play(track)
                            pass # UI is handled automatically by on_wavelink_track_start
                        else:
                            player.queue.put(track)
                            embed = discord.Embed(title="✅ Added to Queue", description=f"**[{track.title}]({track.uri})**", color=discord.Color.green())
                            await ctx.send(embed=embed)
                            
                    break # success, exit retry loop
                    
                except Exception as inner_e:
                    error_msg = str(inner_e)
                    is_rate_limit = "429" in error_msg or "mimetype: text/plain" in error_msg or "502" in error_msg or "500" in error_msg
                    
                    if is_rate_limit and attempt < max_attempts - 1:
                        bad_node = getattr(player, "node", None)
                        if bad_node:
                            print(f"Rate limit/Error hit on {bad_node.uri}. Closing node to force failover...")
                            try:
                                await bad_node.close()
                            except:
                                pass
                        
                        await ctx.send(embed=self.create_embed("🔄 Automatic Failover", "The primary server was overloaded. Instantly switching to a backup server and retrying...", discord.Color.gold()))
                        await asyncio.sleep(2)
                        continue
                    else:
                        raise inner_e # Exhausted retries or non-recoverable, pass to outer except block
                
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            error_msg = str(e) or type(e).__name__
            if "502" in error_msg or "500" in error_msg or "text/html" in error_msg:
                await ctx.send(embed=self.create_embed("⚠️ Server Overloaded", "The public music servers are currently experiencing heavy traffic and rejected the request. Please try playing the song again in a few seconds!", discord.Color.gold()))
            elif error_msg == "None" or "LavalinkLoadException" in type(e).__name__:
                await ctx.send(embed=self.create_embed("⚠️ YouTube Blocked", "The public music server was temporarily blocked by YouTube for requesting too many songs at once (Rate Limited). Try using a Spotify playlist instead, or wait a few minutes!", discord.Color.orange()))
            elif "ChannelTimeoutException" in type(e).__name__ or "timeout" in error_msg.lower():
                await ctx.send(embed=self.create_embed("⚠️ Discord Voice Lag", "Discord's voice servers took too long to respond. Try again or change your Voice Channel's region!", discord.Color.orange()))
            else:
                await ctx.send(embed=self.create_embed("❌ Error Debug", f"Error: {error_msg}\n```py\n{tb[:3000]}\n```", discord.Color.red()))
            print(f"Error in play command: {repr(e)}")

    @commands.command(name="skip", help="Skips the current track.", aliases=['s'])
    async def skip(self, ctx):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        import time
        last_skip = self.last_skip.get(ctx.guild.id, 0)
        if time.time() - last_skip < 4.0:
            return await ctx.send(embed=self.create_embed("⏳ Loading", "The server is currently buffering the next song. Please wait a few seconds!", discord.Color.gold()), delete_after=5)
            
        if not ctx.author.voice or ctx.author.voice.channel != player.channel:
            return await ctx.send(embed=self.create_embed("❌ Error", "You must be in the same voice channel to skip.", discord.Color.red()))

        # Get the number of real members in the voice channel
        members = [m for m in player.channel.members if not m.bot]
        required_votes = math.ceil(len(members) / 2)

        # Allow immediate skip if:
        # - The requester is the only real person in the channel
        # - The requester has manage_channels permissions (Admin/DJ)
        if len(members) <= 1 or ctx.author.guild_permissions.manage_channels:
            self.last_skip[ctx.guild.id] = time.time()
            
            await player.skip(force=True)
                    
            await ctx.send(embed=self.create_embed("⏭️ Skipped", "Forced skip by Admin/DJ."))
            return

        # Initialize vote set for the guild if not exists
        if ctx.guild.id not in self.skip_votes:
            self.skip_votes[ctx.guild.id] = set()

        if ctx.author.id in self.skip_votes[ctx.guild.id]:
            return await ctx.send(embed=self.create_embed("❌ Error", f"You have already voted! ({len(self.skip_votes[ctx.guild.id])}/{required_votes} votes needed)", discord.Color.red()))

        self.skip_votes[ctx.guild.id].add(ctx.author.id)
        current_votes = len(self.skip_votes[ctx.guild.id])

        if current_votes >= required_votes:
            self.skip_votes[ctx.guild.id].clear()
            self.last_skip[ctx.guild.id] = time.time()
            
            await player.skip(force=True)
                    
            await ctx.send(embed=self.create_embed("⏭️ Skipped", f"Vote passed ({current_votes}/{required_votes}). Skipping the track!"))
        else:
            await ctx.send(embed=self.create_embed("🗳️ Skip Vote", f"{ctx.author.mention} has voted to skip! ({current_votes}/{required_votes} votes needed)", discord.Color.gold()))

    @commands.command(name="pause", help="Pauses the current track.")
    async def pause(self, ctx):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        await player.pause(True)
        await ctx.send(embed=self.create_embed("⏸️ Paused", "The music has been paused."))

    @commands.command(name="resume", help="Resumes the paused track.")
    async def resume(self, ctx):
        player = ctx.guild.voice_client
        if not player or not player.paused:
            return await ctx.send(embed=self.create_embed("❌ Error", "The music is not paused.", discord.Color.red()))
            
        await player.pause(False)
        await ctx.send(embed=self.create_embed("▶️ Resumed", "The music has been resumed."))

    @commands.command(name="shuffle", help="Shuffles the queue.")
    async def shuffle(self, ctx):
        player = ctx.guild.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(embed=self.create_embed("❌ Error", "The queue is empty.", discord.Color.red()))
            
        player.queue.shuffle()
        await ctx.send(embed=self.create_embed("🔀 Shuffled", "The queue has been shuffled successfully!"))

    @commands.command(name="loop", help="Toggles the loop mode (off -> track -> queue).")
    async def loop(self, ctx):
        player = ctx.guild.voice_client
        if not player:
            return await ctx.send(embed=self.create_embed("❌ Error", "I am not connected to a voice channel.", discord.Color.red()))
            
        if player.queue.mode == wavelink.QueueMode.normal:
            player.queue.mode = wavelink.QueueMode.loop
            mode_text = "Track Loop 🔂"
        elif player.queue.mode == wavelink.QueueMode.loop:
            player.queue.mode = wavelink.QueueMode.loop_all
            mode_text = "Queue Loop 🔁"
        else:
            player.queue.mode = wavelink.QueueMode.normal
            mode_text = "Loop Disabled ➡️"
            
        await ctx.send(embed=self.create_embed("🔄 Loop Mode Changed", f"Loop mode is now: **{mode_text}**"))

    @commands.command(name="clear", help="Clears the current queue.")
    async def clear(self, ctx):
        player = ctx.guild.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(embed=self.create_embed("❌ Error", "The queue is already empty.", discord.Color.red()))
            
        player.queue.clear()
        await ctx.send(embed=self.create_embed("🗑️ Queue Cleared", "All upcoming tracks have been removed."))

    @commands.command(name="remove", help="Removes a track from the queue by position or name.", aliases=['rm'])
    async def remove(self, ctx, *, query: str):
        player = ctx.guild.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(embed=self.create_embed("❌ Error", "The queue is empty.", discord.Color.red()))
            
        if query.isdigit():
            index = int(query)
            if index < 1 or index > len(player.queue):
                return await ctx.send(embed=self.create_embed("❌ Error", f"Please provide a valid track number between 1 and {len(player.queue)}.", discord.Color.red()))
            removed_track = player.queue[index - 1]
            player.queue.delete(index - 1)
            await ctx.send(embed=self.create_embed("🗑️ Track Removed", f"Removed **{removed_track.title}** from the queue."))
        else:
            query_lower = query.lower()
            for i, track in enumerate(player.queue):
                if query_lower in track.title.lower():
                    removed_track = track
                    player.queue.delete(i)
                    return await ctx.send(embed=self.create_embed("🗑️ Track Removed", f"Removed **{removed_track.title}** from the queue."))
            
            await ctx.send(embed=self.create_embed("❌ Error", f"Could not find any song matching **'{query}'** in the queue.", discord.Color.red()))

    @commands.command(name="seek", help="Seeks to a specific position in the track (in seconds).")
    async def seek(self, ctx, seconds: int):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        position = seconds * 1000
        if position > player.current.length:
            return await ctx.send(embed=self.create_embed("❌ Error", "Seek position exceeds track length.", discord.Color.red()))
            
        await player.seek(position)
        await ctx.send(embed=self.create_embed("⏩ Seeked", f"Jumped to **{seconds}** seconds."))

    @commands.command(name="replay", help="Replays the current track from the beginning.")
    async def replay(self, ctx):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        await player.seek(0)
        await ctx.send(embed=self.create_embed("🔄 Replaying", "Restarted the current track."))

    @commands.command(name="forward", help="Skips forward by a certain amount of seconds.", aliases=['fwd'])
    async def forward(self, ctx, seconds: int = 10):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        new_pos = player.position + (seconds * 1000)
        if new_pos > player.current.length:
            new_pos = player.current.length - 1000 # almost end
            
        await player.seek(new_pos)
        await ctx.send(embed=self.create_embed("⏩ Forward", f"Skipped forward by **{seconds}** seconds."))

    @commands.command(name="rewind", help="Rewinds backward by a certain amount of seconds.", aliases=['rwd'])
    async def rewind(self, ctx, seconds: int = 10):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        new_pos = player.position - (seconds * 1000)
        if new_pos < 0:
            new_pos = 0
            
        await player.seek(new_pos)
        await ctx.send(embed=self.create_embed("⏪ Rewind", f"Rewound backwards by **{seconds}** seconds."))

    @commands.command(name="stop", help="Stops playing and clears the queue.")
    async def stop(self, ctx):
        player = ctx.guild.voice_client
        if not player:
            return await ctx.send(embed=self.create_embed("❌ Error", "I am not connected to a voice channel.", discord.Color.red()))
            
        # Mark as an intentional leave so 24/7 mode doesn't auto-rejoin immediately
        self.intentional_leaves.add(ctx.guild.id)
        player.queue.clear()
        await player.disconnect()
        await ctx.send(embed=self.create_embed("🛑 Stopped", "Stopped the music and left the channel.", discord.Color.red()))

    @commands.command(name="queue", help="Shows the current music queue.", aliases=['q'])
    async def queue(self, ctx):
        player = ctx.guild.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(embed=self.create_embed("📋 Queue", "The queue is currently empty."))
            
        queue_list = list(player.queue)
        
        # 10 tracks per page
        chunks = [queue_list[i:i + 10] for i in range(0, len(queue_list), 10)]
        embeds = []
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(title=f"📋 Music Queue (Page {i+1}/{len(chunks)})", color=discord.Color.blue())
            description = ""
            
            if i == 0 and player.current:
                description += f"**🎵 Currently Playing:**\n[{player.current.title}]({player.current.uri})\n\n**⏭️ Upcoming Tracks:**\n"
                
            for j, track in enumerate(chunk):
                description += f"**{(i*10)+j+1}.** [{track.title}]({track.uri})\n"
            embed.description = description
            
            # Keep the footer for convenience on all pages
            if player.current:
                embed.set_footer(text=f"Currently Playing: {player.current.title}")
            embeds.append(embed)
            
        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
        else:
            view = QueuePaginationView(embeds)
            await ctx.send(embed=embeds[0], view=view)

    @commands.command(name="skipto", help="Skips to a specific track number or song name in the queue.")
    async def skipto(self, ctx, *, query: str):
        player = ctx.guild.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(embed=self.create_embed("❌ Error", "The queue is empty.", discord.Color.red()))
            
        index = -1
        
        # Check if the query is a number
        if query.isdigit():
            idx = int(query)
            if 1 <= idx <= len(player.queue):
                index = idx
        else:
            # Search by name (case-insensitive)
            query_lower = query.lower()
            for i, track in enumerate(player.queue, 1):
                if query_lower in track.title.lower():
                    index = i
                    break
                    
        if index == -1:
            return await ctx.send(embed=self.create_embed("❌ Error", f"Could not find a track matching `{query}` in the queue.", discord.Color.red()))
            
        # Get the track name for the success message
        target_track = player.queue[index - 1]
            
        for _ in range(index - 1):
            player.queue.get()
            
        await player.skip(force=True)
        await ctx.send(embed=self.create_embed("⏭️ Skipped To", f"Skipped directly to **{target_track.title}** (Track #{index}).", discord.Color.green()))

    @commands.command(name="volume", help="Changes the player volume (1-100).", aliases=['vol'])
    async def volume(self, ctx, vol: int):
        player = ctx.guild.voice_client
        if not player:
            return await ctx.send(embed=self.create_embed("❌ Error", "I am not connected to a voice channel.", discord.Color.red()))
            
        if vol < 0 or vol > 100:
            return await ctx.send(embed=self.create_embed("❌ Error", "Please provide a volume between 0 and 100.", discord.Color.red()))
            
        await player.set_volume(vol)
        await ctx.send(embed=self.create_embed("🔊 Volume Changed", f"Volume set to **{vol}%**", discord.Color.green()))

    @commands.command(name="lyrics", help="Gets the lyrics for the currently playing song.")
    async def lyrics(self, ctx):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
        
        track = player.current
        title = track.title
        author = track.author or ""
        
        # Use lrclib.net to get the lyrics.
        query = urllib.parse.quote(f"{title} {author}".strip())
        url = f"https://lrclib.net/api/search?q={query}"
        
        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers={"User-Agent": "DiscordBot/1.0"}) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            lyrics = None
                            for track_data in data:
                                if track_data.get("plainLyrics"):
                                    lyrics = track_data["plainLyrics"]
                                    break
                            
                            if lyrics:
                                # Discord embeds have a 4096 character limit for descriptions.
                                chunks = [lyrics[i:i+4000] for i in range(0, len(lyrics), 4000)]
                                for i, chunk in enumerate(chunks):
                                    embed = discord.Embed(title=f"📜 Lyrics for {title}" if i == 0 else f"📜 Lyrics for {title} (Cont.)", description=chunk, color=discord.Color.blurple())
                                    await ctx.send(embed=embed)
                            else:
                                await ctx.send(embed=self.create_embed("❌ Error", "Could not find lyrics for this song.", discord.Color.red()))
                        else:
                            await ctx.send(embed=self.create_embed("❌ Error", "Failed to fetch lyrics from the API.", discord.Color.red()))
            except Exception as e:
                print(f"Error fetching lyrics: {e}")
                await ctx.send(embed=self.create_embed("❌ Error", "An error occurred while fetching the lyrics.", discord.Color.red()))

    @commands.group(name="playlist", invoke_without_command=True)
    async def playlist(self, ctx):
        await ctx.send(embed=self.create_embed("📚 Playlist Commands", "Use `f#playlist save <name>`, `f#playlist play <name>`, or `f#playlist list`.", discord.Color.gold()))

    @playlist.command(name="save", help="Saves the current queue as a personal playlist.")
    async def playlist_save(self, ctx, *, name: str):
        player = ctx.guild.voice_client
        if not player or (not player.playing and player.queue.is_empty):
            return await ctx.send(embed=self.create_embed("❌ Error", "The queue is empty! Play some songs first before saving.", discord.Color.red()))
            
        tracks = []
        if player.current:
            tracks.append(player.current.uri)
        for t in player.queue:
            tracks.append(t.uri)
            
        await self.db.update_one(
            {"user_id": ctx.author.id, "name": name},
            {"$set": {"tracks": tracks}},
            upsert=True
        )
        await ctx.send(embed=self.create_embed("✅ Saved", f"Saved {len(tracks)} tracks to your playlist **{name}**!", discord.Color.green()))

    @playlist.command(name="play", help="Loads and plays a saved personal playlist.")
    async def playlist_play(self, ctx, *, name: str):
        if not ctx.author.voice:
            return await ctx.send(embed=self.create_embed("❌ Error", "You must be in a voice channel to play music.", discord.Color.red()))
            
        doc = await self.db.find_one({"user_id": ctx.author.id, "name": name})
        if not doc:
            return await ctx.send(embed=self.create_embed("❌ Error", f"You don't have a playlist named **{name}**.", discord.Color.red()))
            
        tracks = doc.get("tracks", [])
        if not tracks:
            return await ctx.send(embed=self.create_embed("❌ Error", "Playlist is empty.", discord.Color.red()))
            
        vc = ctx.author.voice.channel
        player = ctx.guild.voice_client
        
        async with ctx.typing():
            if not player:
                player = await vc.connect(cls=wavelink.Player)
                player.autoplay = wavelink.AutoPlayMode.enabled
                player.inactive_timeout = 0
                player.inactive_channel_tokens = 0
                await self.setup_sponsorblock(player)
                player.text_channel = ctx.channel
            elif player.channel.id != vc.id:
                await player.move_to(vc)
                
            added = 0
            for uri in tracks:
                results = await wavelink.Playable.search(uri)
                if results:
                    if isinstance(results, wavelink.Playlist):
                        player.queue.put(results[0])
                    else:
                        player.queue.put(results[0])
                    added += 1
                    
            if not player.playing and not player.queue.is_empty:
                await player.set_volume(30)
                await player.play(player.queue.get())
                
        await ctx.send(embed=self.create_embed("✅ Loaded", f"Loaded {added} tracks from **{name}** into the queue!", discord.Color.green()))

    @playlist.command(name="list", help="Lists all your saved personal playlists.")
    async def playlist_list(self, ctx):
        cursor = self.db.find({"user_id": ctx.author.id})
        docs = await cursor.to_list(length=None)
            
        if not docs:
            return await ctx.send(embed=self.create_embed("❌ Error", "You don't have any saved playlists yet.", discord.Color.red()))
            
        embed = self.create_embed("📚 Your Playlists")
        for doc in docs:
            pname = doc.get("name", "Unknown")
            tracks_list = doc.get("tracks", [])
            embed.add_field(name=f"🎵 {pname}", value=f"{len(tracks_list)} tracks", inline=False)
            
        await ctx.send(embed=embed)

    @commands.group(name="filter", invoke_without_command=True)
    async def filter(self, ctx):
        await ctx.send(embed=self.create_embed("🎛️ Filter Commands", "Use `f#filter bassboost <level>`, `f#filter nightcore`, `f#filter vaporwave`, `f#filter karaoke`, `f#filter 8d`, or `f#filter reset`.", discord.Color.gold()))

    @filter.command(name="8d", help="Applies an 8D audio filter.")
    async def filter_8d(self, ctx):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        filters: wavelink.Filters = player.filters
        filters.rotation.set(rotation_hz=0.2)
        await player.set_filters(filters)
        await ctx.send(embed=self.create_embed("🎛️ 8D Audio", "Applied 8D audio filter! Put on your headphones! 🎧", discord.Color.purple()))

    @filter.command(name="bassboost", help="Applies a bassboost filter (level 0 to 100).")
    async def filter_bassboost(self, ctx, level: int = 50):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        level = max(0, min(100, level))
        gain = level / 100.0 * 1.0 # Max gain of 1.0
        
        filters: wavelink.Filters = player.filters
        filters.equalizer.set(bands=[
            {"band": 0, "gain": gain},
            {"band": 1, "gain": gain * 0.75},
            {"band": 2, "gain": gain * 0.5},
            {"band": 3, "gain": gain * 0.25},
        ])
        await player.set_filters(filters)
        await ctx.send(embed=self.create_embed("🎛️ Bassboost", f"Bassboost set to {level}%", discord.Color.green()))

    @filter.command(name="nightcore", help="Applies a nightcore filter (pitch and speed up).")
    async def filter_nightcore(self, ctx):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.1, rate=1.0)
        await player.set_filters(filters)
        await ctx.send(embed=self.create_embed("🎛️ Nightcore", "Applied Nightcore filter!", discord.Color.purple()))

    @filter.command(name="vaporwave", help="Applies a vaporwave filter (slowed and reverb).")
    async def filter_vaporwave(self, ctx):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=0.8, speed=0.8, rate=1.0)
        await player.set_filters(filters)
        await ctx.send(embed=self.create_embed("🎛️ Vaporwave", "Applied Vaporwave filter! Ａｅｓｔｈｅｔｉｃ", discord.Color.teal()))

    @filter.command(name="karaoke", help="Applies a karaoke filter and retrieves lyrics.")
    async def filter_karaoke(self, ctx):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        filters: wavelink.Filters = player.filters
        filters.karaoke.set(level=1.0, mono_level=1.0, filter_band=220.0, filter_width=100.0)
        await player.set_filters(filters)
        
        track = player.current
        title = track.title if track else ""
        artist = track.author if track else ""
        
        headers = {"User-Agent": "FemboysBot/1.0 (Discord Music Bot)"}
        params = {"track_name": title, "artist_name": artist}
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://lrclib.net/api/get", params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    lyrics = data.get("plainLyrics")
                    if lyrics:
                        if len(lyrics) > 4096:
                            lyrics = lyrics[:4093] + "..."
                        embed = discord.Embed(title=f"🎤 Karaoke: {title}", description=lyrics, color=discord.Color.blue())
                        if artist:
                            embed.set_author(name=artist)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(embed=self.create_embed("🎤 Karaoke", "Karaoke mode activated, but no lyrics were found.", discord.Color.blue()))
                else:
                    await ctx.send(embed=self.create_embed("🎤 Karaoke", "Karaoke mode activated, but no lyrics were found.", discord.Color.blue()))

    @filter.command(name="reset", help="Resets all audio filters.")
    async def filter_reset(self, ctx):
        player = ctx.guild.voice_client
        if not player:
            return await ctx.send(embed=self.create_embed("❌ Error", "The bot is not in a voice channel.", discord.Color.red()))
            
        filters: wavelink.Filters = player.filters
        filters.reset()
        await player.set_filters(filters)
        await ctx.send(embed=self.create_embed("🎛️ Reset", "All filters have been reset to normal.", discord.Color.green()))

    @commands.command(name="history", help="Shows the last 10 tracks played in this server.")
    async def history(self, ctx):
        cursor = self.history_col.find({"guild_id": ctx.guild.id}).sort("played_at", -1).limit(10)
        tracks = await cursor.to_list(length=10)
        
        if not tracks:
            return await ctx.send(embed=self.create_embed("📊 Play History", "No tracks have been played yet!", discord.Color.blue()))
            
        embed = discord.Embed(title="📊 Last 10 Tracks Played", color=discord.Color.blue())
        for i, track in enumerate(tracks, 1):
            played_at = track.get("played_at")
            timestamp = f"<t:{int(played_at.timestamp())}:R>" if played_at else "Unknown time"
            
            track_title = track.get('track_title', 'Unknown')
            artist = track.get('artist', 'Unknown')
            embed.add_field(name=f"{i}. {track_title} by {artist}", value=f"Played {timestamp}", inline=False)
            
        await ctx.send(embed=embed)

    @commands.command(name="top", help="Shows the top 10 most played tracks in this server.")
    async def top(self, ctx):
        pipeline = [
            {"$match": {"guild_id": ctx.guild.id}},
            {"$group": {
                "_id": {"title": "$track_title", "artist": "$artist"},
                "plays": {"$sum": 1}
            }},
            {"$sort": {"plays": -1}},
            {"$limit": 10}
        ]
        
        cursor = self.history_col.aggregate(pipeline)
        top_tracks = await cursor.to_list(length=10)
        
        if not top_tracks:
            return await ctx.send(embed=self.create_embed("🏆 Top Tracks", "No tracks have been played yet!", discord.Color.gold()))
            
        embed = discord.Embed(title="🏆 Top 10 Most Played Tracks", color=discord.Color.gold())
        for i, track in enumerate(top_tracks, 1):
            title = track["_id"].get("title", "Unknown")
            artist = track["_id"].get("artist", "Unknown")
            plays = track["plays"]
            embed.add_field(name=f"{i}. {title} by {artist}", value=f"Plays: {plays}", inline=False)
            
        await ctx.send(embed=embed)

    @commands.command(name="playlyrics", help="Search for a song by its lyrics and play it.")
    async def playlyrics(self, ctx, *, query: str):
        player = ctx.guild.voice_client
        if not player:
            if not ctx.author.voice:
                return await ctx.send(embed=self.create_embed("❌ Error", "You are not connected to a voice channel.", discord.Color.red()))
            player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        
        headers = {"User-Agent": "FemboysBot/1.0 (Discord Music Bot)"}
        params = {"q": query}
        async with aiohttp.ClientSession() as session:
            async with session.get("https://lrclib.net/api/search", params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data:
                        return await ctx.send(embed=self.create_embed("❌ Error", "No songs matched those lyrics.", discord.Color.red()))
                    
                    track_name = data[0].get("trackName", "")
                    artist_name = data[0].get("artistName", "")
                    search_query = f"{track_name} {artist_name}".strip()
                    
                    tracks = await wavelink.Playable.search(search_query)
                    if not tracks:
                        return await ctx.send(embed=self.create_embed("❌ Error", f"Found lyrics for **{search_query}** but couldn't find the audio track.", discord.Color.red()))
                        
                    track = tracks[0]
                    track.extras = {"requester_id": ctx.author.id}
                    await player.queue.put_wait(track)
                    
                    await ctx.send(embed=self.create_embed("🎶 Lyrics Match", f"Found lyrics for **{search_query}**!\nAdded [{track.title}]({track.uri}) to the queue.", discord.Color.green()))
                    
                    if not player.playing:
                        await player.play(player.queue.get())
                else:
                    return await ctx.send(embed=self.create_embed("❌ Error", "Lyrics API is currently unavailable.", discord.Color.red()))

    @commands.command(name="seek", help="Seek to a specific time in the song (e.g. 1m30s, 90, 1:30)")
    async def seek(self, ctx, time_str: str):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        total_seconds = 0
        import re
        if ":" in time_str:
            parts = time_str.split(":")
            if len(parts) == 2:
                total_seconds = int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                total_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif re.match(r'^(\d+[hms])+$', time_str):
            hours = re.search(r'(\d+)h', time_str)
            mins = re.search(r'(\d+)m', time_str)
            secs = re.search(r'(\d+)s', time_str)
            if hours: total_seconds += int(hours.group(1)) * 3600
            if mins: total_seconds += int(mins.group(1)) * 60
            if secs: total_seconds += int(secs.group(1))
        elif time_str.isdigit():
            total_seconds = int(time_str)
        else:
            return await ctx.send(embed=self.create_embed("❌ Error", "Invalid time format! Use `1m30s`, `1:30`, or `90`.", discord.Color.red()))
            
        milliseconds = total_seconds * 1000
        await player.seek(milliseconds)
        await ctx.send(embed=self.create_embed("⏩ Seek", f"Jumped to **{datetime.timedelta(seconds=total_seconds)}** in the track.", discord.Color.green()))

    @commands.command(name="speed", help="Change the playback speed (0.5x to 2.0x)")
    async def speed(self, ctx, multiplier: float):
        player = ctx.guild.voice_client
        if not player:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        if multiplier < 0.5 or multiplier > 2.0:
            return await ctx.send(embed=self.create_embed("❌ Error", "Speed multiplier must be between 0.5 and 2.0.", discord.Color.red()))
            
        filters: wavelink.Filters = player.filters
        filters.timescale.set(speed=multiplier, pitch=1.0, rate=1.0)
        await player.set_filters(filters)
        
        await ctx.send(embed=self.create_embed("⏩ Speed", f"Playback speed set to **{multiplier}x**.", discord.Color.green()))

async def setup(bot):
    await bot.add_cog(Music(bot))
