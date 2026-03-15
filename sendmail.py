import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True  # 建議開啟，以便找尋成員
bot = commands.Bot(command_prefix="%", intents=intents)

MY_GUILD_ID = 1477288273767301170




@bot.event
async def on_ready():
    guild = discord.Object(id=MY_GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print("Bot is ready.")

@bot.command
async def send_message():
    
    




bot.run(TOKEN)