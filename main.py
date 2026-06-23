import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.tree.command(
    name="ping",
    description="Test bot"
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🏹 Albion Party Bot Online!"
    )

@bot.tree.command(
    name="party",
    description="Create Party"
)
async def party(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📢 AVA NEW ROUTE",
        description=f"Leader: {interaction.user.mention}",
        color=0x5865F2
    )

    embed.add_field(
        name="Main Tank",
        value="Kosong",
        inline=False
    )

    embed.add_field(
        name="Holy",
        value="Kosong",
        inline=False
    )

    embed.add_field(
        name="DPS",
        value="Kosong",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.event
async def on_ready():

    print("Bot Login")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Sync Error: {e}")

    print(f"Online : {bot.user}")

bot.run(TOKEN)
