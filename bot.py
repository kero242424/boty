import os
import discord
from discord.ext import commands
from groq import Groq
import sqlite3
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Discord Bot Kurulumu
intents = discord.Intents.default()
intents.message_content = True  # KESİNLİKLE AÇIK OLMALI
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Groq İstemcisi
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
executor = ThreadPoolExecutor(max_workers=10)

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

def groq_istek_gonder(mesaj_icerigi):
    system_prompt = (
        "Sen mutlak bir totaliter rejim gözetmenisin. Sana gelen her mesajı analiz et. "
        "Eğer mesajda en ufak bir hakaret, kaba dil, otoriteye karşı çıkış, küfür veya iğneleme varsa "
        "SADECE 'EVET' yanıtını ver. Eğer mesaj tamamen zararsız ve itaatkar ise 'HAYIR' yanıtını ver. "
        "Sadece tek kelime ile yanıtla: EVET veya HAYIR."
    )
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mesaj_icerigi}
            ],
            model="llama3-8b-8192",
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"API Hatası: {e}")
        return "HAYIR"

async def derin_analiz(mesaj_icerigi):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, groq_istek_gonder, mesaj_icerigi)

@bot.event
async def on_ready():
    veritabanı_hazırla()
    print(f"--- SİSTEM AKTİF: {bot.user.name} ---")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Kendi kendine komutları çalıştırmasın
    if message.content.startswith('!'):
        await bot.process_commands(message)
        return

    # Analiz süreci
    karar = await derin_analiz(message.content)
    print(f"DEBUG: '{message.content}' -> Karar: {karar}")
    
    if karar == "EVET":
        ihlal_sayisi = sicil_guncelle(message.author.id, message.author.name)
        
        # İmha
        try:
            await message.delete()
        except discord.Forbidden:
            print("HATA: Mesajı silme yetkim yok!")
        
        # DM Uyarı
        try:
            await message.author.send(f"⚠️ İhlal tespit edildi. Siciliniz: {ihlal_sayisi}. Sadakat, özgürlüktür.")
        except:
            pass

        # Loglama
        log_channel = discord.utils.get(message.guild.text_channels, name="ihlaller")
        if log_channel:
            embed = discord.Embed(title="🚨 İHLAL RAPORU", color=0xFF0000)
            embed.add_field(name="Üye", value=message.author.name, inline=True)
            embed.add_field(name="İhlal Sayısı", value=str(ihlal_sayisi), inline=True)
            embed.add_field(name="İmha Edilen Mesaj", value=message.content, inline=False)
            await log_channel.send(embed=embed)

    await bot.process_commands(message)

bot.run(os.getenv('DISCORD_TOKEN'))
