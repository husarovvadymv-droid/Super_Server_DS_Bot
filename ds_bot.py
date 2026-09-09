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

@bot.event
async def on_ready():
    print(f'🤖 Бот {bot.user.name} успішно запустився і готовий до роботи!')
    await bot.change_presence(activity=discord.Game(name="Злом бази даних..."))

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="📥 ВИЯВЛЕНО НОВИЙ СИГНАЛ",
            description=f"Об'єкт {member.mention} успішно підключився до мережі.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Сканування особистості", value="Пройдено успішно ✅", inline=True)
        embed.add_field(name="Рівень доступу", value="Гість (Рівень 1)", inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text="Організація «Світ» • База даних оновлена")
        
        await channel.send(embed=embed)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Привіт, {ctx.author.mention}! На зв\'язку Організація «Світ». Протоколи активовано.")

@bot.command()
async def status(ctx, *, target_name: str = None):
    if target_name is None:
        await ctx.send("❓ **Помилка:** Вкажіть ім'я об'єкта. Наприклад: `!status віталій`")
        return

    name_lower = target_name.lower()

    if name_lower == "віталій":
        embed = discord.Embed(
            title="🚨 СИСТЕМНА ТРИВОГА 🚨",
            description="Зафіксовано підозрілу активність у секторі складу!",
            color=discord.Color.red()
        )
        embed.add_field(name="Об'єкт", value="Наглядач Віталій", inline=True)
        embed.add_field(name="Статус", value="Переносить зашифровані архіви", inline=True)
        embed.set_footer(text="Організація «Світ» • Моніторинг безпеки")
        await ctx.send(embed=embed)
        
    elif name_lower in ["адмін", "титан", "вадим"]:
        await ctx.send(f"🔍 Статус об'єкта **{target_name}**: Стабільний. Аномалій не виявлено. Доступ дозволено.")

    elif name_lower in ["sys_admin", "i"]:
        await ctx.send(f"🔍 Статус об'єкта **{target_name}**: Може становити загрозу. Стежити обов'язково.")
        
    else:
        await ctx.send(f"❌ **ПОМИЛКА ДОСТУПУ:** Об'єкт **{target_name}** відсутній у базі даних Організації «Світ».")

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
