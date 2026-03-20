import discord,os,time
from discord.ext import commands
from dotenv import load_dotenv

MY_GUILD_ID = 1477288273767301170
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.default()
intents.members = True  
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents,description="Summerain的逼你工作多功能機器人")



@bot.command()
async def reload(ctx, extension):
    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"ReLoaded {extension} done.")
        
@bot.command()
async def on_command_error(ctx,error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("發生錯誤。")
        await ctx.send(error)
    
@bot.event
async def on_ready():
    try:
        for cog in os.listdir('./cogs'):
            if cog.endswith('.py'):
                await bot.load_extension(f'cogs.{cog[:-3]}')
        print("Cog loaded.")
    except Exception as e:
        print(f"Failed to load cog my_cog: {e}")
    
    guild = discord.Object(id=MY_GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)

    
    
bot.run(TOKEN)