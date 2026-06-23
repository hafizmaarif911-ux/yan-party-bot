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

parties = {}

# =====================================
# EMBED
# =====================================

def build_embed(content_id):

    data = parties[content_id]

    embed = discord.Embed(
        title=f"📢 {data['name']}",
        color=0x5865F2
    )

    joined = 0

    for role in data["roles"]:

        user = data["members"][role]

        if user:
            value = f"<@{user}>"
            joined += 1
        else:
            value = "Kosong"

        embed.add_field(
            name=role,
            value=value,
            inline=False
        )

    embed.description = (
        f"Leader: <@{data['leader']}>\n"
        f"Status: {joined}/{len(data['roles'])}"
    )

    return embed


# =====================================
# JOIN BUTTON
# =====================================

class JoinButton(discord.ui.Button):

    def __init__(self, content_id, role_name):

        super().__init__(
            label=role_name,
            style=discord.ButtonStyle.primary
        )

        self.content_id = content_id
        self.role_name = role_name

    async def callback(self, interaction):

        data = parties[self.content_id]
        user_id = interaction.user.id

        # hapus role lama

        for role in data["roles"]:
            if data["members"][role] == user_id:
                data["members"][role] = None

        # role sudah diisi

        if data["members"][self.role_name]:
            return await interaction.response.send_message(
                "Role sudah diisi.",
                ephemeral=True
            )

        data["members"][self.role_name] = user_id

        await interaction.message.edit(
            embed=build_embed(self.content_id),
            view=PartyView(self.content_id)
        )

        await interaction.response.send_message(
            f"Masuk ke {self.role_name}",
            ephemeral=True
        )


# =====================================
# VIEW
# =====================================

class PartyView(discord.ui.View):

    def __init__(self, content_id):

        super().__init__(timeout=None)

        self.content_id = content_id

        data = parties[content_id]

        for role in data["roles"]:
            self.add_item(
                JoinButton(content_id, role)
            )

        leave = discord.ui.Button(
            label="Leave",
            style=discord.ButtonStyle.secondary
        )

        massing = discord.ui.Button(
            label="Massing",
            style=discord.ButtonStyle.success
        )

        cancel = discord.ui.Button(
            label="Cancel",
            style=discord.ButtonStyle.danger
        )

        # LEAVE

        async def leave_callback(interaction):

            user = interaction.user.id

            for role in data["roles"]:
                if data["members"][role] == user:
                    data["members"][role] = None

            await interaction.message.edit(
                embed=build_embed(content_id),
                view=PartyView(content_id)
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

            for role in data["roles"]:

                member = data["members"][role]

                if member:
                    mentions.append(f"<@{member}>")

            await interaction.channel.send(
                "🔔 MASSING NOW!\n\n" +
                "\n".join(mentions)
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

            del parties[content_id]

            await interaction.message.edit(
                content="❌ Content dibatalkan",
                embed=None,
                view=None
            )

            await interaction.response.defer()

        cancel.callback = cancel_callback

        self.add_item(leave)
        self.add_item(massing)
        self.add_item(cancel)


# =====================================
# MODAL
# =====================================

class ContentModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="Create Content"
        )

        self.content_name = discord.ui.TextInput(
            label="Nama Content",
            placeholder="AVA NEW ROUTE"
        )

        self.roles = discord.ui.TextInput(
            label="Role",
            style=discord.TextStyle.paragraph,
            placeholder="Main Tank\nHoly\nDPS 1\nDPS 2\nScout"
        )

        self.add_item(self.content_name)
        self.add_item(self.roles)

    async def on_submit(self, interaction):

        content_id = len(parties) + 1

        role_list = [
            role.strip()
            for role in self.roles.value.splitlines()
            if role.strip()
        ]

        parties[content_id] = {
            "name": self.content_name.value,
            "leader": interaction.user.id,
            "roles": role_list,
            "members": {
                role: None
                for role in role_list
            }
        }

        await interaction.response.send_message(
            embed=build_embed(content_id),
            view=PartyView(content_id)
        )


# =====================================
# COMMAND
# =====================================

@bot.tree.command(
    name="content",
    description="Create Albion Content"
)
async def content(interaction: discord.Interaction):

    await interaction.response.send_modal(
        ContentModal()
    )


@bot.tree.command(
    name="ping",
    description="Ping bot"
)
async def ping(interaction: discord.Interaction):

    await interaction.response.send_message(
        "🏹 Albion Party Bot Online!"
    )


# =====================================
# READY
# =====================================

@bot.event
async def on_ready():

    print("Bot Login")

    synced = await bot.tree.sync()

    print(f"Synced {len(synced)} commands")
    print(f"Online : {bot.user}")


bot.run(TOKEN)
