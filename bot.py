import os
import sys
import random
import discord
from discord.ext import commands
import requests
from datetime import datetime, timedelta
import asyncio

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_xp = {}
afk_users = {}
user_bakiye = {}
sopa_cezalilar = {}

def sayi_coumle(deger_str: str) -> int:
    deger_str = deger_str.lower().strip()
    carpici = 1
    if deger_str.endswith('k'):
        carpici = 1_000
        deger_str = deger_str[:-1]
    elif deger_str.endswith('m'):
        carpici = 1_000_000
        deger_str = deger_str[:-1]
    elif deger_str.endswith('b'):
        carpici = 1_000_000_000
        deger_str = deger_str[:-1]
        
    try:
        return int(float(deger_str) * carpici)
    except ValueError:
        return 0

@bot.event
async def on_ready():
    print(f"Mega Ultra Bot devrede: {bot.user}")
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
        embed.set_footer(text="Python Ultra Bot v54.0 Kaos Edition", icon_url="https://cdn-icons-png.flaticon.com/512/25/25231.png")

        await channel.send(embed=embed)
    except Exception as e:
        print(f"Commit bildirimi hatası: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    author_id = message.author.id

    if author_id in sopa_cezalilar:
        bitis_zamani = sopa_cezalilar[author_id]
        if datetime.now() < bitis_zamani:
            try:
                await message.delete()
                bozuk_metin = message.content[::-1] + " 🥴 [Sopa Yedim Sistemim Bozuldu]"
                await message.channel.send(f"🔨 {message.author.mention} sopa yediği için kelimeleri birbirine girdi: {bozuk_metin}")
            except:
                pass
            return
        else:
            del sopa_cezalilar[author_id]

    if message.mentions:
        for mentioned in message.mentions:
            if mentioned.id in afk_users:
                reason = afk_users[mentioned.id]
                await message.channel.send(f"💤 **{mentioned.name}** şu anda AFK! Sebep: *{reason}*")

    if author_id in afk_users:
        del afk_users[author_id]
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

    if author_id not in user_xp:
        user_xp[author_id] = 0
    
    user_xp[author_id] += 10

    await bot.process_commands(message)


# --- YERE PARA DÜŞME & KAPIŞMA MEKANİZMASI ---

class ParaKapmaButonu(discord.ui.View):
    def __init__(self, miktar):
        super().__init__(timeout=None)
        self.miktar = miktar
        self.tiklandi = False

    @discord.ui.button(label="💵 PARAYI KAP", style=discord.ButtonStyle.green, custom_id="para_kap_buton")
    async def parayi_kap(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.tiklandi:
            await interaction.response.send_message("❌ Geç kaldın koçum, parayı çoktan başkası kaptı bile!", ephemeral=True)
            return
        
        self.tiklandi = True
        kazanan = interaction.user
        
        user_bakiye[kazanan.id] = user_bakiye.get(kazanan.id, 1000) + self.miktar
        
        button.disabled = True
        button.label = f"KAPILDI: {kazanan.name}"
        button.style = discord.ButtonStyle.grey
        
        embed = interaction.message.embeds[0]
        embed.color = 0x95A5A6
        embed.title = "💵 YERDEKİ PARA KAPILDI!"
        embed.description = f"⚡ Yerdeki parayı gören **{kazanan.mention}** ortama mermi gibi dalıp **{self.miktar:,} Coin**'i cebine indirdi!"
        
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"🎉 Helal olsun {kazanan.mention}! Yerden kaldırdığın para cüzdanına eklendi: **+{self.miktar:,} Coin**!")


async def kaybi_oyunlara_dusur(guild, miktar, kaybeden):
    if miktar <= 0:
        return
    
    oyunlar_kanali = discord.utils.get(guild.text_channels, name="oyunlar")
    if not oyunlar_kanali:
        return

    embed = discord.Embed(
        title="💸 YERE PARA SAÇILDI!",
        description=f"🚨 **{kaybeden.name}** kumarda fena battı ve yere **{miktar:,} Coin** saçtı!\nAşağıdaki **PARAYI KAP** butonuna **ilk tıklayan** parayı anında kapar. Görelim kim hızlı!",
        color=0x2ECC71,
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"Batıran: {kaybeden.name}", icon_url=kaybeden.avatar.url if kaybeden.avatar else None)
    
    view = ParaKapmaButonu(miktar)
    await oyunlar_kanali.send(embed=embed, view=view)


# --- KUMARHANE & EKONOMİ SİSTEMİ ---

@bot.command(name="bakiye", help="Cüzdanındaki parayı gösterir.")
async def bakiye(ctx, member: discord.Member = None):
    target = member or ctx.author
    para = user_bakiye.get(target.id, 1000)
    user_bakiye[target.id] = para
    embed = discord.Embed(title=f"💰 {target.name} - Cüzdan", description=f"Güncel Bakiye: **{para:,} Coin**", color=0xF1C40F)
    await ctx.send(embed=embed)

@bot.command(name="gunluk", help="Her gün 500 coin toplarsın.")
async def gunluk(ctx):
    author_id = ctx.author.id
    para = user_bakiye.get(author_id, 1000)
    para += 500
    user_bakiye[author_id] = para
    await ctx.send(f"🎁 {ctx.author.mention} Günlük bonusunu aldın! Cüzdana **+500 Coin** eklendi.")

@bot.command(name="paraekle", help="Belirtilen kullanıcıya para ekler (Örn: !paraekle @user 1m).")
async def paraekle(ctx, member: discord.Member, miktar_str: str):
    miktar = sayi_coumle(miktar_str)
    if miktar <= 0:
        await ctx.send("❌ Geçersiz miktar! Örn: `100`, `50k`, `1m` gibi yazmalısın.")
        return

    author_id = member.id
    mevcut = user_bakiye.get(author_id, 1000)
    yeni_bakiye = mevcut + miktar
    user_bakiye[author_id] = yeni_bakiye
    await ctx.send(f"💸 {member.mention} hesabına **{miktar:,} Coin** eklendi! Yeni bakiye: **{yeni_bakiye:,} Coin**")

@bot.command(name="slots", help="Animasyonlu slot makinesi (Örn: !slots 50k).")
async def slots(ctx, miktar_str: str = "100"):
    miktar = sayi_coumle(miktar_str)
    author_id = ctx.author.id
    bakiye_miktari = user_bakiye.get(author_id, 1000)

    if miktar <= 0 or bakiye_miktari < miktar:
        await ctx.send("❌ Yetersiz bakiye veya geçersiz miktar!")
        return

    user_bakiye[author_id] -= miktar
    msg = await ctx.send("🎰 **Slot Makinesi Çevriliyor...**\n[ 🔄 | 🔄 | 🔄 ]")
    await asyncio.sleep(1)
    
    sym = ["🍒", "🍋", "⭐", "🔔", "💎"]
    s = [random.choice(sym) for _ in range(3)]
    
    kazanc = 0
    if s[0] == s[1] == s[2]:
        kazanc = miktar * 5
        sonuc = f"🎉 **JACKPOT!** {kazanc:,} Coin kazandın!"
    elif s[0] == s[1] or s[1] == s[2] or s[0] == s[2]:
        kazanc = int(miktar * 1.5)
        sonuc = f"✨ **Tebrikler!** {kazanc:,} Coin kazandın!"
    else:
        sonuc = f"💸 **Kaybettin!** Kaybettiğin **{miktar:,} Coin** yere saçıldı ve **#oyunlar** kanalına düştü!"
        await kaybi_oyunlara_dusur(ctx.guild, miktar, ctx.author)

    user_bakiye[author_id] += kazanc
    await msg.edit(content=f"🎰 **Slot Sonucu**\n[ {s[0]} | {s[1]} | {s[2]} ]\n\n{sonuc}\n💼 Kalan Bakiye: **{user_bakiye[author_id]:,} Coin**")

@bot.command(name="rulet", help="Renk bazlı rulet oyunu (Örn: !rulet kirmizi 10k).")
async def rulet(ctx, renk: str, miktar_str: str = "100"):
    author_id = ctx.author.id
    bakiye_miktari = user_bakiye.get(author_id, 1000)
    renk = renk.lower()
    miktar = sayi_coumle(miktar_str)

    if renk not in ["kirmizi", "siyah", "yesil"]:
        await ctx.send("❌ Geçersiz renk! `kirmizi`, `siyah` veya `yesil` seçmelisin.")
        return

    if miktar <= 0 or bakiye_miktari < miktar:
        await ctx.send("❌ Yetersiz bakiye veya geçersiz miktar!")
        return

    user_bakiye[author_id] -= miktar
    msg = await ctx.send(f"🎲 Rulet çarkı dönüyor... ({renk.upper()} için {miktar:,} coin yatırıldı)")
    await asyncio.sleep(1.5)

    sans = random.choices(["kirmizi", "siyah", "yesil"], weights=[48, 48, 4], k=1)[0]
    
    kazanc = 0
    if sans == renk:
        carpan = 14 if sans == "yesil" else 2
        kazanc = miktar * carpan
        user_bakiye[author_id] += kazanc
        sonuc = f"🎯 Çark **{sans.upper()}** geldi! Kazandın: **+{kazanc:,} Coin**"
    else:
        sonuc = f"❌ Kaybettin! **{miktar:,} Coin** yere saçıldı ve **#oyunlar** kanalına düştü."
        await kaybi_oyunlara_dusur(ctx.guild, miktar, ctx.author)

    await msg.edit(content=f"🎲 **Rulet Sonucu**\nGelen: **{sans.upper()}**\n\n{sonuc}\n💼 Kalan Bakiye: **{user_bakiye[author_id]:,} Coin**")


# --- !SOPA ---

@bot.command(name="sopa", help="Belirtilen kullanıcıya 40 saniye timeout verir ve mesajlarını 2 dakika bozar.")
async def sopa(ctx, member: discord.Member, *, sebep: str = "Test sopası"):
    try:
        sure = timedelta(seconds=40)
        await member.timeout(sure, reason=sebep)
        sopa_cezalilar[member.id] = datetime.now() + timedelta(minutes=2)

        embed = discord.Embed(
            title="🔨 Kafaya Sopa İndi!",
            description=f"**{member.mention}** adlı kişinin kafasına kaya gibi sopa indirildi!",
            color=0xE74C3C,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="⏳ Timeout Süresi", value="40 Saniye", inline=True)
        embed.add_field(name="🌀 Bozuk Mesaj Süresi", value="2 Dakika", inline=True)
        embed.add_field(name="📌 Sebep", value=sebep, inline=False)
        embed.set_footer(text=f"Sopalayan: {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Sopa atılırken hata oluştu: {e}")


# --- DİĞER PRO KOMUTLAR ---

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
        embed.add_field(name="💵 USD", value=f"**${price_usd:,.4f}**", inline=True)
        embed.add_field(name="₺ TRY", value=f"**₺{price_try:,.4f}**", inline=True)
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

@bot.command(name="avatar", help="Profil fotoğrafını büyütür.")
async def avatar(ctx, member: discord.Member = None):
    target = member or ctx.author
    url = target.avatar.url if target.avatar else target.default_avatar.url
    embed = discord.Embed(title=f"🖼️ {target.name} - Avatar", color=0x3498DB).set_image(url=url)
    await ctx.send(embed=embed)

@bot.command(name="sunucubilgi", help="Sunucu künyesi.")
async def sunucubilgi(ctx):
    g = ctx.guild
    embed = discord.Embed(title=f"🛡️ {g.name}", color=0x9B59B6)
    if g.icon: embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="Sahip", value=g.owner, inline=True)
    embed.add_field(name="Üye", value=g.member_count, inline=True)
    await ctx.send(embed=embed)

