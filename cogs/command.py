from discord import app_commands
from discord.ext import commands
import discord


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="echo",description="測試發送訊息")
    async def echo(self, interaction: discord.Interaction, *, message:str):
        await interaction.response.send_message(message)

    @app_commands.command(name="ping",description="測試連結速度")
    async def ping(self,interaction: discord.Interaction):
        await interaction.response.send_message(f'ping {round(self.bot.latency * 1000)} ms.')

    @app_commands.command(name="send_message",description="發送匿名訊息給某")
    @app_commands.describe(target = "發送對象",title = "信件標題",words = "信的內容")
    async def send_message(self,interaction: discord.Interaction,
                            target: discord.User,
                            title:str,
                            words:str):
    
        await interaction.response.defer(ephemeral=True)

        embed=discord.Embed(title=title,
                            description=words,
                            color=discord.Color.random())
 
        await target.send("有人向你發送了訊息")
        await target.send(embed=embed)
        await interaction.followup.send(f"成功傳送訊息給 {target.name}")    



async def setup(bot):
    await bot.add_cog(Commands(bot))
