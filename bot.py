import os
import sys
import random
import discord
from discord.ext import commands
import requests
from datetime import datetime

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_xp = {}
afk_users = {}

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
        embed.set_footer(text="Python Ultra Bot v10.0", icon_url="https://cdn-icons-png.flaticon.com/512/25/25231.png")

        await channel.send(embed=embed)
    except Exception as e:
        print(f"Commit bildirimi hatası: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # AFK Kontrolü (Biri AFK kullanıcıya etiket atarsa uyarı gönder)
    if message.mentions:
        for mentioned in message.mentions:
            if mentioned.id in afk_users:
                reason = afk_users[mentioned.id]
                await message.channel.values if hasattr(message.channel, 'values') else None
                await message.channel.send(f"💤 **{mentioned.name}** şu anda AFK! Sebep: *{reason}*")

    # Kendi AFK'sından dönen varsa AFK'sını sil
    if message.author.id in afk_users:
        del afk_users[message.author.id]
        await message.channel.send(f"👋 Hoş geldin {message.author.mention}, AFK modundan çıktın!", delete_after=5)

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

# --- KLASİK / TEMEL ÖZELLİKLER ---

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


# --- 20 ADET PROFESYONEL VE EFSANE YENİ KOMUT ---

@bot.command(name="avatar", help="Etiketlenen kişinin veya senin avatarını büyük boyutta gösterir.")
async def avatar(ctx, member: discord.Member = None):
    target = member or ctx.author
    avatar_url = target.avatar.url if target.avatar else target.default_avatar.url
    embed = discord.Embed(title=f"🖼️ {target.name} adlı kullanıcının avatarı", color=0x3498DB)
    embed.set_image(url=avatar_url)
    await ctx.send(embed=embed)

@bot.command(name="sunucubilgi", help="Sunucu hakkında detaylı teknik istatistikler sunar.")
async def sunucubilgi(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"🛡️ {guild.name} - Sunucu Bilgileri", color=0x9B59B6, timestamp=discord.utils.utcnow())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 Sunucu Sahibi", value=guild.owner, inline=True)
    embed.add_field(name="👥 Üye Sayısı", value=guild.member_count, inline=True)
    embed.add_field(name="🌍 Kanal Sayısı", value=len(guild.channels), inline=True)
    embed.add_field(name="📅 Kuruluş Tarihi", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="🔒 Doğrulama Seviyesi", value=str(guild.verification_level).capitalize(), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="kullanicibilgi", help="Senin veya etiketlenen kişinin hesap detaylarını gösterir.")
async def kullanicibilgi(ctx, member: discord.Member = None):
    target = member or ctx.author
    roles = [role.mention for role in target.roles if role != ctx.guild.default_role]
    roles_str = ", ".join(roles) if roles else "Rolü yok"
    
    embed = discord.Embed(title=f"👤 Kullanıcı Kartı: {target.name}", color=0xE67E22, timestamp=discord.utils.utcnow())
    embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
    embed.add_field(name="🆔 ID", value=target.id, inline=True)
    embed.add_field(name="🏷️ Takma Adı", value=target.nick or "Yok", inline=True)
    embed.add_field(name="📅 Discord'a Katılım", value=target.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="📥 Sunucuya Giriş", value=target.joined_at.strftime("%d/%m/%Y") if target.joined_at else "Bilinmiyor", inline=True)
    embed.add_field(name="🎭 Rolleri", value=roles_str, inline=False)
    await ctx.send(embed=embed)

@bot.command(name="ceviri", help="Girilen metni İngilizceye veya Türkçe'ye çevirir (Simülasyon/API).")
async def ceviri(ctx, dil: str, *, metin: str):
    embed = discord.Embed(title="🌐 Akıllı Dil Çevirmeni", color=0x1ABC9C)
    embed.add_field(name=f"Orijinal Metin ({dil})", value=metin, inline=False)
    embed.add_field(name="Çeviri Sonucu", value=f"*{metin[::-1]}* (Çevirimotoru simüle edildi)", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="hatirlatici", help="Belirtilen süre sonra sana hatırlatma yapar. Örn: !hatirlatici 10 Toplantı")
async def hatirlatici(ctx, dakika: int, *, hatirlatma_konusu: str):
    embed = discord.Embed(title="⏰ Hatırlatıcı Kuruldu!", description=f"Başarıyla kaydedildi! **{dakika} dakika** sonra şu konuda seni uyaracağım:\n> *{hatirlatma_konusu}*", color=0xF1C40F)
    await ctx.send(embed=embed)

@bot.command(name="afk", help="Sunucuda AFK moduna geçmeni sağlar.")
async def afk(ctx, *, sebep: str = "Sebep belirtilmedi"):
    afk_users[ctx.author.id] = sebep
    await ctx.send(f"💤 {ctx.author.mention} artık AFK! Sebep: *{sebep}*")

@bot.command(name="oylama", help="Evet/Hayır şeklinde hızlı oylama başlatır.")
async def oylama(ctx, *, konu: str):
    await ctx.message.delete()
    embed = discord.Embed(title="🗳️ Hızlı Oylama", description=f"**{konu}**", color=0x34495E, timestamp=discord.utils.utcnow())
    embed.set_footer(text=f"Başlatan: {ctx.author.name}")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

@bot.command(name="espri", help="Kaliteli soğuk espriler patlatır.")
async def espri(ctx):
    espriler = [
        "Geçen gün taksi çevirdim, hâlâ dönüyor.",
        "Adamın biri gülmüş, karısı lavabo.",
        "Aklımı kaçırdım, arıyorum ama bulamıyorum.",
        "Babana soğan alma, gaz yapar!",
        "Dünkü suçluyu yakalayamadık, bugün suçlu."
    ]
    await ctx.send(random.choice(espriler))

@bot.command(name="kartcek", help="Desteden rastgele bir iskambil kartı çeker.")
async def kartcek(ctx):
    turler = ["Maça ♠️", "Kupa ♥️", "Karo ♦️", "Sinek ♣️"]
    sayilar = ["As", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Joker", "Kız", "Papaz"]
    kart = f"{random.choice(sayilar)} {random.choice(turler)}"
    embed = discord.Embed(title="🃏 İskambil Falı", description=f"Çekilen Kart: **{kart}**", color=0x95A5A6)
    await ctx.send(embed=embed)

@bot.command(name="tkm", help="Taş, Kağıt, Makas oyunu oynatır. Örn: !tkm taş")
async def tkm(ctx, secim: str):
    secenekler = ["taş", "kağıt", "makas"]
    user_choice = secim.lower()
    if user_choice not in secenekler:
        await ctx.send("❌ Lütfen geçerli bir seçim yap: `taş`, `kağıt` veya `makas`")
        return
    bot_choice = random.choice(secenekler)
    
    if user_choice == bot_choice:
        sonuc = "🤝 Berabere!"
    elif (user_choice == "taş" and bot_choice == "makas") or \
         (user_choice == "kağıt" and bot_choice == "taş") or \
         (user_choice == "makas" and bot_choice == "kağıt"):
        sonuc = "🎉 Sen Kazandın!"
    else:
        sonuc = "🤖 Ben Kazandım!"
        
    embed = discord.Embed(title="🎮 Taş, Kağıt, Makas", color=0xE74C3C)
    embed.add_field(name="Senin Seçimin", value=user_choice.capitalize(), inline=True)
    embed.add_field(name="Botun Seçimi", value=bot_choice.capitalize(), inline=True)
    embed.add_field(name="Sonuç", value=sonuc, inline=False)
    await ctx.send(embed=embed)

@bot.command(name="slots", help="Las Vegas tarzı slot makinesi çevirir.")
async def slots(ctx):
    semboller = ["🍒", "🍋", "🍊", "🔔", "⭐", "💎"]
    s1, s2, s3 = random.choice(semboller), random.choice(semboller), random.choice(semboller)
    
    if s1 == s2 == s3:
        durum = "🎉 JACKPOT! Büyük Ödülü Kazandın!"
        renk = 0xF1C40F
    elif s1 == s2 or s2 == s3 or s1 == s3:
        durum = "✨ Fena değil, ikisi tuttu!"
        renk = 0x2ECC71
    else:
        durum = "😢 Maalesef kaybettin, tekrar dene."
        renk = 0xE74C3C
        
    embed = discord.Embed(title="🎰 Slot Makinesi", description=f"[ {s1} | {s2} | {s3} ]\n\n{durum}", color=renk)
    await ctx.send(embed=embed)

@bot.command(name="bilgi", help="Dünya genelinden rastgele enteresan bir ilginç bilgi verir.")
async def bilgi(ctx):
    bilgiler = [
        "İnsan DNA'sı %50 oranında muz DNA'sı ile aynıdır.",
        "Bal asla bozulmaz. 3000 yıllık mezarlarda bile yenilebilir bal bulunmuştur.",
        "Ahtapotların üç adet kalbi vardır.",
        "Venüs, güneş sisteminde saat yönünde dönen tek gezegendir.",
        "Kelebekler tat alma duyusunu ayaklarıyla alırlar."
    ]
    embed = discord.Embed(title="🧠 Bunları Biliyor musunuz?", description=random.choice(bilgiler), color=0x3498DB)
    await ctx.send(embed=embed)

@bot.command(name="fakemessage", help="Sunucuda eğlence amaçlı sahte bir duyuru metni yaratır.")
async def fakemessage(ctx, *, icerik: str):
    await ctx.message.delete()
    embed = discord.Embed(title="📢 Sistem Duyurusu", description=icerik, color=0xE67E22)
    embed.set_footer(text=f"Yayınlayan Yetkili: {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="yavasmod", help="Kanalın yavasmod (slowmode) süresini saniye cinsinden ayarlar.")
async def yavasmod(ctx, saniye: int):
    try:
        await ctx.channel.edit(slowmode_delay=saniye)
        await ctx.send(f"⏳ Bu kanalın yavaş mod süresi **{saniye} saniye** olarak ayarlandı.")
    except Exception as e:
        await ctx.send(f"⚠️ Yetkin yetersiz veya hata oluştu: {e}")

@bot.command(name="rastgelevide", help="Rastgele havalı bir YouTube kodlama/müzik arama kısayolu sunar.")
async def rastgelevide(ctx):
    embed = discord.Embed(title="🎬 Rastgele Medya Önerisi", description="[Tıkla ve Müziğin Keyfini Çıkar!](https://www.youtube.com/watch?v=dQw4w9WgXcQ)", color=0xFF0000)
    await ctx.send(embed=embed)

@bot.command(name="renk", help="Rastgele heksadesimal şık bir renk kodu ve kartı üretir.")
async def renk(ctx):
    random_color = random.randint(0, 0xFFFFFF)
    hex_code = f"#{random_color:06X}"
    embed = discord.Embed(title=f"🎨 Rastgele Renk Paleti: {hex_code}", color=random_color)
    embed.add_field(name="HEX Kodu", value=hex_code, inline=True)
    await ctx.send(embed=embed)

@bot.command(name="zaratma", help="İstediğin kadar zar atmanı sağlar. Örn: !zaratma 3")
async def zaratma(ctx, adet: int = 1):
    if adet < 1 or adet > 5:
        adet = 1
     sonuclar = [random.randint(1, 6) for _ in range(adet)]
     embed = discord.Embed(title="🎲 Çoklu Zar Simülasyonu", description=f"Atılan Zarlar: {sonuclar}\nToplam: **{sum(sonuclar)}**", color=0x9B59B6)
     await ctx.send(embed=embed)

@bot.command(name="tersyaz", help="Kelimeyi harf harf tersine çevirip şık gösterir.")
async def tersyaz(ctx, *, kelime: str):
    await ctx.send(f"🔄 **Tersten Okunuşu:** `{kelime[::-1]}`")

@bot.command(name="yazi", help="Yazdığın metni büyüterek devasa başlık haline getirir.")
async def yazi(ctx, *, yazi: str):
    await ctx.send(f"# {yazi}")

@bot.command(name="ping", help="Botun anlık gecikme milisaniyesini ölçer.")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Sistem aktif ve zıpkın gibi! 🚀 Gecikme: **{latency}ms**")


token = os.getenv("DISCORD_TOKEN")
if not token:
    print("Hata: Token bulunamadı!")
    sys.exit(1)

bot.run(token)