@bot.command(name="kullanicibilgi", help="Kullanıcı kartı.")
async def kullanicibilgi(ctx, member: discord.Member = None):
    t = member or ctx.author
    embed = discord.Embed(title=f"👤 {t.name}", color=0xE67E22)
    embed.set_thumbnail(url=t.avatar.url if t.avatar else t.default_avatar.url)
    embed.add_field(name="ID", value=t.id, inline=True)
    embed.add_field(name="Kayıt", value=t.created_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="afk", help="AFK moduna geçer.")
async def afk(ctx, *, sebep: str = "Yok"):
    afk_users[ctx.author.id] = sebep
    await ctx.send(f"💤 {ctx.author.mention} AFK! Sebep: {sebep}")

@bot.command(name="oylama", help="Hızlı anket.")
async def oylama(ctx, *, soru: str):
    await ctx.message.delete()
    m = await ctx.send(embed=discord.Embed(title="🗳️ Oylama", description=soru, color=0xF1C40F))
    await m.add_reaction("✅")
    await m.add_reaction("❌")

@bot.command(name="espri", help="Soğuk espri.")
async def espri(ctx):
    await ctx.send(random.choice(["Geçen taksi çevirdim, hâlâ dönüyor.", "Adam gülmüş, karısı lavabo.", "Aklımı kaçırdım, arıyorum."]))

