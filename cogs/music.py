import os
# pyrefly: ignore [missing-import]
import discord
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

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stay_connected = {} # guild_id -> bool
        self.intentional_leaves = set() # guild_ids that were explicitly told to leave
        self.skip_votes = {} # guild_id -> set(user_ids)
        self.last_skip = {} # guild_id -> timestamp
        self.rejoin_attempts = {} # guild_id -> list of timestamps

    async def cog_load(self):
        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        # Primary Node
        node_uri = os.getenv("LAVALINK_URI", "https://lavalinkv4.serenetia.com:443")
        node_password = os.getenv("LAVALINK_PASSWORD", "youshallnotpass")
        node1 = wavelink.Node(uri=node_uri, password=node_password)

        # Fallback Node 1 (Public)
        node2 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_2", "https://lavalink.oops.wtf:443"), 
            password=os.getenv("LAVALINK_PASSWORD_2", "www.freelavalink.ga")
        )

        # Fallback Node 2 (Public)
        node3 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_3", "http://lava.link:80"), 
            password=os.getenv("LAVALINK_PASSWORD_3", "Corite")
        )

        # Fallback Node 3 (Public - highly available)
        node4 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_4", "https://lavalink.jirayu.net:1337"), 
            password=os.getenv("LAVALINK_PASSWORD_4", "youshallnotpass")
        )

        # Fallback Node 4 (Public - highly available)
        node5 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_5", "https://lavalink.ahri.dev:443"), 
            password=os.getenv("LAVALINK_PASSWORD_5", "ahridev")
        )

        # Fallback Node 5
        node6 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_6", "https://v4.lavalink.info:443"), 
            password=os.getenv("LAVALINK_PASSWORD_6", "youshallnotpass")
        )

        # Fallback Node 6
        node7 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_7", "https://lavalink.lexnet.cc:443"), 
            password=os.getenv("LAVALINK_PASSWORD_7", "youshallnotpass")
        )

        # Fallback Node 7
        node8 = wavelink.Node(
            uri=os.getenv("LAVALINK_URI_8", "https://lava.freelavalink.gq:443"), 
            password=os.getenv("LAVALINK_PASSWORD_8", "freelavalink.gq")
        )

        # Fallback Nodes 8 to 19 (Placeholders - Replace with real servers or your own nodes)
        node9 = wavelink.Node(uri=os.getenv("LAVALINK_URI_9", "https://node9.example.com"), password=os.getenv("LAVALINK_PASSWORD_9", "youshallnotpass"))
        node10 = wavelink.Node(uri=os.getenv("LAVALINK_URI_10", "https://node10.example.com"), password=os.getenv("LAVALINK_PASSWORD_10", "youshallnotpass"))
        node11 = wavelink.Node(uri=os.getenv("LAVALINK_URI_11", "https://node11.example.com"), password=os.getenv("LAVALINK_PASSWORD_11", "youshallnotpass"))
        node12 = wavelink.Node(uri=os.getenv("LAVALINK_URI_12", "https://node12.example.com"), password=os.getenv("LAVALINK_PASSWORD_12", "youshallnotpass"))
        node13 = wavelink.Node(uri=os.getenv("LAVALINK_URI_13", "https://node13.example.com"), password=os.getenv("LAVALINK_PASSWORD_13", "youshallnotpass"))
        node14 = wavelink.Node(uri=os.getenv("LAVALINK_URI_14", "https://node14.example.com"), password=os.getenv("LAVALINK_PASSWORD_14", "youshallnotpass"))
        node15 = wavelink.Node(uri=os.getenv("LAVALINK_URI_15", "https://node15.example.com"), password=os.getenv("LAVALINK_PASSWORD_15", "youshallnotpass"))
        node16 = wavelink.Node(uri=os.getenv("LAVALINK_URI_16", "https://node16.example.com"), password=os.getenv("LAVALINK_PASSWORD_16", "youshallnotpass"))
        node17 = wavelink.Node(uri=os.getenv("LAVALINK_URI_17", "https://node17.example.com"), password=os.getenv("LAVALINK_PASSWORD_17", "youshallnotpass"))
        node18 = wavelink.Node(uri=os.getenv("LAVALINK_URI_18", "https://node18.example.com"), password=os.getenv("LAVALINK_PASSWORD_18", "youshallnotpass"))
        node19 = wavelink.Node(uri=os.getenv("LAVALINK_URI_19", "https://node19.example.com"), password=os.getenv("LAVALINK_PASSWORD_19", "youshallnotpass"))
        node20 = wavelink.Node(uri=os.getenv("LAVALINK_URI_20", "https://node20.example.com"), password=os.getenv("LAVALINK_PASSWORD_20", "youshallnotpass"))
        
        # Wavelink will automatically switch to the next available node if one fails/crashes!
        try:
            nodes_list = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node15, node16, node17, node18, node19, node20]
            await wavelink.Pool.connect(nodes=nodes_list, client=self.bot, cache_capacity=100)
        except Exception as e:
            print(f"Failed to connect to one or more nodes: {e}")

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
                    player.autoplay = wavelink.AutoPlayMode.partial
                    player.inactive_timeout = 0
                    player.inactive_channel_tokens = 0
                    print(f"Auto-rejoined {before.channel.name} due to 24/7 mode.")
                except Exception as e:
                    print(f"Failed to auto-rejoin: {e}")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        print(f"Wavelink Node connected: {payload.node!r} | Resumed: {payload.resumed}")

    @commands.Cog.listener()
    async def on_wavelink_node_disconnected(self, payload: wavelink.NodeDisconnectedEventPayload):
        print(f"Wavelink Node disconnected: {payload.node.identifier}")
        # Notify active voice clients that a node died and we are failing over
        for vc in self.bot.voice_clients:
            if isinstance(vc, wavelink.Player) and hasattr(vc, "text_channel"):
                try:
                    await vc.text_channel.send(embed=self.create_embed(
                        "⚠️ Server Connection Lost",
                        f"The music server we were connected to just crashed! Wavelink is automatically switching to a backup server. Your music should resume shortly.",
                        discord.Color.orange()
                    ))
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        player = payload.player
        if not player or not hasattr(player, "text_channel"):
            return
            
        # Reset skip votes for the new track
        if player.guild.id in self.skip_votes:
            self.skip_votes[player.guild.id].clear()
            
        track = payload.track
        embed = discord.Embed(title="🎶 Now Playing", description=f"**[{track.title}]({track.uri})**", color=discord.Color.green())
        if track.author:
            embed.add_field(name="Author", value=track.author, inline=True)
        if track.length:
            minutes, seconds = divmod(track.length // 1000, 60)
            embed.add_field(name="Duration", value=f"{minutes}:{seconds:02d}", inline=True)
            
        await player.text_channel.send(embed=embed)

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
    async def on_wavelink_node_disconnected(self, payload: wavelink.NodeDisconnectedEventPayload):
        print(f"Node {payload.node.identifier} disconnected. Attempting Failover Memory restoration...")
        
        for vc in self.bot.voice_clients:
            if isinstance(vc, wavelink.Player):
                # If the player was interrupted and stopped playing, but still has a current track
                if vc.current and not vc.playing:
                    try:
                        print(f"Restoring {vc.current.title} at {vc.position}ms for guild {vc.guild.id}")
                        await asyncio.sleep(3) # Give wavelink a moment to move to the fallback node
                        
                        # Resume exactly where it left off!
                        await vc.play(vc.current, start=vc.position)
                        
                        if hasattr(vc, "text_channel") and vc.text_channel:
                            await vc.text_channel.send(embed=self.create_embed("🔄 Node Failover", f"The music server crashed! Automatically restored playback of **{vc.current.title}**.", discord.Color.gold()))
                    except Exception as e:
                        print(f"Failover restoration failed: {e}")

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
                player.autoplay = wavelink.AutoPlayMode.partial
                player.inactive_timeout = 0
                player.inactive_channel_tokens = 0
                await ctx.send(embed=self.create_embed("✅ Joined Channel", f"Successfully joined {vc.mention}"))
            elif player.channel.id != vc.id:
                await player.move_to(vc)
                await ctx.send(embed=self.create_embed("✅ Moved Channel", f"Moved to {vc.mention}"))
            else:
                await ctx.send(embed=self.create_embed("ℹ️ Info", "I am already in your voice channel.", discord.Color.gold()))
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
            elif player.channel.id != vc.id:
                await player.move_to(vc)

            player.text_channel = ctx.channel

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
                else:
                    player.queue.put(track)
                    embed = discord.Embed(title="✅ Added to Queue", description=f"**[{track.title}]({track.uri})**", color=discord.Color.green())
                    await ctx.send(embed=embed)
                
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

    @commands.command(name="nowplaying", help="Shows the currently playing track.", aliases=['np'])
    async def nowplaying(self, ctx):
        player = ctx.guild.voice_client
        if not player or not player.playing:
            return await ctx.send(embed=self.create_embed("❌ Error", "Nothing is playing right now.", discord.Color.red()))
            
        track = player.current
        embed = discord.Embed(title="🎶 Now Playing", description=f"**[{track.title}]({track.uri})**", color=discord.Color.green())
        if track.author:
            embed.add_field(name="Author", value=track.author, inline=True)
        if track.length:
            minutes, seconds = divmod(track.length // 1000, 60)
            embed.add_field(name="Duration", value=f"{minutes}:{seconds:02d}", inline=True)
            
        await ctx.send(embed=embed)

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
            return await ctx.send(embed=self.create_embed("⏭️ Skipped", "Skipped the current track."))

        # Initialize vote set for the guild if not exists
        if ctx.guild.id not in self.skip_votes:
            self.skip_votes[ctx.guild.id] = set()

        if ctx.author.id in self.skip_votes[ctx.guild.id]:
            return await ctx.send(embed=self.create_embed("ℹ️ Vote Recorded", f"You have already voted to skip! ({len(self.skip_votes[ctx.guild.id])}/{required_votes} votes needed)", discord.Color.gold()))

        self.skip_votes[ctx.guild.id].add(ctx.author.id)
        current_votes = len(self.skip_votes[ctx.guild.id])

        if current_votes >= required_votes:
            self.skip_votes[ctx.guild.id].clear()
            self.last_skip[ctx.guild.id] = time.time()
            await player.skip(force=True)
            await ctx.send(embed=self.create_embed("⏭️ Skipped", f"Vote passed ({current_votes}/{required_votes}). Skipped the current track!", discord.Color.green()))
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

    @commands.command(name="remove", help="Removes a track from the queue at the given position.", aliases=['rm'])
    async def remove(self, ctx, index: int):
        player = ctx.guild.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(embed=self.create_embed("❌ Error", "The queue is empty.", discord.Color.red()))
            
        if index < 1 or index > len(player.queue):
            return await ctx.send(embed=self.create_embed("❌ Error", f"Please provide a valid track number between 1 and {len(player.queue)}.", discord.Color.red()))
            
        # Wavelink queue is zero-indexed, but users type 1-indexed
        removed_track = player.queue[index - 1]
        player.queue.delete(index - 1)
        await ctx.send(embed=self.create_embed("🗑️ Track Removed", f"Removed **{removed_track.title}** from the queue."))

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

async def setup(bot):
    await bot.add_cog(Music(bot))
