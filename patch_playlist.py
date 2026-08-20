import json

with open("cogs/music.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """            player.text_channel = ctx.channel
            self.text_channels[ctx.guild.id] = ctx.channel

            max_attempts = 3"""

replacement = """            player.text_channel = ctx.channel
            self.text_channels[ctx.guild.id] = ctx.channel

            is_yt_playlist = "youtube.com/playlist?list=" in search or ("youtu.be/" in search and "list=" in search)

            if is_yt_playlist:
                tmp_msg = await ctx.send(embed=self.create_embed("? Fetching Playlist...", "Downloading playlist metadata locally. This might take a second...", discord.Color.gold()))
                
                def extract_flat():
                    ydl_opts = {'extract_flat': True, 'quiet': True}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        return ydl.extract_info(search, download=False)
                        
                try:
                    info = await asyncio.to_thread(extract_flat)
                    entries = info.get('entries', [])
                    if not entries:
                        raise ValueError("No entries found in playlist.")
                        
                    urls = [entry['url'] for entry in entries if 'url' in entry]
                    playlist_name = info.get('title', 'Unknown Playlist')
                except Exception as e:
                    await tmp_msg.delete()
                    await ctx.send(embed=self.create_embed("? Extraction Failed", f"Failed to extract playlist: {e}", discord.Color.red()))
                    return
                
                await tmp_msg.delete()
                
                initial_chunk = urls[:50]
                remaining_urls = urls[50:]
                
                added_count = 0
                for url in initial_chunk:
                    try:
                        tracks = await wavelink.Playable.search(url)
                        if tracks:
                            track = tracks[0] if not isinstance(tracks, wavelink.Playlist) else list(tracks)[0]
                            if not player.playing:
                                await player.set_volume(30)
                                await player.play(track)
                            else:
                                player.queue.put(track)
                            added_count += 1
                    except Exception:
                        pass
                
                if remaining_urls:
                    await ctx.send(embed=self.create_embed("? Partial Playlist Loaded", f"Added the first {added_count} tracks from **{playlist_name}**.\\nLoading the remaining {len(remaining_urls)} tracks in the background...", discord.Color.green()))
                    
                    async def background_loader():
                        chunks = [remaining_urls[i:i + 50] for i in range(0, len(remaining_urls), 50)]
                        for chunk in chunks:
                            await asyncio.sleep(5)
                            for url in chunk:
                                try:
                                    tracks = await wavelink.Playable.search(url)
                                    if tracks:
                                        track = tracks[0] if not isinstance(tracks, wavelink.Playlist) else list(tracks)[0]
                                        player.queue.put(track)
                                except Exception:
                                    pass
                                    
                    asyncio.create_task(background_loader())
                else:
                    await ctx.send(embed=self.create_embed("? Playlist Loaded", f"Added {added_count} tracks from **{playlist_name}**.", discord.Color.green()))
                    
                return

            max_attempts = 3"""

new_content = content.replace(target, replacement)

if new_content == content:
    print("Replace failed!")
else:
    with open("cogs/music.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Replace successful!")
