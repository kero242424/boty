import discord
from discord.ext import commands
import random

# Token'ı buraya gömdüm, direkt çalıştır.
TOKEN = 'MTUyNzMyMTQxNjA4NzYzODAxNg.GUXMHz.hLeEQn5LI-LtCLrs8Yh5P2H6iKnyMonb5Mqdgc'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

kaos_mesajlari = [
    "Ya beyler aslında ben sizin hakkınızda arkadan konuşulanları biliyorum, keşke bilseniz...",
    "Sunucunun sahibi de bence boş çar, yakında burayı bırakıp kaçacak.",
    "Bence herkes birbirinin açığını arıyor, çok yapmacıksınız.",
    "Adminler sadece kendi egolarını tatmin ediyor, başka yaptıkları bir şey yok.",
    "Birisiyle özelden yazıştım, kim olduğunu söyleyemem ama çok fena şeyler döndü."
]

@bot.event
async def on_ready():
    print(f'🔥 Doppelgänger aktif! {bot.user.name} iş başında.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # %15 ihtimalle kurbanı seç ve kaosu başlat
    if random.random() < 0.15:
        try:
            webhook = await message.channel.create_webhook(name="Kaos")
            await webhook.send(
                content=random.choice(kaos_mesajlari),
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url
            )
            await webhook.delete()
        except Exception as e:
            print(f"Hata: {e}")

    await bot.process_commands(message)

bot.run(TOKEN)
