import discord
from discord.ext import commands, tasks
import random
import asyncio
import os
from mcstatus import JavaServer
from keep_alive import keep_alive

keep_alive()

TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True         
bot = commands.Bot(command_prefix='!', intents=intents)

SERVER_IP = "listing-dans.gl.joinmc.link"
SERVER_VERSION = "1.21.10"
WELCOME_CHANNEL_ID = int(os.environ.get('WELCOME_CHANNEL_ID', 1527321504096981084))

SECRET_LOGS = [
    "📡 [СИГНАЛ]: Зафіксовано запуск архівування `.tar.gz`.",
    "⚠️ [ПОПЕРЕДЖЕННЯ]: Об'єкт Віталій помічений біля сектору B.",
    "🔧 [СИСТЕМА]: Плагін `CustomRecipes` успішно синхронізовано з ядром 1.21.10.",
    "🔒 [БЕЗПЕКА]: Спроба несанкціонованого доступу відхилена."
]

def get_status_data():
    try:
        server = JavaServer.lookup(SERVER_IP)
        status = server.status()
        players = status.players.sample
        names = [p.name for p in players] if players else []
        return status.players.online, status.players.max, names, True
    except Exception:
        return 0, 0, [], False

@tasks.loop(seconds=60)
async def update_presence():
    online, max_p, _, is_online = get_status_data()
    if is_online:
        await bot.change_presence(activity=discord.Game(name=f"Онлайн: {online}/{max_p} 🎮"))
    else:
        await bot.change_presence(activity=discord.Game(name="Сервер OFFLINE 🔴"))

@bot.event
async def on_ready():
    print(f'🤖 Бот {bot.user.name} успішно запустився!')
    update_presence.start()

@bot.command()
async def online(ctx):
    online_count, max_players, names, is_online = get_status_data()
    
    if not is_online:
        embed = discord.Embed(
            title="🔴 СЕРВЕР ОФЛАЙН",
            description="Організація «Світ» не може встановити зв'язок із ядром.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    players_str = "\n".join([f"• `{name}`" for name in names]) if names else "_Немає гравців у мережі_"
    
    embed = discord.Embed(
        title="📡 Моніторинг активності мережі",
        color=discord.Color.blue()
    )
    embed.add_field(name="Статус", value="🟢 ONLINE", inline=True)
    embed.add_field(name="Гравці", value=f"`{online_count}/{max_players}`", inline=True)
    embed.add_field(name="Активні агенти", value=players_str, inline=False)
    embed.set_footer(text="Організація «Світ» • Моніторинг в реальному часі")
    
    await ctx.send(embed=embed)

@bot.command()
async def ip(ctx):
    embed = discord.Embed(
        title="🔌 Підключення до сервера",
        description=f"📍 **IP:** `{SERVER_IP}`\n⚙️ **Версія:** `{SERVER_VERSION}`",
        color=discord.Color.green()
    )
    msg = await ctx.send(embed=embed)
    await asyncio.sleep(30)
    try:
        await msg.delete()
        await ctx.message.delete()
    except discord.Forbidden:
        pass  

@bot.command()
async def logs(ctx):
    log = random.choice(SECRET_LOGS)
    await ctx.send(f"💾 **[Термінал Організації «Світ»]:** {log}")

bot.run(TOKEN)
