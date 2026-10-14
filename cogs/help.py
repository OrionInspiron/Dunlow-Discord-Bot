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
    """Help documentation for the 24/7 Soothing Lofi Radio Bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", help="Shows the soothing lofi radio command guide.")
    async def help_command(self, ctx):
        friendly_descriptions = {
            "radio": "Summons the bot into your voice channel and begins streaming continuous soothing non-lyrical melodies directly from lofi.radio.",
            "shuffle": "Randomizes the remaining upcoming melodies in the radio queue.",
            "next": "Skips immediately to the next soothing melody.",
            "previous": "Plays the previous soothing melody from recent playback history.",
            "pause": "Pauses the soothing radio stream.",
            "resume": "Resumes playing the paused radio stream.",
            "nowplaying": "Shows the current melody card with interactive control buttons.",
            "queue": "Displays the rotating lineup of upcoming soothing melodies.",
            "volume": "Adjusts the radio volume (1-100%).",
            "247": "Toggles 24/7 mode (keeps the bot in the voice channel continuously).",
            "stop": "Stops the radio and disconnects from your voice channel.",
            "restart": "Restarts the bot internally (Admins/Owners only).",
            "help": "Displays this helpful command guide."
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
                title=f"📻 Lofi Radio Bot • Commands (Page {i+1}/{len(chunks)})",
                description="24/7 non-lyrical chill beats to study, relax, and sleep powered directly by **[lofi.radio](https://lofi.radio/)**.\nHere are the available commands:",
                color=discord.Color.from_rgb(0, 209, 178)
            )

            for cmd in chunk:
                aliases = f" (Aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
                parent = f"{cmd.parent.name} " if cmd.parent else ""
                usage = f"`f#{parent}{cmd.name} {cmd.signature}`".strip()

                desc = friendly_descriptions.get(cmd.name, cmd.help or "No description provided.")

                embed.add_field(
                    name=f"🔹 {parent}{cmd.name}{aliases}",
                    value=f"**Description:** {desc}\n**Usage:** {usage}",
                    inline=False
                )

            embed.set_footer(text="Use the buttons below to flip through pages • Prefix: f#")
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
