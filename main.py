import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ==========================
# READY
# ==========================

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

    print(f"Online : {bot.user}")
    
@bot.tree.error
async def on_app_command_error(interaction, error):
    print(f"ERROR COMMAND: {error}")
# ==========================
# PING
# ==========================

@bot.tree.command(
    name="ping",
    description="Tes bot"
)
async def ping(interaction: discord.Interaction):

    await interaction.response.send_message(
        "🏓 Pong!",
        ephemeral=True
    )

# ==========================
# PARTY TEST
# ==========================

@bot.tree.command(
    name="party",
    description="Create Party"
)
async def party(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📢 AVA NEW ROUTE",
        color=0x5865F2
    )

    embed.add_field(
        name="🛡 Main Tank",
        value="Kosong",
        inline=False
    )

    embed.add_field(
        name="💚 Holy",
        value="Kosong",
        inline=False
    )

    embed.add_field(
        name="⚔ DPS 1",
        value="Kosong",
        inline=False
    )

    embed.add_field(
        name="⚔ DPS 2",
        value="Kosong",
        inline=False
    )

    embed.add_field(
        name="👁 Scout",
        value="Kosong",
        inline=False
    )

    embed.set_footer(text="0/5 Slot")

    await interaction.response.send_message(
        embed=embed
    )

bot.run(TOKEN)
