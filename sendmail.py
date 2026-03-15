import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True  
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

MY_GUILD_ID = 1477288273767301170


@bot.tree.command(name="send_message",description="Send a message to everyone.")
async def send_message(interaction: discord.Interaction,c :str):
    await interaction.response.send_message(c)

@bot.event
async def on_ready():
    guild = discord.Object(id=MY_GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)


    
    




bot.run(TOKEN)