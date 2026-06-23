import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Menyimpan data party sementara
parties = {}

# =====================================
# VIEW PARTY
# =====================================

class PartyView(discord.ui.View):

    def __init__(self, party_id):
        super().__init__(timeout=None)

        self.party_id = party_id

        data = parties[party_id]

        for role in data["roles"]:

            button = discord.ui.Button(
                label=role,
                style=discord.ButtonStyle.primary
            )

            async def callback(interaction, role_name=role):
                await join_role(interaction, party_id, role_name)

            button.callback = callback

            self.add_item(button)

        massing = discord.ui.Button(
            label="MASSING NOW",
            style=discord.ButtonStyle.success
        )

        cancel = discord.ui.Button(
            label="CANCEL",
            style=discord.ButtonStyle.danger
        )

        async def massing_callback(interaction):

            if interaction.user.id != data["leader"]:
                return await interaction.response.send_message(
                    "Hanya leader yang bisa massing.",
                    ephemeral=True
                )

            mentions = []

            for members in data["members"].values():
                mentions.extend(members)

            text = "\n".join(
                f"<@{m}>"
                for m in mentions
            )

            await interaction.channel.send(
                f"🔔 MASSING NOW!\n\n{text}"
            )

            await interaction.response.defer()

        async def cancel_callback(interaction):

            if interaction.user.id != data["leader"]:
                return await interaction.response.send_message(
                    "Hanya leader yang bisa cancel.",
                    ephemeral=True
                )

            parties.pop(party_id)

            await interaction.message.edit(
                content="❌ Content dibatalkan.",
                embed=None,
                view=None
            )

            await interaction.response.defer()

        massing.callback = massing_callback
        cancel.callback = cancel_callback

        self.add_item(massing)
        self.add_item(cancel)

# =====================================
# EMBED
# =====================================

def build_embed(party_id):

    data = parties[party_id]

    embed = discord.Embed(
        title=f"📢 {data['name']}",
        color=0x2f3136
    )

    total = 0
    current = 0

    for role, limit in data["roles"].items():

        members = data["members"][role]

        current += len(members)
        total += limit

        if members:
            value = "\n".join(
                f"<@{m}>"
                for m in members
            )
        else:
            value = "Kosong"

        embed.add_field(
            name=f"{role} ({len(members)}/{limit})",
            value=value,
            inline=False
        )

    embed.set_footer(
        text=f"{current}/{total} Slot"
    )

    return embed

# =====================================
# JOIN ROLE
# =====================================

async def join_role(interaction, party_id, role_name):

    data = parties[party_id]

    user = interaction.user.id

    for role in data["members"]:

        if user in data["members"][role]:
            data["members"][role].remove(user)

    if len(data["members"][role_name]) >= data["roles"][role_name]:

        return await interaction.response.send_message(
            "Role sudah penuh.",
            ephemeral=True
        )

    data["members"][role_name].append(user)

    await interaction.message.edit(
        embed=build_embed(party_id),
        view=PartyView(party_id)
    )

    await interaction.response.send_message(
        f"Masuk sebagai {role_name}",
        ephemeral=True
    )

# =====================================
# MODAL
# =====================================

class PartyModal(discord.ui.Modal, title="Create Party"):

    content_name = discord.ui.TextInput(
        label="Nama Content"
    )

    role_data = discord.ui.TextInput(
        label="Role",
        style=discord.TextStyle.paragraph,
        placeholder="Holy:1\nDPS:4\nTank:1"
    )

    async def on_submit(self, interaction):

        party_id = len(parties) + 1

        roles = {}

        for line in self.role_data.value.splitlines():

            role, amount = line.split(":")

            roles[role.strip()] = int(amount)

        parties[party_id] = {
            "name": self.content_name.value,
            "leader": interaction.user.id,
            "roles": roles,
            "members": {
                r: []
                for r in roles
            }
        }

        embed = build_embed(party_id)

        await interaction.response.send_message(
            embed=embed,
            view=PartyView(party_id)
        )

# =====================================
# SLASH COMMAND
# =====================================

@bot.tree.command(
    name="content",
    description="Buat Content Albion"
)
async def content(interaction):

    await interaction.response.send_modal(
        PartyModal()
    )

# =====================================
# READY
# =====================================

@bot.event
async def on_ready():

    await bot.tree.sync()

    print(bot.user)

bot.run(TOKEN)
