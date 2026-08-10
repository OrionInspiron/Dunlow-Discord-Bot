# pyrefly: ignore [missing-import]
import discord
# pyrefly: ignore [missing-import]
from discord.ext import commands

class HelpPaginationView(discord.ui.View):
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


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", help="Shows this help message.")
    async def help_command(self, ctx):
        friendly_descriptions = {
            "247": "Keeps the bot in the voice channel 24/7, even when no music is playing.",
            "join": "Summons the bot into your current voice channel.",
            "play": "Plays a song! Just type a song name or paste a link.",
            "nowplaying": "Shows the song that is currently playing.",
            "skip": "Skips the current song and plays the next one.",
            "pause": "Pauses the music.",
            "resume": "Resumes playing the paused music.",
            "shuffle": "Mixes up all the songs in your queue randomly.",
            "loop": "Changes the loop mode (Loop off -> Loop song -> Loop entire queue).",
            "clear": "Removes all songs from the queue.",
            "remove": "Removes a specific song from the queue using its number.",
            "seek": "Jumps to a specific time in the song (e.g., 60 for 1 minute).",
            "replay": "Restarts the current song from the very beginning.",
            "forward": "Jumps forward in the song by the amount of seconds you specify.",
            "rewind": "Jumps backward in the song by the amount of seconds you specify.",
            "stop": "Stops the music entirely and clears everything out.",
            "queue": "Shows you the list of upcoming songs.",
            "skipto": "Skips directly to a specific song number or name in the queue.",
            "volume": "Turns the music volume up or down (1-100).",
            "lyrics": "Searches for the lyrics of the currently playing song.",
            "playlist": "Commands to manage your personal playlists.",
            "save": "Saves everything in the queue to a personal playlist you can play later.",
            "list": "Shows you a list of all the personal playlists you have saved.",
            "filter": "Fun audio effects you can apply to the music.",
            "bassboost": "Turns up the bass! You can set the level from 0 to 100.",
            "nightcore": "Speeds up the song and raises the pitch for a Nightcore vibe.",
            "vaporwave": "Slows down the song and lowers the pitch for a chill Vaporwave aesthetic.",
            "reset": "Turns off all audio filters and returns the song to normal.",
            "help": "Shows this helpful guide to all the bot's commands!"
        }

        commands_list = []
        for command in self.bot.walk_commands():
            if not command.hidden:
                commands_list.append(command)
                
        commands_list.sort(key=lambda x: x.qualified_name)
        
        per_page = 6
        chunks = [commands_list[i:i + per_page] for i in range(0, len(commands_list), per_page)]
        
        embeds = []
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=f"📚 Bot Commands (Page {i+1}/{len(chunks)})",
                description="Here is a list of all available commands in easy-to-understand language:",
                color=discord.Color.blurple()
            )
            
            for cmd in chunk:
                aliases = f" (Aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
                
                # Format usage with parent command if it exists
                parent = f"{cmd.parent.name} " if cmd.parent else ""
                usage = f"`f#{parent}{cmd.name} {cmd.signature}`".strip()
                
                # Check for friendly description
                desc = friendly_descriptions.get(cmd.name, cmd.help or "No description provided.")
                
                embed.add_field(
                    name=f"🔹 {parent}{cmd.name}{aliases}",
                    value=f"**Description:** {desc}\n**Usage:** {usage}",
                    inline=False
                )
            
            embed.set_footer(text="Use the buttons below to navigate pages.")
            embeds.append(embed)
            
        if len(embeds) == 0:
            await ctx.send("No commands found.")
        elif len(embeds) == 1:
            await ctx.send(embed=embeds[0])
        else:
            view = HelpPaginationView(embeds)
            await ctx.send(embed=embeds[0], view=view)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
