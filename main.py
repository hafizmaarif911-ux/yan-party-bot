import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import (
    init_db,
    save_content,
    save_attendance,
    get_history,
    get_stats,
    get_top_attendance
)

load_dotenv()

TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNELS = [
    1440319464800391310,
	1498327389393129664,
]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

parties = {}
def channel_allowed(interaction):
    return interaction.channel.id in ALLOWED_CHANNELS
# =====================================
# EMBED
# =====================================

def build_embed(content_id):

    data = parties[content_id]

    embed = discord.Embed(
        title=f"⚔️ {data['name']}",
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

    embed.set_footer(
        text="Klik tombol untuk mengambil role"
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

    async def callback(self, interaction: discord.Interaction):

        if self.content_id not in parties:

            return await interaction.response.send_message(
                "❌ Content sudah selesai atau dibatalkan.",
                ephemeral=True
            )

        data = parties[self.content_id]
        user_id = interaction.user.id

        # Hapus role lama user
        for role in data["roles"]:

            if data["members"][role] == user_id:
                data["members"][role] = None

        # Role sudah diisi
        if data["members"][self.role_name]:

            return await interaction.response.send_message(
                "❌ Role sudah diisi.",
                ephemeral=True
            )

        # Isi role
        data["members"][self.role_name] = user_id

        # Update embed
        await interaction.message.edit(
            embed=build_embed(self.content_id),
            view=PartyView(self.content_id)
        )

        # Kirim notif ke thread
        thread_id = data.get("thread_id")

        if thread_id:

            thread = interaction.guild.get_thread(thread_id)

            if thread:

                await thread.send(
                    f"✅ <@{user_id}> mengambil role **{self.role_name}**"
                )

        # Notif hanya ke user
        await interaction.response.send_message(
            f"✅ Berhasil mengambil role {self.role_name}",
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

        # ROLE BUTTONS
        for role in data["roles"]:
            self.add_item(
                JoinButton(content_id, role)
            )

        # CONTROL BUTTONS
        leave = discord.ui.Button(
            label="Leave",
            style=discord.ButtonStyle.secondary
        )

        massing = discord.ui.Button(
            label="Massing",
            style=discord.ButtonStyle.primary
        )

        finish = discord.ui.Button(
            label="Finish",
            style=discord.ButtonStyle.success
        )

        cancel = discord.ui.Button(
            label="Cancel",
            style=discord.ButtonStyle.danger
        )

        # =========================
        # LEAVE
        # =========================

        async def leave_callback(interaction):

            if content_id not in parties:
                return await interaction.response.send_message(
                    "❌ Content sudah selesai.",
                    ephemeral=True
                )

            user_id = interaction.user.id

            for role in data["roles"]:

                if data["members"][role] == user_id:
                    data["members"][role] = None

            await interaction.message.edit(
                embed=build_embed(content_id),
                view=PartyView(content_id)
            )

            thread_id = data.get("thread_id")

            if thread_id:

                thread = interaction.guild.get_thread(thread_id)

                if thread:

                    await thread.send(
                        f"❌ <@{user_id}> keluar dari party"
                    )

            await interaction.response.send_message(
                "Keluar dari party.",
                ephemeral=True
            )

        leave.callback = leave_callback

        # =========================
        # MASSING
        # =========================

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

            message = (
                f"⚔️ **{data['name']}**\n\n"
                f"📢 **MASSING NOW**\n"
                f"Caller: <@{data['leader']}> memanggil pasukan\n\n"
                f"{' '.join(mentions)}\n\n"
                f"Gear up, mount up, let's move!"
            )

            thread_id = data.get("thread_id")

            if thread_id:

                thread = interaction.guild.get_thread(thread_id)

                if thread:
                    await thread.send(message)

            await interaction.response.send_message(
                "Massing berhasil dikirim.",
                ephemeral=True
            )

        massing.callback = massing_callback
        # =========================
        # FINISH
        # =========================

        async def finish_callback(interaction):

            if interaction.user.id != data["leader"]:
                return await interaction.response.send_message(
                    "Hanya leader yang bisa finish content.",
                    ephemeral=True
                )

            await interaction.response.send_modal(
                FinishModal(content_id)
            )

        finish.callback = finish_callback

        # =========================
        # CANCEL
        # =========================

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

            await interaction.response.send_message(
                "Content dibatalkan.",
                ephemeral=True
            )

        cancel.callback = cancel_callback

        # ADD BUTTONS
        self.add_item(leave)
        self.add_item(massing)
        self.add_item(finish)
        self.add_item(cancel)
		

# =====================================
# MODAL
# =====================================
class FinishModal(discord.ui.Modal):

    def __init__(self, content_id):

        super().__init__(title="Finish Content")

        self.content_id = content_id

        self.silver_bag = discord.ui.TextInput(
            label="Silver Bag Value",
            placeholder="5000000"
        )

        self.item_value = discord.ui.TextInput(
            label="Item Value",
            placeholder="2500000"
        )

        self.add_item(self.silver_bag)
        self.add_item(self.item_value)

    async def on_submit(self, interaction):

        data = parties[self.content_id]

        silver_bag = int(self.silver_bag.value)
        item_value = int(self.item_value.value)

        total_loot = silver_bag + item_value

        members = []

        for role in data["roles"]:

            user_id = data["members"][role]

            if user_id:
                members.append(user_id)

        total_members = len(members)

        split_value = (
            total_loot // total_members
            if total_members > 0
            else 0
        )

        content_db_id = await save_content(
            data["name"],
            interaction.user.name,
            data["leader"],
            total_members,
            silver_bag,
            item_value,
            total_loot,
            split_value
        )

        for role in data["roles"]:

            user_id = data["members"][role]

            if user_id:

                user = await bot.fetch_user(user_id)

                await save_attendance(
                    content_db_id,
                    user_id,
                    user.name,
                    role
                )

        embed = discord.Embed(
            title="✅ Content Finished",
            color=0x2ECC71
        )

        embed.add_field(
            name="Silver Bag",
            value=f"{silver_bag:,}",
            inline=False
        )

        embed.add_field(
            name="Item Value",
            value=f"{item_value:,}",
            inline=False
        )

        embed.add_field(
            name="Total Loot",
            value=f"{total_loot:,}",
            inline=False
        )

        embed.add_field(
            name="Split Per Member",
            value=f"{split_value:,}",
            inline=False
        )
        await interaction.response.send_message(
            embed=embed
        )

        thread_id = data.get("thread_id")

        if thread_id:

            thread = interaction.guild.get_thread(thread_id)

            if thread:

                await thread.send(
                    f"""
✅ CONTENT FINISHED

💰 Silver Bag : {silver_bag:,}
📦 Item Value : {item_value:,}
💎 Total Loot : {total_loot:,}
👥 Split : {split_value:,}
"""
                )

        del parties[self.content_id]
class ContentModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="Create Content"
        )

        self.content_name = discord.ui.TextInput(
            label="Nama Content",
            placeholder="NAMA CONTEN"
        )

        self.roles = discord.ui.TextInput(
            label="Role",
            style=discord.TextStyle.paragraph,
            placeholder="Main Tank\nHealer\nDPS 1\nDPS 2\nScout"
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
            "thread_id": None,
            "roles": role_list,
            "members": {
                role: None
                for role in role_list
            }
        }

        msg = await interaction.channel.send(
            embed=build_embed(content_id),
            view=PartyView(content_id)
        )

        thread = await msg.create_thread(
            name=self.content_name.value
        )

        parties[content_id]["thread_id"] = thread.id

        await interaction.response.send_message(
            f"✅ Content dibuat: {thread.mention}",
            ephemeral=True
        )

# =====================================
# COMMAND
# =====================================

@bot.tree.command(
    name="content",
    description="Create Albion Content"
)
async def content(interaction: discord.Interaction):

    if not channel_allowed(interaction):
        return await interaction.response.send_message(
            "❌ Command ini hanya dapat digunakan di channel content yang ditentukan.",
            ephemeral=True
        )

    await interaction.response.send_modal(
        ContentModal()
    )


@bot.tree.command(
    name="sayhi",
    description="Say hi to YPing"
)
async def ping(interaction: discord.Interaction):

    await interaction.response.send_message(
        "👋 Halo, sayang!"
    )

@bot.tree.command(
    name="history",
    description="Lihat history content"
)
async def history(interaction: discord.Interaction):

    if not channel_allowed(interaction):
        return await interaction.response.send_message(
            "❌ Gunakan command ini di channel content.",
            ephemeral=True
        )

    rows = await get_history()

    if not rows:
        return await interaction.response.send_message(
            "Belum ada history.",
            ephemeral=True
        )

    embed = discord.Embed(
        title="📜 Content History",
        color=0x2ecc71
    )

    for row in rows:

        embed.add_field(
            name=f"#{row[0]} - {row[1]}",
            value=(
                f"👥 {row[4]} Member\n"
                f"💰 {row[7]:,} Silver"
            ),
            inline=False
        )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="stats",
    description="Guild Stats"
)
async def stats(interaction: discord.Interaction):

    if not channel_allowed(interaction):
        return await interaction.response.send_message(
            "❌ Gunakan command ini di channel content.",
            ephemeral=True
        )

    data = await get_stats()

    total_content = data[0]
    total_loot = data[1]
    total_silver = data[2]
    total_item = data[3]

    top = await get_top_attendance()

    embed = discord.Embed(
        title="📊 Guild Stats",
        color=0xf1c40f
    )

    embed.add_field(
        name="Total Content",
        value=f"{total_content}",
        inline=False
    )

    embed.add_field(
        name="Silver Bag",
        value=f"{total_silver:,}",
        inline=False
    )

    embed.add_field(
        name="Item Value",
        value=f"{total_item:,}",
        inline=False
    )

    embed.add_field(
        name="Total Loot",
        value=f"{total_loot:,}",
        inline=False
    )

    if top:

        ranking = ""

        for i, row in enumerate(top, start=1):

            ranking += (
                f"{i}. {row[0]} "
                f"({row[1]})\n"
            )

        embed.add_field(
            name="🏆 Attendance",
            value=ranking,
            inline=False
        )

    await interaction.response.send_message(
        embed=embed
    )

# =====================================
# READY
# =====================================

@bot.event
async def on_ready():

    print("=" * 40)
    print(f"Online : {bot.user}")
    print("=" * 40)

    for guild in bot.guilds:
        print(
            f"{guild.name} ({guild.id})"
        )

    await init_db()

    synced = await bot.tree.sync()

    print(f"Synced {len(synced)} commands")

bot.run(TOKEN)
