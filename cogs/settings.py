import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

DB_PATH = "bot.db"

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_github", description="綁定你的 GitHub 帳號")
    async def set_github(self, interaction: discord.Interaction, username: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, github_username)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET github_username = ?
        """, (str(interaction.user.id), username, username))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"✅ 已綁定 GitHub 帳號：`{username}`")

async def setup(bot):
    await bot.add_cog(Settings(bot))