import os
import asyncio
import random
import time
import urllib.parse
from typing import Optional, Dict, List, Set

# pyrefly: ignore [missing-import]
import discord
# pyrefly: ignore [missing-import]
from discord.ext import commands

# All 224 non-lyrical / soothing instrumental tracks from lofi.radio (by Purrple Cat)
LOFI_RADIO_SONGS = [
    "3 A.M. Radio.mp3", "A Place to Hide.mp3", "Adrift.mp3", "Aether.mp3", "After Hours.mp3",
    "All Curled Up.mp3", "Alley Cat.mp3", "Artifact.mp3", "Astral Projection.mp3", "Aurora.mp3",
    "Awakenings.mp3", "Bayou Blues.mp3", "Beautiful Day.mp3", "Bird Bath.mp3", "Birdhouse.mp3",
    "Blood Moon.mp3", "Bloom.mp3", "Breathing Underwater.mp3", "Cable Car.mp3", "Calm Waters.mp3",
    "Can't Sleep.mp3", "Carousel.mp3", "Cave of Solace.mp3", "Celestial Sands.mp3", "Changes.mp3",
    "Chasing Snowflakes.mp3", "Chugging Along.mp3", "Come One, Come All.mp3", "Comfy.mp3",
    "Constellations.mp3", "Contact.mp3", "Convergence.mp3", "Cool Breeze.mp3", "Corner Store.mp3",
    "Cosmic Echoes.mp3", "Cosmic Web.mp3", "Creation.mp3", "Creatures of the Night.mp3",
    "Crescent Moon.mp3", "Crossroads.mp3", "Cruisin'.mp3", "Dance of the Cacti.mp3",
    "Dancing Dandelions.mp3", "Dancing Shadows.mp3", "Dark Corners.mp3", "Dark Forest.mp3",
    "Day's End.mp3", "Defunct.mp3", "Deja Vu.mp3", "Desert Rain.mp3", "Desolate.mp3",
    "Discovery.mp3", "Distant Ships.mp3", "Dont Look Back.mp3", "Downpour.mp3", "Downtown.mp3",
    "Dream Machine.mp3", "Dream State.mp3", "Drifting.mp3", "Dune Drifter.mp3", "Ebb and Flow.mp3",
    "Echoes of Yesterday.mp3", "Eerie Glow.mp3", "Egress.mp3", "Elevated.mp3", "Embrace.mp3",
    "Empty Sidewalks.mp3", "End of the Line.mp3", "Epiphany.mp3", "Equinox.mp3", "Ethereal.mp3",
    "Everchanging.mp3", "Exhale.mp3", "Exploration.mp3", "Eye of the Storm.mp3", "Eyes in the Dark.mp3",
    "Fading.mp3", "Fallen.mp3", "Familiar Faces.mp3", "Field Of Fireflies.mp3", "Flourish.mp3",
    "Fog Blanket.mp3", "Forget-Me-Not.mp3", "Fourth Dimension.mp3", "Fragments.mp3", "Frolic.mp3",
    "Frosted Evergreen.mp3", "Frozen Flowers.mp3", "Gentle Breeze.mp3", "Ghost Planet.mp3",
    "Ghost Town.mp3", "Ghosties.mp3", "Gingerbread House.mp3", "Glowing Tides.mp3",
    "Going With The Flow.mp3", "Goosebumps.mp3", "Green Tea.mp3", "Half Awake.mp3", "Happy Trails.mp3",
    "Heart of the Ocean.mp3", "Ice Palace.mp3", "Icicles.mp3", "In Between.mp3", "In the Moment.mp3",
    "In the Past.mp3", "In the Walls.mp3", "Infinite.mp3", "Insomnia.mp3", "Intertwined.mp3",
    "Labyrinth.mp3", "Lazy Afternoon.mp3", "Leviathan.mp3", "Lighthouse.mp3", "Lonely.mp3",
    "Long Day.mp3", "Looking Up.mp3", "Lost Paradise.mp3", "Lost Souls.mp3", "Lost and Found.mp3",
    "Lost at Sea.mp3", "Low Tide.mp3", "Lullaby.mp3", "Luminous.mp3", "Lurking in the Shadows.mp3",
    "Lush.mp3", "Maelstrom.mp3", "Magical Moments.mp3", "Mesa's Edge.mp3", "Message in a Bottle.mp3",
    "Meteorites.mp3", "Mirage.mp3", "Missing Pieces.mp3", "Morning Dew.mp3", "Moving Landscapes.mp3",
    "Mysterious Passenger.mp3", "Nevermore.mp3", "Nexus.mp3", "Night Light.mp3", "Night Owls.mp3",
    "Night Train.mp3", "Nightfall.mp3", "Not Alone.mp3", "Nowhere to Hide.mp3", "Oddity.mp3",
    "On the Brink.mp3", "Once in a Lifetime.mp3", "Otherworldly.mp3", "Out of Place.mp3",
    "Out of the Blue.mp3", "Palm Tree.mp3", "Paradox.mp3", "Passing Time.mp3",
    "Peppermint Mocha.mp3", "Phantom Waltz.mp3", "Pineapple Popsicle.mp3", "Pitter Patter.mp3",
    "Planetary Alignment.mp3", "Rainy Streets.mp3", "Refractions.mp3", "Rewind.mp3",
    "Rift in Time.mp3", "Rocky Shores.mp3", "Rooftop Rendezvous.mp3", "Running Late.mp3",
    "Sandstorm.mp3", "Satellite.mp3", "Sea Foam.mp3", "Sea of Stars.mp3", "Seashells.mp3",
    "Secret Of The Forest.mp3", "Serendipity.mp3", "Serenity Now.mp3", "Shelter.mp3",
    "Signs of Life.mp3", "Silent Wood.mp3", "Siren's Song.mp3", "Skeleton Dance.mp3",
    "Skyscrapers.mp3", "Snow Pillow.mp3", "Soft.mp3", "Solitude.mp3", "Sonder.mp3",
    "Spring Showers.mp3", "Star Bright.mp3", "Starlit Beach.mp3", "Starry Night.mp3",
    "Stars Collide.mp3", "Starseed.mp3", "Stasis.mp3", "Step Right Up.mp3", "Still of the Night.mp3",
    "Stranded.mp3", "Strange Fog.mp3", "Stray.mp3", "Streetlights.mp3", "Strike of Midnight.mp3",
    "Sunken Secrets.mp3", "Supernova.mp3", "Take Me With You.mp3", "The Bells.mp3",
    "The Dungeon.mp3", "The Midnight Diner.mp3", "The Murk.mp3", "The Portal.mp3",
    "The Toymaker.mp3", "Through the Trees.mp3", "Thunderous Waves.mp3", "Time Loop.mp3",
    "Time to Think.mp3", "Timeless.mp3", "Toasty.mp3", "Torn.mp3", "Tracks to Nowhere.mp3",
    "Transformation.mp3", "Tumbleweeds.mp3", "Tunnels.mp3", "Twilight Market.mp3", "UFO.mp3",
    "Under the Canopy.mp3", "Undertow.mp3", "Underwater Cavern.mp3", "Uninvited.mp3",
    "Unreality.mp3", "Upside Down.mp3", "Verdant.mp3", "Visions.mp3", "Waiting for the Sun.mp3",
    "Wanderlust.mp3", "Warm Horizon.mp3", "Weightless.mp3", "Weird Dream.mp3",
    "What Lies Beyond.mp3", "Wild Strawberry.mp3", "Window Seat.mp3", "Wish You Were Here.mp3",
    "Wishes.mp3", "Wishing Well.mp3", "Wonderland.mp3", "Wonderment.mp3", "Zero Gravity.mp3",
    "Zzz....mp3"
]

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class RadioPlayerUI(discord.ui.View):
    def __init__(self, music_cog):
        super().__init__(timeout=None)
        self.music_cog = music_cog

    @discord.ui.button(label="⏯️ Play/Pause", style=discord.ButtonStyle.primary, custom_id="lofi_play_pause", row=0)
    async def play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await interaction.response.send_message("Radio is not playing right now.", ephemeral=True)

        guild_id = interaction.guild.id
        if vc.is_playing():
            vc.pause()
        elif vc.is_paused():
            vc.resume()
        else:
            return await interaction.response.send_message("Radio is currently loading next track.", ephemeral=True)

        current = self.music_cog.current_song.get(guild_id, "Soothing Melody")
        embed = self.music_cog.create_player_embed(guild_id, current)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⏭️ Next Melody", style=discord.ButtonStyle.secondary, custom_id="lofi_skip", row=0)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await interaction.response.send_message("Radio is not playing right now.", ephemeral=True)

        if not interaction.user.voice or interaction.user.voice.channel != vc.channel: # pyrefly: ignore
            return await interaction.response.send_message("You must be in the same voice channel to skip.", ephemeral=True)

        guild_id = interaction.guild.id
        now = time.time()
        last_skip = self.music_cog.last_skip.get(guild_id, 0)
        if now - last_skip < 2.0:
            return await interaction.response.send_message("⏳ Buffering next melody, please wait a moment!", ephemeral=True)

        self.music_cog.last_skip[guild_id] = now
        await interaction.response.send_message("⏭️ Tuned to the next soothing melody.", ephemeral=True)
        vc.stop() # Triggers play_next_song which edits the single session message!

    @discord.ui.button(label="🔀 Shuffle", style=discord.ButtonStyle.secondary, custom_id="lofi_shuffle", row=0)
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await interaction.response.send_message("Radio is not active.", ephemeral=True)

        guild_id = interaction.guild.id
        queue = self.music_cog.queues.get(guild_id, [])
        random.shuffle(queue)
        await interaction.response.send_message(f"🔀 Shuffled {len(queue)} upcoming soothing melodies!", ephemeral=True)
        current = self.music_cog.current_song.get(guild_id, "Soothing Melody")
        embed = self.music_cog.create_player_embed(guild_id, current)
        try:
            if interaction.message:
                await interaction.message.edit(embed=embed, view=self)
        except Exception:
            pass

    @discord.ui.button(label="🔉 Vol -", style=discord.ButtonStyle.secondary, custom_id="lofi_vol_down", row=0)
    async def vol_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        current_vol = self.music_cog.volumes.get(guild_id, 0.35)
        new_vol = max(0.05, round(current_vol - 0.10, 2))
        self.music_cog.volumes[guild_id] = new_vol

        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if vc and vc.source and isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = new_vol

        current = self.music_cog.current_song.get(guild_id, "Soothing Melody")
        embed = self.music_cog.create_player_embed(guild_id, current)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🔊 Vol +", style=discord.ButtonStyle.secondary, custom_id="lofi_vol_up", row=0)
    async def vol_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        current_vol = self.music_cog.volumes.get(guild_id, 0.35)
        new_vol = min(1.0, round(current_vol + 0.10, 2))
        self.music_cog.volumes[guild_id] = new_vol

        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if vc and vc.source and isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = new_vol

        current = self.music_cog.current_song.get(guild_id, "Soothing Melody")
        embed = self.music_cog.create_player_embed(guild_id, current)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⏹️ Stop & Leave", style=discord.ButtonStyle.danger, custom_id="lofi_stop", row=1)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client # pyrefly: ignore
        if not vc:
            return await interaction.response.send_message("Radio is not playing.", ephemeral=True)

        guild_id = interaction.guild.id
        self.music_cog.intentional_leaves.add(guild_id)
        if guild_id:
            self.music_cog.queues[guild_id] = []
        vc.stop()
        await vc.disconnect()

        embed = discord.Embed(
            title="📻 Soothing Lofi Radio • Session Ended",
            description="The radio stream has ended. Thank you for listening!\nUse `f#radio` to start a new soothing session anytime.",
            color=discord.Color.dark_grey()
        )
        embed.set_footer(text="Femboys Bot • 24/7 Lofi Radio", icon_url=self.music_cog.bot.user.display_avatar.url if self.music_cog.bot.user else None)
        await interaction.response.edit_message(embed=embed, view=None)
        self.music_cog.player_messages.pop(guild_id, None)