@bot.command(name="kartcek", help="İskambil kartı.")
async def kartcek(ctx):
    await ctx.send(f"🃏 Kartın: **{random.choice(['As','Kız','Papaz','10','7'])} {random.choice(['Maça ♠️','Kupa ♥️','Karo ♦️','Sinek ♣️'])}**")

@bot.command(name="tkm", help="Taş kağıt makas.")
async def tkm(ctx, secim: str):
    s = ["taş", "kağıt", "makas"]
    if secim.lower() not in s: return await ctx.send("Geçersiz!")
    b = random.choice(s)
    await ctx.send(f"Sen: {secim} | Bot: {b} | Sonuç: {'Berabere' if secim==b else 'Kazandın' if (secim=='taş' and b=='makas') or (secim=='kağıt' and b=='taş') or (secim=='makas' and b=='kağıt') else 'Kaybettin'}")

@bot.command(name="bilgi", help="İlginç bilgi.")
async def bilgi(ctx):
    await ctx.send(random.choice(["Ahtapotun 3 kalbi vardır.", "Bal asla bozulmaz.", "İnsan DNA'sı muzla %50 benzer."]))

@bot.command(name="zaratma", help="Zar at.")
async def zaratma(ctx, adet: int = 1):
    res = [random.randint(1, 6) for _ in range(min(max(adet, 1), 5))]
    await ctx.send(f"Zarlar: {res} (Toplam: {sum(res)})")

