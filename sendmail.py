import discord,os,time
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True  
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

MY_GUILD_ID = 1477288273767301170


@bot.tree.command(name="send_message",description="發送匿名訊息給某")
@app_commands.describe(target = "發送對象", sec = "等待幾秒",title = "信件標題",words = "信的內容")
async def send_message(interaction: discord.Interaction,
                       target: discord.User,
                       sec:int,
                       title:str,
                       words:str):
    
    await interaction.response.defer(ephemeral=True)

    embed=discord.Embed(title=title,
                         description=words,
                         color=discord.Color.random())
    time.sleep(sec)
    await target.send("有人向你發送了訊息")
    await target.send(embed=embed)
    await interaction.followup.send(f"成功傳送訊息給 {target.name}")

        
    
    
@bot.event
async def on_ready():
    guild = discord.Object(id=MY_GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)


    
    
bot.run(TOKEN)