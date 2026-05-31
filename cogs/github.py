import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import sqlite3
from datetime import datetime, timezone, timedelta
from discord.ext import tasks
import datetime as dt

DB_PATH = "bot.db"


CHECK_TIME = dt.time(hour=5, minute=1, tzinfo=timezone.utc)

async def fetch_latest_commit(session, github_username, repo_name):
    """呼叫GitHub API，回傳最新commit時間，或None（失敗時）"""
    url = f"https://api.github.com/repos/{github_username}/{repo_name}/commits?per_page=1"
    async with session.get(url, headers={"Accept": "application/vnd.github+json"}) as resp:
        if resp.status != 200:
            return None, resp.status
        commits = await resp.json()
        if not commits:
            return None, "empty"
        time_str = commits[0]["commit"]["author"]["date"]
        return datetime.fromisoformat(time_str.replace("Z", "+00:00")), None

class GitHub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_check.start()  # bot啟動時自動開始定時任務

    def cog_unload(self):
        self.daily_check.cancel()  # bot關閉時停止定時任務

    # ==================
    # 手動查詢指令
    # ==================

    @app_commands.command(name="check_repo", description="手動查詢指定項目的 repo 是否有新 commit")
    async def check_repo(self, interaction: discord.Interaction, project_id: int):

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.repo_name, p.check_interval_days, u.github_username
            FROM projects p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.id = ? AND p.user_id = ?
        """, (project_id, str(interaction.user.id)))
        row = cursor.fetchone()
        conn.close()

        if not row:
            await interaction.response.send_message(
                f"❌ 找不到項目 `#{project_id}`，請用 `/my_projects` 確認編號。"
            )
            return

        project_name, repo_name, check_interval_days, github_username = row

        if not github_username:
            await interaction.response.send_message(
                "❌ 你還沒有綁定 GitHub 帳號，請先用 `/set_github` 綁定！"
            )
            return

        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            latest_commit_time, error = await fetch_latest_commit(session, github_username, repo_name)

        if error == 404:
            await interaction.followup.send(f"⚠️ 找不到 repo `{github_username}/{repo_name}`。")
            return
        if error:
            await interaction.followup.send(f"⚠️ 無法取得 commit 資料（{error}），請稍後再試。")
            return

        now = datetime.now(timezone.utc)
        threshold = now - timedelta(days=check_interval_days)

        if latest_commit_time >= threshold:
            await interaction.followup.send(
                f"✅ **{project_name}** 達標！\n"
                f" `{github_username}/{repo_name}`\n"
                f" 最新 commit：{latest_commit_time.strftime('%Y-%m-%d %H:%M')} UTC\n"
                f" 查詢範圍：過去 {check_interval_days} 天內"
            )
        else:
            await interaction.followup.send(
                f"❌ **{project_name}** 未達標！\n"
                f" `{github_username}/{repo_name}`\n"
                f" 最新 commit：{latest_commit_time.strftime('%Y-%m-%d %H:%M')} UTC\n"
                f" 查詢範圍：過去 {check_interval_days} 天內\n"
                f" 快去寫程式吧！"
            )

    # ==================
    # 定時任務
    # ==================

    @tasks.loop(time=CHECK_TIME)  # 每天UTC 14:00（台灣時間22:00）執行
    async def daily_check(self):
        """每天自動查詢所有project，核對是否有commit，並通知使用者"""

        # 取出所有project
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.repo_name, p.check_interval_days,
                   p.notify_channel_id, p.user_id, u.github_username
            FROM projects p
            JOIN users u ON p.user_id = u.user_id
            WHERE u.github_username IS NOT NULL
        """)
        projects = cursor.fetchall()
        conn.close()

        async with aiohttp.ClientSession() as session:
            for project in projects:
                project_id, project_name, repo_name, check_interval_days, \
                notify_channel_id, user_id, github_username = project

                latest_commit_time, error = await fetch_latest_commit(
                    session, github_username, repo_name
                )

                # 取得通知頻道
                channel = self.bot.get_channel(int(notify_channel_id))
                if not channel:
                    continue  # 找不到頻道就跳過

                now = datetime.now(timezone.utc)
                threshold = now - timedelta(days=check_interval_days)

                if error:
                    # API失敗，只發頻道訊息
                    await channel.send(
                        f"⚠️ 無法查詢 **{project_name}** 的 commit 資料（`{github_username}/{repo_name}`）"
                    )
                    continue

                if latest_commit_time >= threshold:
                    # 達標，只發頻道訊息
                    await channel.send(
                        f"✅ <@{user_id}> 的 **{project_name}** 達標！\n"
                        f"`{github_username}/{repo_name}`\n"
                        f"最新 commit：{latest_commit_time.strftime('%Y-%m-%d %H:%M')} UTC"
                    )
                else:
                    # 未達標，頻道訊息 + 私訊
                    await channel.send(
                        f"❌ <@{user_id}> 的 **{project_name}** 未達標！\n"
                        f" `{github_username}/{repo_name}`\n"
                        f" 最新 commit：{latest_commit_time.strftime('%Y-%m-%d %H:%M')} UTC\n"
                    )
                    # 私訊使用者
                    try:
                        user = await self.bot.fetch_user(int(user_id))
                        await user.send(
                            f"提醒你！**{project_name}** 在過去 {check_interval_days} 天內沒有新 commit，快去寫程式吧！"
                        )
                    except discord.Forbidden:
                        # 使用者關閉私訊，跳過不報錯
                        pass

    @daily_check.before_loop
    async def before_daily_check(self):
        await self.bot.wait_until_ready()  # 確保bot完全啟動後才開始定時任務

async def setup(bot):
    await bot.add_cog(GitHub(bot))