@bot.command(name="tersyaz", help="Tersten yaz.")
async def tersyaz(ctx, *, m: str):
    await ctx.send(m[::-1])

@bot.command(name="yazi", help="Büyük başlık.")
async def yazi(ctx, *, m: str):
    await ctx.send(f"# {m}")

@bot.command(name="ping", help="Gecikme.")
async def ping(ctx):
    await ctx.send(f"Pong! 🚀 {round(bot.latency * 1000)}ms")

@bot.command(name="yazitura", help="Yazı tura atar.")
async def yazitura(ctx):
    await ctx.send(f"🪙 Sonuç: **{random.choice(['Yazı 🦅', 'Tura 🪙'])}**")

@bot.command(name="sifre", help="Şifre üretir.")
async def sifre(ctx, l: int = 10):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%"
    await ctx.send(f"🔐 Şifre: `{''.join(random.choice(chars) for _ in range(min(max(l,6),30)))}`")

@bot.command(name="renk", help="Rastgele renk.")
async def renk(ctx):
    c = random.randint(0, 0xFFFFFF)
    await ctx.send(embed=discord.Embed(title=f"🎨 #{c:06X}", color=c))

@bot.command(name="fakeprofil", help="Sahte kimlik.")
async def fakeprofil(ctx):
    isim = random.choice(['Ali Yılmaz', 'Ayşe Demir', 'John Doe'])
    ulke = random.choice(['Türkiye', 'Almanya', 'ABD'])
    await ctx.send(f"🕵️ Kimlik: {isim} - {ulke}")

@bot.command(name="soz", help="Felsefi söz.")
async def soz(ctx):
    await ctx.send(f"💡 *{random.choice(['Çalışıyorsa dokunma!', 'Önce problemi çöz.', 'Kahve girer kod çıkar.'])}*")

@bot.command(name="kedi", help="Kedi resmi.")
async def kedi(ctx):
    try:
        url = requests.get("https://api.thecatapi.com/v1/images/search", timeout=3).json()[0]['url']
        await ctx.send(embed=discord.Embed(title="🐱 Kedi").set_image(url=url))
    except:
        await ctx.send("🐱 Kedi API uykuda!")

@bot.command(name="kopek", help="Köpek resmi.")
async def kopek(ctx):
    try:
        url = requests.get("https://dog.ceo/api/breeds/image/random", timeout=3).json()['message']
        await ctx.send(embed=discord.Embed(title="🐶 Köpek").set_image(url=url))
    except:
        await ctx.send("🐶 Köpek API uykuda!")

@bot.command(name="hesapla", help="Matematik.")
async def hesapla(ctx, *, expr: str):
    try:
        if not all(c in "0123456789+-*/(). " for c in expr): return await ctx.send("Geçersiz karakter!")
        await ctx.send(f"🧮 Sonuç: **{eval(expr)}**")
    except:
        await ctx.send("⚠️ Hesaplama hatası!")