class QueuePaginationView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], timeout: float = 60.0):
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
    """Direct 24/7 Soothing Melody Radio Cog (Streaming 224+ non-lyrical tracks from lofi.radio)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: Dict[int, List[str]] = {}
        self.history: Dict[int, List[str]] = {}
        self.current_song: Dict[int, str] = {}
        self.volumes: Dict[int, float] = {}
        self.text_channels: Dict[int, discord.abc.Messageable] = {}
        self.player_messages: Dict[int, discord.Message] = {}
        self.last_skip: Dict[int, float] = {}
        self.stay_connected: Dict[int, bool] = {}
        self.intentional_leaves: Set[int] = set()

    def create_embed(self, title: str, description: str = "", color: discord.Color = discord.Color.blurple()) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="Femboys Bot • 24/7 Lofi Radio", icon_url=self.bot.user.display_avatar.url if self.bot.user else None)
        return embed

    def get_song_title(self, filename: str) -> str:
        """Strips the .mp3 extension and cleans the song title."""
        if filename.endswith(".mp3"):
            return filename[:-4]
        return filename

    def get_song_url(self, filename: str) -> str:
        """Returns direct high-speed audio stream URL from lofi.radio."""
        quoted = urllib.parse.quote(filename)
        return f"https://lofi.radio/songs/{quoted}"

    def ensure_queue(self, guild_id: int):
        """Ensures the guild has a randomized upcoming queue."""
        q = self.queues.setdefault(guild_id, [])
        if len(q) < 5:
            fresh_batch = list(LOFI_RADIO_SONGS)
            random.shuffle(fresh_batch)
            q.extend(fresh_batch)

    def create_player_embed(self, guild_id: int, song_filename: str) -> discord.Embed:
        title = self.get_song_title(song_filename)
        song_url = self.get_song_url(song_filename)
        vol_pct = int(self.volumes.get(guild_id, 0.35) * 100)
        remaining = len(self.queues.get(guild_id, []))

        guild = self.bot.get_guild(guild_id)
        vc: Optional[discord.VoiceClient] = guild.voice_client if guild else None # pyrefly: ignore
        is_paused = vc.is_paused() if vc else False
        status_text = "⏸️ Stream Paused" if is_paused else "▶️ Streaming Live (24/7)"

        embed = discord.Embed(
            title="📻 Soothing Lofi Radio • Now Playing",
            description=f"### 🎵 [{title}]({song_url})\n"
                        f"👤 **Artist:** Purrple Cat\n"
                        f"🌐 **Source:** [lofi.radio](https://lofi.radio/)\n"
                        f"✨ **Genre:** 100% Non-Lyrical Chill Beats & Melodies\n\n"
                        f"━🔘━━━━━━━━━━ `{status_text}`",
            color=discord.Color.from_rgb(0, 209, 178) # Lofi teal
        )
        embed.set_thumbnail(url="https://lofi.radio/lofiradio.png")
        embed.add_field(
            name="📊 Radio Status",
            value=f"🔊 **Volume:** {vol_pct}%\n"
                  f"🔀 **Remaining in Queue:** {remaining} tracks\n"
                  f"🕒 **24/7 Mode:** {'Enabled ✅' if self.stay_connected.get(guild_id, True) else 'Disabled ❌'}",
            inline=True
        )
        embed.add_field(
            name="☕ Relax & Focus",
            value="Dreamy chill beats to study, relax, and sleep.\nNo ads, no lyrics, no interruptions.",
            inline=True
        )
        embed.set_footer(
            text="Single Session Stream • Powered directly by lofi.radio",
            icon_url=self.bot.user.display_avatar.url if self.bot.user else None
        )
        return embed

    async def update_player_message(self, guild_id: int, song_filename: str):
        """Updates the persistent single session message for this guild."""
        channel = self.text_channels.get(guild_id)
        if not channel:
            guild = self.bot.get_guild(guild_id)
            if guild:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        self.text_channels[guild_id] = ch
                        break

        if not channel:
            return

        embed = self.create_player_embed(guild_id, song_filename)
        view = RadioPlayerUI(self)

        existing_msg = self.player_messages.get(guild_id)
        if existing_msg:
            try:
                await existing_msg.edit(embed=embed, view=view)
                return
            except discord.NotFound:
                self.player_messages.pop(guild_id, None)
            except discord.HTTPException as e:
                print(f"[RADIO] Failed to edit existing player message: {e}")
                self.player_messages.pop(guild_id, None)

        try:
            msg = await channel.send(embed=embed, view=view)
            self.player_messages[guild_id] = msg
        except Exception as e:
            print(f"[RADIO] Failed to send Player UI: {e}")

    async def cleanup_session(self, guild_id: int):
        """Edits the single session message to ended state when the bot leaves or stops."""
        msg = self.player_messages.pop(guild_id, None)
        if msg:
            try:
                embed = discord.Embed(
                    title="📻 Soothing Lofi Radio • Session Ended",
                    description="The radio stream has ended. Thank you for listening!\nUse `f#radio` to start a new soothing session anytime.",
                    color=discord.Color.dark_grey()
                )
                embed.set_footer(text="Femboys Bot • 24/7 Lofi Radio", icon_url=self.bot.user.display_avatar.url if self.bot.user else None)
                await msg.edit(embed=embed, view=None)
            except Exception:
                pass

    def play_next_song(self, guild_id: int):
        """Plays the next soothing melody from the queue and updates the single session message."""
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return

        vc: Optional[discord.VoiceClient] = guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return

        self.ensure_queue(guild_id)
        next_song = self.queues[guild_id].pop(0)
        self.current_song[guild_id] = next_song

        hist = self.history.setdefault(guild_id, [])
        hist.append(next_song)
        if len(hist) > 30:
            hist.pop(0)

        url = self.get_song_url(next_song)
        vol = self.volumes.get(guild_id, 0.35)

        try:
            audio_source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
            vol_source = discord.PCMVolumeTransformer(audio_source, volume=vol)

            def after_play(error):
                if error:
                    print(f"[RADIO] Playback error for {next_song}: {error}")
                self.bot.loop.call_soon_threadsafe(self.play_next_song, guild_id)

            vc.play(vol_source, after=after_play)
            print(f"\033[32m[RADIO] 🎵 Now Playing:\033[0m {self.get_song_title(next_song)} in {guild.name}")

            # Update the single session message
            self.bot.loop.create_task(self.update_player_message(guild_id, next_song))
        except Exception as e:
            print(f"[RADIO] Failed to play {next_song}: {e}")
            self.bot.loop.call_soon_threadsafe(self.play_next_song, guild_id)

    # ==================== VOICE STATE LISTENER ====================

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id != self.bot.user.id:
            return

        guild_id = member.guild.id

        # If disconnected unexpectedly, auto-rejoin if 24/7 is enabled
        if before.channel is not None and after.channel is None:
            if guild_id in self.intentional_leaves:
                self.intentional_leaves.discard(guild_id)
                await self.cleanup_session(guild_id)
                return

            if self.stay_connected.get(guild_id, True):
                print(f"[RADIO] Disconnected from {before.channel.name}. Auto-rejoining in 2 seconds (24/7 mode)...")
                await asyncio.sleep(2)
                try:
                    vc = await before.channel.connect(timeout=20.0, reconnect=True)
                    self.play_next_song(guild_id)
                except Exception as e:
                    print(f"[RADIO] Auto-rejoin failed: {e}")
                    await self.cleanup_session(guild_id)
            else:
                await self.cleanup_session(guild_id)

    # ==================== BOT COMMANDS ====================

    @commands.command(name="radio", help="Starts the 24/7 soothing lofi radio from lofi.radio.", aliases=["join", "start", "play", "p"])
    async def radio_command(self, ctx):
        """Summons the bot and begins streaming non-stop soothing melodies directly from lofi.radio."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(embed=self.create_embed("❌ Voice Channel Required", "Please join a voice channel first to start the radio!", discord.Color.red()), delete_after=10)

        vc_target = ctx.author.voice.channel
        guild_id = ctx.guild.id
        self.text_channels[guild_id] = ctx.channel
        self.stay_connected[guild_id] = True # Default 24/7

        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore

        if not vc or not vc.is_connected():
            msg = await ctx.send(embed=self.create_embed("📻 Connecting...", f"Connecting to {vc_target.mention} and tuning into **lofi.radio**...", discord.Color.blue()))
            try:
                vc = await vc_target.connect(timeout=20.0, reconnect=True)
                self.player_messages[guild_id] = msg
            except Exception as e:
                return await msg.edit(embed=self.create_embed("❌ Connection Failed", f"Could not connect to {vc_target.mention}: {e}", discord.Color.red()))
        elif vc.channel.id != vc_target.id:
            await vc.move_to(vc_target)

        # If not playing, start radio immediately
        if not vc.is_playing() and not vc.is_paused():
            self.ensure_queue(guild_id)
            self.play_next_song(guild_id)
        else:
            current = self.current_song.get(guild_id, "Soothing Melody")
            await self.update_player_message(guild_id, current)

        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="next", help="Skips to the next soothing melody.", aliases=["skip", "s"])
    async def next_command(self, ctx):
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await ctx.send(embed=self.create_embed("❌ Error", "Radio is not playing.", discord.Color.red()), delete_after=5)

        vc.stop() # Triggers play_next_song which edits the single session message
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="previous", help="Replays the previous melody from history.", aliases=["prev"])
    async def prev_command(self, ctx):
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await ctx.send(embed=self.create_embed("❌ Error", "Radio is not playing.", discord.Color.red()), delete_after=5)

        guild_id = ctx.guild.id
        hist = self.history.get(guild_id, [])
        if len(hist) < 2:
            return await ctx.send(embed=self.create_embed("❌ Error", "No previous melody in history.", discord.Color.red()), delete_after=5)

        # Put current song back to front of queue
        current = self.current_song.get(guild_id)
        if current:
            self.queues.setdefault(guild_id, []).insert(0, current)

        hist.pop()
        prev_song = hist.pop()
        self.queues[guild_id].insert(0, prev_song)
        vc.stop()
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="shuffle", help="Shuffles upcoming soothing melodies.")
    async def shuffle_command(self, ctx):
        guild_id = ctx.guild.id
        self.ensure_queue(guild_id)
        random.shuffle(self.queues[guild_id])
        current = self.current_song.get(guild_id, "Soothing Melody")
        await self.update_player_message(guild_id, current)
        await ctx.send(embed=self.create_embed("🔀 Shuffled", f"Randomized {len(self.queues[guild_id])} upcoming soothing melodies from **lofi.radio**!", discord.Color.green()), delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="pause", help="Pauses the radio stream.")
    async def pause_command(self, ctx):
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await ctx.send(embed=self.create_embed("❌ Error", "Radio is not active.", discord.Color.red()), delete_after=5)

        if vc.is_playing():
            vc.pause()
            current = self.current_song.get(ctx.guild.id, "Soothing Melody")
            await self.update_player_message(ctx.guild.id, current)
            await ctx.send(embed=self.create_embed("⏸️ Paused", "Paused the soothing radio stream.", discord.Color.gold()), delete_after=5)
        else:
            await ctx.send(embed=self.create_embed("ℹ️ Already Paused", "Radio is already paused.", discord.Color.gold()), delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="resume", help="Resumes the paused radio stream.")
    async def resume_command(self, ctx):
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected():
            return await ctx.send(embed=self.create_embed("❌ Error", "Radio is not active.", discord.Color.red()), delete_after=5)

        if vc.is_paused():
            vc.resume()
            current = self.current_song.get(ctx.guild.id, "Soothing Melody")
            await self.update_player_message(ctx.guild.id, current)
            await ctx.send(embed=self.create_embed("▶️ Resumed", "Resumed the soothing radio stream.", discord.Color.green()), delete_after=5)
        else:
            await ctx.send(embed=self.create_embed("ℹ️ Already Playing", "Radio is already playing.", discord.Color.green()), delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="volume", help="Adjusts radio volume (1-100%).", aliases=["vol", "v"])
    async def volume_command(self, ctx, volume: int):
        volume = max(1, min(100, volume))
        guild_id = ctx.guild.id
        vol_float = volume / 100.0
        self.volumes[guild_id] = vol_float

        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if vc and vc.source and isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = vol_float

        current = self.current_song.get(guild_id, "Soothing Melody")
        await self.update_player_message(guild_id, current)
        await ctx.send(embed=self.create_embed("🔊 Volume", f"Radio volume set to **{volume}%**.", discord.Color.blue()), delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="nowplaying", help="Focuses or refreshes the single session player message.", aliases=["np"])
    async def nowplaying_command(self, ctx):
        guild_id = ctx.guild.id
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc or not vc.is_connected() or guild_id not in self.current_song:
            return await ctx.send(embed=self.create_embed("ℹ️ Radio Offline", "The radio is not currently playing. Use `f#radio` to tune in!", discord.Color.gold()), delete_after=8)

        self.text_channels[guild_id] = ctx.channel
        await self.update_player_message(guild_id, self.current_song[guild_id])
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="queue", help="Shows upcoming soothing melodies.", aliases=["q"])
    async def queue_command(self, ctx):
        guild_id = ctx.guild.id
        self.ensure_queue(guild_id)
        tracks = self.queues[guild_id]

        per_page = 8
        chunks = [tracks[i:i + per_page] for i in range(0, min(len(tracks), 40), per_page)]

        embeds = []
        for page_idx, chunk in enumerate(chunks):
            lines = [f"**Source:** [lofi.radio](https://lofi.radio/) • **Artist:** Purrple Cat\n"]
            for idx, track in enumerate(chunk):
                item_num = page_idx * per_page + idx + 1
                title = self.get_song_title(track)
                url = self.get_song_url(track)
                lines.append(f"`{item_num}.` **[{title}]({url})**")

            embed = discord.Embed(
                title=f"📻 Upcoming Soothing Melodies (Page {page_idx + 1}/{len(chunks)})",
                description="\n".join(lines),
                color=discord.Color.from_rgb(0, 209, 178)
            )
            embed.set_footer(text=f"Total in rotating playlist: {len(LOFI_RADIO_SONGS)} tracks")
            embeds.append(embed)

        if len(embeds) == 1:
            await ctx.send(embed=embeds[0], delete_after=60)
        else:
            view = QueuePaginationView(embeds)
            await ctx.send(embed=embeds[0], view=view, delete_after=60)

    @commands.command(name="247", help="Toggles 24/7 continuous stream mode.")
    async def toggle_247(self, ctx):
        current = self.stay_connected.get(ctx.guild.id, True)
        self.stay_connected[ctx.guild.id] = not current
        status = "Enabled ✅" if self.stay_connected[ctx.guild.id] else "Disabled ❌"
        current_song = self.current_song.get(ctx.guild.id, "Soothing Melody")
        await self.update_player_message(ctx.guild.id, current_song)
        await ctx.send(embed=self.create_embed("🕒 24/7 Radio Mode", f"24/7 continuous stream is now **{status}**.", discord.Color.gold()), delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.command(name="stop", help="Stops radio and leaves the voice channel.", aliases=["leave", "dc", "disconnect"])
    async def stop_command(self, ctx):
        vc: Optional[discord.VoiceClient] = ctx.guild.voice_client # pyrefly: ignore
        if not vc:
            return await ctx.send(embed=self.create_embed("ℹ️ Not Connected", "The bot is not in a voice channel.", discord.Color.gold()), delete_after=5)

        guild_id = ctx.guild.id
        self.intentional_leaves.add(guild_id)
        if guild_id:
            self.queues[guild_id] = []
        vc.stop()
        await vc.disconnect()
        await self.cleanup_session(guild_id)
        try:
            await ctx.message.delete()
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))

