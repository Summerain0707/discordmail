import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

DB_PATH = "bot.db"

class Projects(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_project", description="新增一個程式項目")
    async def add_project(
        self,
        interaction: discord.Interaction,
        name: str,
        repo_name: str,
        check_interval_days: int,
        notify_channel: discord.TextChannel
    ):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projects (user_id, name, repo_name, check_interval_days, notify_channel_id)
            VALUES (?, ?, ?, ?, ?)
        """, (str(interaction.user.id), name, repo_name, check_interval_days, str(notify_channel.id)))
        conn.commit()
        conn.close()
        await interaction.response.send_message(
            f" 已新增項目：**{name}**\n"
            f"Repository：`{repo_name}`\n"
            f" 查詢頻率：每 {check_interval_days} 天\n"
            f"通知頻道：{notify_channel.mention}"
        )

    @app_commands.command(name="my_projects", description="查看我的所有項目")
    async def my_projects(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, repo_name, check_interval_days, notify_channel_id
            FROM projects
            WHERE user_id = ?
        """, (str(interaction.user.id),))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message("你還沒有任何項目，用 `/add_project` 新增吧！")
            return

        msg = "**你的項目清單：**\n"
        for row in rows:
            msg += (
                f"• `#{row[0]}` **{row[1]}**\n"
                f"  repo：`{row[2]}`\n"
                f"  每 {row[3]} 天查詢一次\n"
                f"   通知頻道：<#{row[4]}>\n"
            )
        await interaction.response.send_message(msg)

async def setup(bot):
    await bot.add_cog(Projects(bot))