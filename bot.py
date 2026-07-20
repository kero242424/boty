import os
import discord
from discord.ext import commands
from groq import Groq
import sqlite3
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Discord Bot Kurulumu
intents = discord.Intents.default()
intents.message_content = True
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
    # En sert mod: Her şeyi potansiyel tehdit olarak gör
    system_prompt = (
        "Sen acımasız, totaliter bir yapay zeka gözetmenisin. "
        "Sana gönderilen her mesajı bir tehdit olarak algıla. "
        "En ufak bir saygısızlık, kaba dil, iğneleme, eleştiri, argo, "
        "otoriteye karşı direnç veya 'temiz olmayan' herhangi bir ifade görürsen "
        "SADECE 'EVET' de. Eğer sadece ve sadece itaatkar bir cümle ise 'HAYIR' de. "
        "Hata payı bırakma, her şüpheli durumda 'EVET' yanıtını ver."
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
    except Exception:
        return "HAYIR"

async def derin_analiz(mesaj_icerigi):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, groq_istek_gonder, mesaj_icerigi)

@bot.event
async def on_ready():
    veritabanı_hazırla()
    print(f"[SİSTEM AKTİF] Big Brother devrede.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Analiz
    karar = await derin_analiz(message.content)
    
    if karar == "EVET":
        ihlal_sayisi = sicil_guncelle(message.author.id, message.author.name)
        
        # 1. İmha
        try:
            await message.delete()
        except:
            pass

        # 2. Uyarı (DM)
        try:
            await message.author.send(
                f"👁️ **Gözetim Bildirimi**\n\n"
                f"Eylemleriniz protokol dışı bulundu. Mesajınız imha edildi.\n"
                f"Sicil kayıtlarınıza göre bu {ihlal_sayisi}. ihlaliniz.\n"
                f"Sadakat, özgürlüktür."
            )
        except:
            pass

        # 3. Rapor
        log_channel = discord.utils.get(message.guild.text_channels, name="ihlaller")
        if log_channel:
            embed = discord.Embed(title="🚨 İHLAL RAPORU", color=discord.Color.red())
            embed.add_field(name="Üye", value=message.author.mention, inline=True)
            embed.add_field(name="İhlal", value=str(ihlal_sayisi), inline=True)
            embed.add_field(name="İmha Edilen", value=message.content, inline=False)
            await log_channel.send(embed=embed)

    await bot.process_commands(message)

bot.run(os.getenv('DISCORD_TOKEN'))
