import os
import discord
from discord.ext import commands
import sqlite3

# --- AYARLAR ---
BLACKLIST = [
    "amk", "aq", "orospu", "piç", "siktir", "sikerim", "göt", "yavşak", 
    "amına", "ananı", "avradını", "sik", "oç", "kahpe", "yarak", "yarrak", 
    "mal", "aptal", "salak", "gerizekalı", "eşek", "hayvan", "köpek", 
    "ezik", "pezevenk", "gavat", "ibne", "top", "hasiktir",
    "sikiyim", "amcık", "meme", "döl", "dölsüz", "bacını", "sülaleni"
]

# Discord Bot Kurulumu
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Veritabanı
DB_FILE = "big_brother_dossiers.db"

def veritabanı_hazırla():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dossiers (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            infractions INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def sicil_guncelle(user_id, username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO dossiers (user_id, username, infractions) VALUES (?, ?, 0)", (user_id, username))
    cursor.execute("UPDATE dossiers SET infractions = infractions + 1 WHERE user_id = ?", (user_id,))
    cursor.execute("SELECT infractions FROM dossiers WHERE user_id = ?", (user_id,))
    infractions = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return infractions

@bot.event
async def on_ready():
    veritabanı_hazırla()
    print("--- SİSTEM AKTİF: GÖZETİM DEVREDE ---")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Blacklist Kontrolü
    msg_content = message.content.lower()
    if any(word in msg_content for word in BLACKLIST):
        ihlal_sayisi = sicil_guncelle(message.author.id, message.author.name)
        
        # 1. İmha
        try:
            await message.delete()
        except Exception as e:
            print(f"HATA: Mesaj silinemedi -> {e}")

        # 2. Uyarı
        try:
            await message.author.send(f"⚠️ İhlal tespit edildi. Siciliniz: {ihlal_sayisi}. Sadakat, özgürlüktür.")
        except:
            pass

        # 3. Loglama
        log_channel = discord.utils.get(message.guild.text_channels, name="ihlaller")
        if log_channel:
            embed = discord.Embed(title="🚨 İHLAL RAPORU", color=0xFF0000)
            embed.add_field(name="Üye", value=message.author.name, inline=True)
            embed.add_field(name="İhlal Sayısı", value=str(ihlal_sayisi), inline=True)
            embed.add_field(name="İmha Edilen", value=message.content, inline=False)
            await log_channel.send(embed=embed)
        return

    await bot.process_commands(message)

# TOKENİ GÜVENLİĞE ALDIN MI?
token = os.getenv('DISCORD_TOKEN')
if not token:
    print("HATA: DISCORD_TOKEN bulunamadı!")
else:
    bot.run(token)
