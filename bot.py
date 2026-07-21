import os
import sys
import random
import discord
from discord.ext import commands
import requests

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_xp = {}

@bot.event
async def on_ready():
    print(f"Süper Bot devrede: {bot.user}")
    await send_startup_commit_notification()

async def send_startup_commit_notification():
    try:
        channel_id = os.getenv("DISCORD_CHANNEL_ID")
        channel = None

        if channel_id and channel_id.strip():
            try:
                channel = await bot.fetch_channel(int(channel_id))
            except Exception:
                pass

        if not channel:
            for guild in bot.guilds:
                for c in guild.text_channels:
                    if c.permissions_for(guild.me).send_messages:
                        channel = c
                        break
                if channel:
                    break

        if not channel:
            return

        commit_message = os.getenv("GITHUB_COMMIT_MESSAGE")
        if not commit_message:
            return

        commit_author = os.getenv("GITHUB_ACTOR", "Bilinmeyen Yazar")
        repo_name = os.getenv("GITHUB_REPOSITORY", "Bilinmeyen Repo")
        commit_sha_full = os.getenv("GITHUB_SHA", "0000000")
        commit_sha = commit_sha_full[:7] if commit_sha_full else "0000000"
        commit_url = f"https://github.com/{repo_name}/commit/{commit_sha_full}"
        ref_name = os.getenv("GITHUB_REF_NAME", "main")

        embed = discord.Embed(
            title="🚀 Mega GitHub Entegrasyonu Tetiklendi!",
            description="Yeni kod satırları sisteme başarıyla işlendi.",
            color=0x9B59B6,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="📁 Depo", value=f"`{repo_name}`", inline=True)
        embed.add_field(name="🌿 Branch", value=f"`{ref_name}`", inline=True)
        embed.add_field(name="👤 Yazar", value=f"**{commit_author}**", inline=True)
        embed.add_field(name="📝 Commit", value=f">>> {commit_message}", inline=False)
        embed.add_field(name="🔗 Link", value=f"[Commit'e Git]({commit_url})", inline=True)
        embed.set_thumbnail(url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
        embed.set_footer(text="Python Ultra Bot v5.0", icon_url="https://cdn-icons-png.flaticon.com/512/25/25231.png")

        await channel.send(embed=embed)
    except Exception as e:
        print(f"Commit bildirimi hatası: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    yasakli_kelimeler = ["discord.gg/", "mal", "orospu", "fuck"]
    content_lower = message.content.lower()
    if any(word in content_lower for word in yasakli_kelimeler):
        try:
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda bu tarz içeriklerin paylaşılması yasak!", delete_after=5)
            return
        except:
            pass

    author_id = message.author.id
    if author_id not in user_xp:
        user_xp[author_id] = 0
    
    user_xp[author_id] += 10

    await bot.process_commands(message)

# --- KLASİK / ÖNCEKİ ÖZELLİKLER ---

@bot.command(name="havadurumu", help="Belirtilen şehrin anlık hava durumunu gösterir.")
async def havadurumu(ctx, *, sehir: str = "Istanbul"):
    try:
        url = f"https://wttr.in/{sehir}?format=j1"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            await ctx.send("❌ Hava durumu bilgisi alınamadı.")
            return

        data = response.json()
        current = data['current_condition'][0]
        temp = current['temp_C']
        feels = current['FeelsLikeC']
        desc = current['weatherDesc'][0]['value']
        humidity = current['humidity']
        wind = current['windspeedKmph']

        embed = discord.Embed(title=f"🌤️ {sehir.capitalize()} Hava Durumu", color=0x3498DB, timestamp=discord.utils.utcnow())
        embed.add_field(name="🌡️ Sıcaklık", value=f"**{temp}°C** (Hissedilen: {feels}°C)", inline=True)
        embed.add_field(name="☁️ Durum", value=f"**{desc}**", inline=True)
        embed.add_field(name="💧 Nem", value=f"%{humidity}", inline=True)
        embed.add_field(name="💨 Rüzgar", value=f"{wind} km/s", inline=True)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Hata: {e}")

@bot.command(name="seviye", help="Seviye ve XP gösterir.")
async def seviye(ctx, member: discord.Member = None):
    target = member or ctx.author
    xp = user_xp.get(target.id, 0)
    level = xp // 100
    embed = discord.Embed(title=f"📊 {target.name} - Seviye Kartı", color=0xE74C3C)
    embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
    embed.add_field(name="⭐ Toplam XP", value=f"{xp} XP", inline=True)
    embed.add_field(name="🏆 Seviye", value=f"Level {level}", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="anket", help="Anket açar.")
async def anket(ctx, *, soru: str):
    await ctx.message.delete()
    embed = discord.Embed(title="📊 Sunucu Anketi", description=f"**{soru}**", color=0xF1C40F, timestamp=discord.utils.utcnow())
    embed.set_footer(text=f"Başlatan: {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    poll_msg = await ctx.send(embed=embed)
    await poll_msg.add_reaction("👍")
    await poll_msg.add_reaction("👎")
    await poll_msg.add_reaction("🤔")

@bot.command(name="borsa", help="Kripto para piyasa verisi çeker.")
async def borsa(ctx, *, coin: str = "bitcoin"):
    try:
        coin_id = coin.lower().strip()
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,try&include_24hr_change=true"
        res = requests.get(url, timeout=5).json()
        if coin_id not in res:
            await ctx.send(f"❌ '{coin}' bulunamadı!")
            return
        price_usd = res[coin_id]['usd']
        price_try = res[coin_id]['try']
        change_24h = res[coin_id].get('usd_24h_change', 0)
        renk = 0x2ECC71 if change_24h >= 0 else 0xE74C3C
        yon = "📈" if change_24h >= 0 else "📉"
        embed = discord.Embed(title=f"{yon} {coin.upper()} Canlı Piyasa", color=renk, timestamp=discord.utils.utcnow())
        embed.add_field(name="💵 USD", value=f"**${price_usd:,.2f}**", inline=True)
        embed.add_field(name="₺ TRY", value=f"**₺{price_try:,.2f}**", inline=True)
        embed.add_field(name="📊 24s Değişim", value=f"%{change_24h:.2f}", inline=True)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Hata: {e}")

@bot.command(name="itiraf", help="Anonim itiraf gönderir.")
async def itiraf(ctx, *, mesaj: str):
    await ctx.message.delete()
    embed = discord.Embed(title="🥷 Gizli İtiraf Kutusu", description=f">>> {mesaj}", color=0x2C3E50, timestamp=discord.utils.utcnow())
    embed.set_footer(text="Bu mesaj tamamen anonimdir.")
    await ctx.send(embed=embed)


# --- YENİ EKLENEN 10 ÇILGIN ÖZELLİK ---

@bot.command(name="rastgelekedi", help="Dünyanın en tatlı rastgele kedi fotoğrafını getirir.")
async def rastgelekedi(ctx):
    try:
        res = requests.get("https://api.thecatapi.com/v1/images/search", timeout=5).json()
        image_url = res[0]['url']
        embed = discord.Embed(title="🐱 Rastgele Kedi Kutusu", color=0xFF69B4, timestamp=discord.utils.utcnow())
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Kedi getirilemedi: {e}")

@bot.command(name="rastgelekopek", help="Rastgele sevimli bir köpek fotoğrafı fırlatır.")
async def rastgelekopek(ctx):
    try:
        res = requests.get("https://dog.ceo/api/breeds/image/random", timeout=5).json()
        image_url = res['message']
        embed = discord.Embed(title="🐶 Rastgele Köpek Kutusu", color=0xD35400, timestamp=discord.utils.utcnow())
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Köpek getirilemedi: {e}")

@bot.command(name="fakeprofil", help="Testler için tamamen rastgele sahte bir kimlik üretir.")
async def fakeprofil(ctx):
    try:
        res = requests.get("https://randomuser.me/api/", timeout=5).json()['results'][0]
        ad = f"{res['name']['first']} {res['name']['last']}"
        ulke = res['location']['country']
        email = res['email']
        resim = res['picture']['large']
        
        embed = discord.Embed(title=f"🕵️ Sahte Kimlik Üreticisi: {ad}", color=0x8E44AD)
        embed.set_thumbnail(url=resim)
        embed.add_field(name="🌍 Ülke", value=ulke, inline=True)
        embed.add_field(name="📧 E-Posta", value=email, inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Kimlik üretilemedi: {e}")

@bot.command(name="soz", help="Derin ve fiyakalı felsefi/mühendislik sözleri patlatır.")
async def soz(ctx):
    sozler = [
        "Kod yazmak şiir yazmak gibidir, ilk başta harika görünür ama sonra hatalarla boğuşursun.",
        "Önce problemi çöz, sonra kodunu yaz. - John Johnson",
        "İşini düzgün yapıyorsan kimse fark etmez, ama hata yaparsan ilk seni ararlar.",
        "Erken optimizasyon bütün kötülüklerin köküdür. - Donald Knuth",
        "Çalışıyorsa sakın dokunma!",
        "Kahve girer, kod çıkar."
    ]
    secilen = random.choice(sozler)
    embed = discord.Embed(title="💡 Günün Felsefi Sözü", description=f">>> *{secilen}*", color=0x1ABC9C)
    await ctx.send(embed=embed)

@bot.command(name="yazitura", help="Yazı mı Tura mı? Kaderini belirle.")
async def yazitura(ctx):
    sonuc = random.choice(["Yazı 🦅", "Tura 🪙"])
    embed = discord.Embed(title="🎲 Para Atıldı!", description=f"Sonuç: **{sonuc}**", color=0xF39C12)
    await ctx.send(embed=embed)

@bot.command(name="zar", help="1 ile 6 arasında rastgele zar atar.")
async def zar(ctx):
    atilan = random.randint(1, 6)
    embed = discord.Embed(title="🎲 Zar Atma Simülasyonu", description=f"Gelen Zar: **{atilan}** 🎯", color=0xE67E22)
    await ctx.send(embed=embed)

@bot.command(name="sifre", help="Güvenli ve kırılması imkansız rastgele şifre üretir.")
async def sifre(ctx, uzunluk: int = 12):
    if uzunluk < 6 or uzunluk > 32:
        uzunluk = 12
    karakterler = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    sifre_str = "".join(random.choice(karakterler) for _ in range(uzunluk))
    
    embed = discord.Embed(title="🔒 Güvenli Şifre Üreticisi", description=f"Oluşturulan Şifre:\n`{sifre_str}`", color=0x27AE60)
    embed.set_footer(text=f"Uzunluk: {uzunluk} karakter")
    await ctx.send(embed=embed)

@bot.command(name="espri", help="Yüzünü güldürecek (veya sinir edecek) rastgele bir espri patlatır.")
async def espri(ctx):
    espriler = [
        "Geçen gün taksi çevirdim, hâlâ dönüyor.",
        "Adamın biri gülmüş, karısı lavabo.",
        "Temel, tren rayına yatmış; 'Acaba 5 vagon mu, 6 vagon mu geçecek' diye sayıyormuş.",
        "İdrarlı sokakları kim yapar? Tabii ki Tuvaletçi Amca!",
        "Karanlıkta aydınlık, aydınlıkta karanlık olan şey nedir? Elektrik kesintisi!"
    ]
    secilen = random.choice(espriler)
    embed = discord.Embed(title="🎭 Botun Komiklik Kutusu", description=secilen, color=0xE91E63)
    await ctx.send(embed=embed)

@bot.command(name="hesapla", help="Matematiksel işlemleri senin için hesaplar. Örn: !hesapla 50 * 42")
async def hesapla(ctx, *, ifade: str):
    try:
        # Güvenlik amaçlı sadece temel matematik karakterlerine izin veriyoruz
        guvenli_karakterler = set("0123456789+-*/(). ")
        if not all(c in guvenli_karakterler for c in ifade):
            await ctx.send("❌ Sadece temel matematik işlemleri (+, -, *, /) yapabilirsin!")
            return
        
        sonuc = eval(ifade)
        embed = discord.Embed(title="🧮 Hesap Makinesi", color=0x34495E)
        embed.add_field(name="İşlem", value=f"`{ifade}`", inline=False)
        embed.add_field(name="Sonuç", value=f"**{sonuc}**", inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Hesaplama hatası: İşlemi doğru yazdığından emin ol.")

@bot.command(name="terscevir", help="Yazdığın metni tamamen tersten yazar.")
async def terscevir(ctx, *, metin: str):
    ters_metin = metin[::-1]
    embed = discord.Embed(title="🔄 Metin Çevirici", description=f">>> {ters_metin}", color=0x95A5A6)
    await ctx.send(embed=embed)

@bot.command(name="ping", help="Gecikme süresini ölçer.")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Roket hızında çalışıyoruz! 🚀 Gecikme: **{latency}ms**")

token = os.getenv("DISCORD_TOKEN")
if not token:
    print("Hata: Token bulunamadı!")
    sys.exit(1)

bot.run(token)