@bot.command(name="yavasmod", help="Yavaş mod.")
async def yavasmod(ctx, saniye: int):
    await ctx.channel.edit(slowmode_delay=saniye)
    await ctx.send(f"⏳ Yavaş mod {saniye} saniye yapıldı.")

@bot.command(name="tarih", help="Bugünün tarihi.")
async def tarih(ctx):
    await ctx.send(f"📅 Bugünün tarihi: {datetime.now().strftime('%d.%m.%Y')}")

@bot.command(name="saat", help="Anlık saat.")
async def saat(ctx):
    await ctx.send(f"⏰ Saat: {datetime.now().strftime('%H:%M:%S')}")

@bot.command(name="sec", help="Seçim yap.")
async def sec(ctx, *, secenekler: str):
    lst = secenekler.split(",")
    await ctx.send(f"🎯 Seçtiğim: **{random.choice(lst).strip()}**")

@bot.command(name="hack", help="Şaka hack.")
async def hack(ctx, member: discord.Member = None):
    m = member or ctx.author
    await ctx.send(f"💻 {m.mention} hackleniyor... %100 Şifre ele geçirildi: `12345`")

@bot.command(name="kiss", help="Öpücük at.")
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"💋 {ctx.author.mention} adlı kullanıcı {member.mention} kişisini öptü!")

@bot.command(name="tokat", help="Tokat at.")
async def tokat(ctx, member: discord.Member):
    await ctx.send(f" 👋 {ctx.author.mention}, {member.mention} kişisine şak diye tokadı bastı!")

@bot.command(name="saril", help="Sarıl.")
async def saril(ctx, member: discord.Member):
    await ctx.send(f"🤗 {ctx.author.mention}, {member.mention} kişisine sımsıkı sarıldı!")

@bot.command(name="havali", help="Havalı yazı.")
async def havali(ctx, *, metin: str):
    await ctx.send(f"✨ **__{metin.upper()}__** ✨")

@bot.command(name="mizah", help="Mizahşör.")
async def mizah(ctx):
    await ctx.send("Komedi dükkanı kapandı arkadaşlar.")

@bot.command(name="melon", help="Gizli komut.")
async def melon(ctx):
    await ctx.send("🍉 Karpuz sever misin?")

@bot.command(name="sunucukurucu", help="Kurucu bilgisi.")
async def sunucukurucu(ctx):
    await ctx.send(f"👑 Kurucu: {ctx.guild.owner}")

@bot.command(name="kanalbilgi", help="Kanal bilgisi.")
async def kanalbilgi(ctx):
    await ctx.send(f"📁 Kanal adı: {ctx.channel.name}, ID: {ctx.channel.id}")

@bot.command(name="rolbilgi", help="Rol sayısı.")
async def rolbilgi(ctx):
    await ctx.send(f"🎭 Toplam Rol Sayısı: {len(ctx.guild.roles)}")

@bot.command(name="emoji", help="Rastgele emoji.")
async def emoji(ctx):
    await ctx.send(random.choice(["🔥", "🚀", "😎", "🎉", "💻", "🤖", "⭐"]))

@bot.command(name="yetenek", help="Yetenek testi.")
async def yetenek(ctx):
    await ctx.send(f"🌟 Yetenek puanın: %{random.randint(50, 100)}")

@bot.command(name="sans", help="Günün şansı.")
async def sans(ctx, member: discord.Member = None):
    await ctx.send(f"🍀 Şans oranım: %{random.randint(1, 100)}")

@bot.command(name="zeka", help="Zeka testi.")
async def zeka(ctx):
    await ctx.send(f"🧠 IQ Seviyen: {random.randint(90, 160)}")

@bot.command(name="kral", help="Kral kim.")
async def kral(ctx):
    await ctx.send(f"👑 Bu sunucunun kralı: {ctx.author.mention}!")

@bot.command(name="botdurum", help="Bot durumu.")
async def botdurum(ctx):
    await ctx.send("🤖 Bot %100 stabil, VDS'e geçişe hazır!")


token = os.getenv("DISCORD_TOKEN")
if not token:
    print("Hata: Token bulunamadı!")
    sys.exit(1)

bot.run(token)
