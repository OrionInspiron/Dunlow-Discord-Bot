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
        cogs = self.bot.cogs
        commands_list = []
        
        # Gather all commands
        for command in self.bot.commands:
            if not command.hidden:
                commands_list.append(command)
                
        # Sort by name
        commands_list.sort(key=lambda x: x.name)
        
        # Paginate commands (6 per page)
        per_page = 6
        chunks = [commands_list[i:i + per_page] for i in range(0, len(commands_list), per_page)]
        
        embeds = []
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=f"📚 Bot Commands (Page {i+1}/{len(chunks)})",
                description="Here is a list of all available commands:",
                color=discord.Color.blurple()
            )
            
            for cmd in chunk:
                # Format aliases if any
                aliases = f" (Aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
                
                # Format usage
                usage = f"`f#{cmd.name} {cmd.signature}`"
                
                embed.add_field(
                    name=f"🔹 {cmd.name}{aliases}",
                    value=f"**Usage:** {usage}\n**Description:** {cmd.help or 'No description provided.'}",
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
