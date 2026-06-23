import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ======================
# PARTY DATA
# ======================

party_data = {
    "Incubus Mace": None,
    "Holy Staff": None,
    "Shadowcaller": None,
    "Mistpiercer": None
}


def create_embed():
    embed = discord.Embed(
        title="⚔️ SMALL SCALE PARTY",
        color=discord.Color.blue()
    )

    for role, player in party_data.items():
        embed.add_field(
            name=role,
            value=player if player else "Kosong",
            inline=False
        )

    joined = len([x for x in party_data.values() if x])
    embed.set_footer(text=f"Slot Terisi: {joined}/4")

    return embed


class PartyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    async def join_role(self, interaction, role_name):

        user = interaction.user.display_name

        # Cegah masuk 2 role
        if user in party_data.values():
            await interaction.response.send_message(
                "Kamu sudah berada di party.",
                ephemeral=True
            )
            return

        if party_data[role_name]:
            await interaction.response.send_message(
                "Slot sudah terisi.",
                ephemeral=True
            )
            return

        party_data[role_name] = user

        await interaction.response.edit_message(
            embed=create_embed(),
            view=self
        )

    @discord.ui.button(label="Incubus Mace", style=discord.ButtonStyle.primary)
    async def incubus(self, interaction, button):
        await self.join_role(interaction, "Incubus Mace")

    @discord.ui.button(label="Holy Staff", style=discord.ButtonStyle.success)
    async def holy(self, interaction, button):
        await self.join_role(interaction, "Holy Staff")

    @discord.ui.button(label="Shadowcaller", style=discord.ButtonStyle.secondary)
    async def shadow(self, interaction, button):
        await self.join_role(interaction, "Shadowcaller")

    @discord.ui.button(label="Mistpiercer", style=discord.ButtonStyle.danger)
    async def mist(self, interaction, button):
        await self.join_role(interaction, "Mistpiercer")

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
    async def cancel(self, interaction, button):

        user = interaction.user.display_name

        for role in party_data:
            if party_data[role] == user:
                party_data[role] = None

        await interaction.response.edit_message(
            embed=create_embed(),
            view=self
        )


@bot.event
async def on_ready():
    print(f"Bot online sebagai {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send("🏹 Albion Party Bot Online!")


@bot.command()
async def party(ctx):

    for role in party_data:
        party_data[role] = None

    await ctx.send(
        embed=create_embed(),
        view=PartyView()
    )


bot.run(TOKEN)
