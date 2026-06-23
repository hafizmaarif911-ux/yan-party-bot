import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

parties = {}

# ==========================================
# EMBED BUILDER
# ==========================================

def build_embed(party_id):

    data = parties[party_id]

    embed = discord.Embed(
        title=f"📢 {data['name']}",
        color=0x5865F2
    )

    joined = 0

    for slot in data["slots"]:

        member = data["members"][slot]

        if member:
            value = f"<@{member}>"
            joined += 1
        else:
            value = "Kosong"

        embed.add_field(
            name=slot,
            value=value,
            inline=False
        )

    embed.description = (
        f"Leader: <@{data['leader']}>\n"
        f"Status: {joined}/{len(data['slots'])}"
    )

    return embed

# ==========================================
# PARTY VIEW
# ==========================================

class PartyView(discord.ui.View):

    def __init__(self, party_id):

        super().__init__(timeout=None)

        self.party_id = party_id

        data = parties[party_id]

        for slot in data["slots"]:

            button = discord.ui.Button(
                label=slot,
                style=discord.ButtonStyle.primary
            )

            async def callback(
                interaction,
                slot_name=slot
            ):
                await join_slot(
                    interaction,
                    party_id,
                    slot_name
                )

            button.callback = callback

            self.add_item(button)

        leave = discord.ui.Button(
            label="LEAVE",
            style=discord.ButtonStyle.secondary
        )

        massing = discord.ui.Button(
            label="MASSING NOW",
            style=discord.ButtonStyle.success
        )

        cancel = discord.ui.Button(
            label="CANCEL",
            style=discord.ButtonStyle.danger
        )

        # LEAVE

        async def leave_callback(interaction):

            user = interaction.user.id

            for slot in data["slots"]:

                if data["members"][slot] == user:
                    data["members"][slot] = None

            await interaction.message.edit(
                embed=build_embed(party_id),
                view=PartyView(party_id)
            )

            await interaction.response.send_message(
                "Keluar dari party.",
                ephemeral=True
            )

        leave.callback = leave_callback

        # MASSING

        async def massing_callback(interaction):

            if interaction.user.id != data["leader"]:
                return await interaction.response.send_message(
                    "Hanya leader.",
                    ephemeral=True
                )

            mentions = []

            for slot in data["slots"]:

                member = data["members"][slot]

                if member:
                    mentions.append(
                        f"<@{member}>"
                    )

            await interaction.channel.send(
                "🔔 MASSING NOW!\n\n"
                + "\n".join(mentions)
            )

            await interaction.response.defer()

        massing.callback = massing_callback

        # CANCEL

        async def cancel_callback(interaction):

            if interaction.user.id != data["leader"]:
                return await interaction.response.send_message(
                    "Hanya leader.",
                    ephemeral=True
                )

            del parties[party_id]

            await interaction.message.edit(
                content="❌ Content dibatalkan.",
                embed=None,
                view=None
            )

            await interaction.response.defer()

        cancel.callback = cancel_callback

        self.add_item(leave)
        self.add_item(massing)
        self.add_item(cancel)

# ==========================================
# JOIN SLOT
# ==========================================

async def join_slot(
    interaction,
    party_id,
    slot_name
):

    data = parties[party_id]

    user = interaction.user.id

    # hapus slot lama

    for slot in data["slots"]:

        if data["members"][slot] == user:
            data["members"][slot] = None

    # cek penuh

    if data["members"][slot_name]:

        return await interaction.response.send_message(
            "Slot sudah diisi.",
            ephemeral=True
        )

    data["members"][slot_name] = user

    await interaction.message.edit(
        embed=build_embed(party_id),
        view=PartyView(party_id)
    )

    await interaction.response.send_message(
        f"Masuk ke {slot_name}",
        ephemeral=True
    )

# ==========================================
# MODAL
# ==========================================

class PartyModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="Create Albion Party"
        )

        self.party_name = discord.ui.TextInput(
            label="Nama Content",
            placeholder="AVA NEW ROUTE"
        )

        self.slots = discord.ui.TextInput(
            label="Slot",
            style=discord.TextStyle.paragraph,
            placeholder=(
                "Main Tank\n"
                "Holy\n"
                "DPS 1\n"
                "DPS 2\n"
                "Scout"
            )
        )

        self.add_item(self.party_name)
        self.add_item(self.slots)

    async def on_submit(
        self,
        interaction
    ):

        party_id = len(parties) + 1

        slot_list = [
            x.strip()
            for x in self.slots.value.splitlines()
            if x.strip()
        ]

        parties[party_id] = {

            "name": self.party_name.value,

            "leader": interaction.user.id,

            "slots": slot_list,

            "members": {
                slot: None
                for slot in slot_list
            }
        }

        await interaction.response.send_message(
            embed=build_embed(party_id),
            view=PartyView(party_id)
        )

# ==========================================
# COMMAND
# ==========================================

@bot.tree.command(
    name="party",
    description="Create Albion Party"
)
async def party(interaction):

    await interaction.response.send_message(
        "Party command jalan!",
        ephemeral=True
    )

# ==========================================
# READY
# ==========================================

@bot.event
async def on_ready():

    await bot.tree.sync()

    print(f"Online : {bot.user}")

bot.run(TOKEN)
