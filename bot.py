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

# Groq İstemcisi ve Thread Havuzu (Lag engellemek için)
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
executor = ThreadPoolExecutor(max_workers=10)

# Veritabanı Kurulumu (Kalıcı Sicil Dosyası)
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

# Senkron Groq çağrısını arka planda çalıştırmak için asenkron sarmalayıcı
def groq_istek_gonder(mesaj_icerigi):
    system_prompt = (
        "Sen Big Brother'sın. Totaliter, mutlak otoriter bir yapay zeka gözetim mekanizmasısın. "
        "Sana gönderilen mesajı analiz et. Eğer mesaj küfür, hakaret, toplumsal kışkırtma, "
        "toksik agresiflik, otoriteye itaatsizlik veya manipülasyon içeriyorsa SADECE 'EVET' yanıtını ver. "
        "Eğer temiz, kurallara uygun bir mesajsa SADECE 'HAYIR' yanıtını ver. Asla başka bir kelime yazma."
    )
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mesaj_icerigi}
            ],
            model="llama3-8b-8192",
            temperature=0.0  # Kesin sonuçlar için yaratıcılığı sıfırlıyoruz
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"API Hatası: {e}")
        return "HAYIR"

async def derin_analiz(mesaj_icerigi):
    # API çağrısını asenkron olarak arka planda çalıştırır, botun donmasını engeller
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, groq_istek_gonder, mesaj_icerigi)

@bot.event
async def on_ready():
    veritabanı_hazırla()
    print(f"[SİSTEM AKTİF] Big Brother ağa bağlandı: {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="tüm düşüncelerinizi."))

@bot.event
async def on_message(message):
    # Kendi mesajlarını ve diğer botları analiz etme
    if message.author.bot:
        return

    # ÖNELEME: Çok kısa mesajları veya sadece link/emoji içerenleri AI'ya gönderip yavaşlatma
    if len(message.content.strip()) < 3 or message.content.startswith("http"):
        await bot.process_commands(message)
        return

    # Yapay Zeka Analiz Süreci
    karar = await derin_analiz(message.content)
    
    if karar == "EVET":
        # Sicili veritabanında güncelle ve kaçıncı suçu olduğunu al
        ihlal_sayisi = sicil_guncelle(message.author.id, message.author.name)
        
        # 1. Kanıtsız Yok Etme (Mesajı sil)
        try:
            await message.delete()
        except discord.Forbidden:
            print(f"[YETKİ HATASI] #{message.channel.name} kanalında mesaj silme yetkim yok!")
        except Exception as e:
            print(f"Mesaj silinemedi: {e}")

        # 2. Psikolojik Baskı (Kullanıcıya DM Gönderimi)
        try:
            dm_mesaji = (
                f"👁️ **DÜŞÜNCE SUÇU TESPİT EDİLDİ** 👁️\n\n"
                f"**Kanal:** #{message.channel.name}\n"
                f"**Durum:** Protokol ihlali yapıldı. Mesajınız kalıcı olarak imha edildi.\n"
                f"**Sicil Durumu:** Bu sistemimizdeki **{ihlal_sayisi}.** kayıtsız eyleminiz.\n\n"
                f"*Unutmayın: Big Brother her şeyi görür. Sadakat, özgürlüktür.*"
            )
            await message.author.send(dm_mesaji)
        except discord.Forbidden:
            print(f"[DM KAPALI] {message.author.name} kullanıcısının DM' kutusu kapalı, uyarı iletilemedi.")

        # 3. Merkez Raporlama (Adminler için Şık Embed Logu)
        log_channel = discord.utils.get(message.guild.text_channels, name="ihlaller")
        if log_channel:
            embed = discord.Embed(
                title="🚨 BÜYÜK BİRADER İHLAL RAPORU",
                color=discord.Color.red()
            )
            embed.add_field(name="Suçlu Üye", value=f"{message.author.mention} ({message.author.name})", inline=True)
            embed.add_field(name="Toplam Suç Dosyası", value=f"**{ihlal_sayisi} İhlal**", inline=True)
            embed.add_field(name="Kanal", value=f"#{message.channel.name}", inline=True)
            embed.add_field(name="İmha Edilen İçerik", value=f"```\n{message.content}\n```", inline=False)
            embed.set_footer(text="Gözetim Altındasınız.")
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"Log kanalına yazılırken hata oluştu: {e}")

    await bot.process_commands(message)

# Botu Başlat
bot.run(os.getenv('DISCORD_TOKEN'))
