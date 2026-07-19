import os
import random
import asyncio
import datetime
import discord
from discord.ext import commands

TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Bazı üye komutları için bu iznin Developer Portal'da açık olması gerekir

bot = commands.Bot(command_prefix='!', intents=intents)

# 1. BOT HAZIR OLMA OLAYI
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="40 Özellikli Canavar Bot v1.0"))
    print(f'{bot.user.name} 40 özellikli sistemiyle aktif edildi!')

# 2. YENİ ÜYE GELDİĞİNDE SELAMLAMA
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f'Hoş geldin {member.mention}! Aramıza katıldığın için mutluyuz. 🎉')

# --- KOMUTLAR BAŞLIYOR ---

# 3. Yazı Tura
@bot.command()
async def yazitura(ctx):
    await ctx.send(f"🪙 Sonuç: **{random.choice(['Yazı', 'Tura'])}**")

# 4. Sihirli 8 Topu
@bot.command(name="8ball")
async def sihirli_top(ctx, *, soru):
    cevaplar = ["Kesinlikle", "Şüphesiz", "Buna güvenebilirsin", "Daha sonra tekrar sor", "Şimdi tahmin edemem", "Buna odaklanıp tekrar sor", "Kaynağım hayır diyor", "Görünüşe göre pek iyi değil", "Çok şüpheli"]
    await ctx.send(f"🔮 **Soru:** {soru}\n Cevap: **{random.choice(cevaplar)}**")

# 5. Mesaj Silme (Moderasyon)
@bot.command()
async def sil(ctx, miktar: int):
    if miktar > 100:
        return await ctx.send("Tek seferde en fazla 100 mesaj silebilirsin!")
    await ctx.channel.purge(limit=miktar + 1)
    msg = await ctx.send(f"🗑️ {miktar} adet mesaj temizlendi.")
    await asyncio.sleep(3)
    await msg.delete()

# 6. Sunucu Bilgisi
@bot.command()
async def sunucubilgi(ctx):
    embed = discord.Embed(title=f"{ctx.guild.name} Sunucu Bilgileri", color=discord.Color.blue())
    embed.add_field(name="Üye Sayısı", value=ctx.guild.member_count)
    embed.add_field(name="Oluşturulma Tarihi", value=ctx.guild.created_at.strftime("%d/%m/%Y"))
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    await ctx.send(embed=embed)

# 7. Kullanıcı Bilgisi
@bot.command()
async def kullanıcı(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name} Profil Kartı", color=discord.Color.green())
    embed.add_field(name="Hesap Açılışı", value=member.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="Sunucuya Katılım", value=member.joined_at.strftime("%d/%m/%Y"))
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    await ctx.send(embed=embed)

# 8. Ping Ölçer
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Gecikme süresi: **{round(bot.latency * 1000)}ms**")

# 9. Rastgele Sayı Üretici
@bot.command()
async def zar(ctx):
    await ctx.send(f"🎲 Zar attın! Çıkan sayı: **{random.randint(1, 6)}**")

# 10. Aşk Ölçer
@bot.command()
async def askolcer(ctx, kisi: discord.Member):
    oran = random.randint(0, 100)
    await ctx.send(f"❤️ {ctx.author.mention} ile {kisi.mention} arasındaki aşk oranı: **%{oran}**")

# 11. Sayı Tahmin Oyunu
@bot.command()
async def sayitahmin(ctx):
    dogru_sayi = random.randint(1, 10)
    await ctx.send("🤖 1 ile 10 arasında bir sayı tuttum. Tahmin et bakalım! (Sadece sayıyı yaz)")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

    try:
        tahmin = await bot.wait_for('message', check=check, timeout=15.0)
        if int(tahmin.content) == dogru_sayi:
            await ctx.send("🎉 Tebrikler, doğru bildin!")
        else:
            await ctx.send(f"❌ Bilemedin! Doğru cevap **{dogru_sayi}** olacaktı.")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Süren doldu! Tuttuğum sayı **{dogru_sayi}** idi.")

# 12. Avatar Gösterici
@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    url = member.avatar.url if member.avatar else "https://discord.com/assets/c0990d036356445175e14d3ca9c00b08.png"
    await ctx.send(f"📸 {member.name} kullanıcısının avatarı:\n{url}")

# 13. Kelime Ters Çevirici
@bot.command()
async def terscevir(ctx, *, metin):
    await ctx.send(metin[::-1])

# 14. Taş Kağıt Makas
@bot.command()
async def tkm(ctx, secim: str):
    secenekler = ["taş", "kağıt", "makas"]
    bot_secimi = random.choice(secenekler)
    secim = secim.lower()
    if secim not in secenekler:
        return await ctx.send("Lütfen sadece 'taş', 'kağıt' veya 'makas' yazın.")
    
    if secim == bot_secimi:
        await ctx.send(f"Berabere! İkimiz de **{secim}** seçtik.")
    elif (secim == "taş" and bot_secimi == "makas") or (secim == "kağıt" and bot_secimi == "taş") or (secim == "makas" and bot_secimi == "kağıt"):
        await ctx.send(f"Tebrikler sen kazandın! Sen: **{secim}** | Bot: **{bot_secimi}**")
    else:
        await ctx.send(f"Kaybettin! Sen: **{secim}** | Bot: **{bot_secimi}**")

# 15. Sunucu Logosu
@bot.command()
async def sunucuresmi(ctx):
    if ctx.guild.icon:
        await ctx.send(ctx.guild.icon.url)
    else:
        await ctx.send("Bu sunucunun bir logosu yok.")

# 16. Rastgele Espri
@bot.command()
async def espri(ctx):
    espriler = [
        "Geçen gün bir taksi çevirdim, hala dönüyor.",
        "Radyo çalıyordu ama polis yakalayamadı.",
        "İngilizcem çok iyi, 'Yes' biliyorum, 'No' biliyorum... Başka ne var ki?",
        "Adamın biri gülmüş, saksıya dikmişler."
    ]
    await ctx.send(random.choice(espriler))

# 17. Tokat Atma
@bot.command()
async def tokat(ctx, member: discord.Member):
    await ctx.send(f"✋ {ctx.author.mention}, {member.mention} kullanıcısına okkalı bir tokat attı!")

# 18. IQ Testi
@bot.command()
async def iq(ctx):
    await ctx.send(f"🧠 Beyin hücrelerini tarıyorum... IQ Skorun: **{random.randint(50, 150)}**")

# 19. Şanslı Sayı
@bot.command()
async def sanslisayi(ctx):
    await ctx.send(f"🔮 Bugünün senin için uğurlu sayısı: **{random.randint(1, 100)}**")

# 20. Seçim Yapıcı
@bot.command()
async def sec(ctx, *, secenekler):
    liste = secenekler.split(",")
    await ctx.send(f"🤔 Bence en mantıklısı: **{random.choice(liste).strip()}**")

# 21. Büyük Harfe Çevir
@bot.command()
async def buyut(ctx, *, metin):
    await ctx.send(metin.upper())

# 22. Küçük Harfe Çevir
@bot.command()
async def kucult(ctx, *, metin):
    await ctx.send(metin.lower())

# 23. Botun Yaşı
@bot.command()
async def botyas(ctx):
    await ctx.send("🤖 Ben daha çok gencim, 2026 model son teknoloji bir yapay zekayım!")

# 24. Üye Banlama (Yetki gerektirir)
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 {member.name} sunucudan banlandı! Sebep: {sebep}")

# 25. Üye Kickleme (Yetki gerektirir)
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member.name} sunucudan atıldı! Sebep: {sebep}")

# 26. Dünyanın En Komik Şakası (Spoiler İçerir)
@bot.command()
async def saka(ctx):
    await ctx.send("||Dünyada 10 çeşit insan vardır; ikilik tabanı bilenler ve bilmeyenler.||")

# 27. Rol Verme (Basit)
@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"✅ {member.mention} kullanıcısına **{role.name}** rolü verildi.")

# 28. Rol Alma
@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"❌ {member.mention} kullanıcısından **{role.name}** rolü geri alındı.")

# 29. Kanal Kilitleme
@bot.command()
@commands.has_permissions(manage_channels=True)
async def kilitle(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Bu kanal yeni mesaj gönderimine kapatıldı.")

# 30. Kanal Kilidi Açma
@bot.command()
@commands.has_permissions(manage_channels=True)
async def kilitac(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Bu kanalın kilidi açıldı, herkes yazabilir.")

# 31. Kaç Gün Oldu?
@bot.command()
async def kacgun(ctx):
    fark = datetime.datetime.now(datetime.timezone.utc) - ctx.guild.created_at
    await ctx.send(f"📅 Bu sunucu kurulalı tam **{fark.days}** gün olmuş!")

# 32. Havalı Yazı Formatı
@bot.command()
async def havali(ctx, *, metin):
    await ctx.send(f"✨ 𝓔𝓿𝓮𝓽, ş𝓾 𝓪𝓷 𝓱𝓪𝓿𝓪𝓵ı 𝔂𝓪𝔃ı𝓵ı𝔂𝓸𝓻: **{metin}** ✨")

# 33. Madeni Para Fırlat
@bot.command()
async def firlat(ctx):
    await ctx.send(f"🚀 Parayı havaya fırlattın ve masanın altına kaçtı! Bulamıyoruz...")

# 34. Takma Ad Değiştirme
@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nickdegis(ctx, member: discord.Member, *, yeni_isim):
    await member.edit(nick=yeni_isim)
    await ctx.send(f"📝 {member.name} kullanıcısının ismi değiştirildi: **{yeni_isim}**")

# 35. Rastgele Renk Kodu
@bot.command()
async def renk(ctx):
    renk_kodu = "".join([random.choice("0123456789ABCDEF") for _ in range(6)])
    await ctx.send(f"🎨 Senin için rastgele bir renk kodu: **#{renk_kodu}**")

# 36. Toplama İşlemi
@bot.command()
async def topla(ctx, a: int, b: int):
    await ctx.send(f"➕ Sonuç: **{a + b}**")

# 37. Çıkarma İşlemi
@bot.command()
async def cikar(ctx, a: int, b: int):
    await ctx.send(f"➖ Sonuç: **{a - b}**")

# 38. Çarpma İşlemi
@bot.command()
async def carp(ctx, a: int, b: int):
    await ctx.send(f"✖️ Sonuç: **{a * b}**")

# 39. Bölme İşlemi
@bot.command()
async def bol(ctx, a: int, b: int):
    if b == 0:
        return await ctx.send("🚨 Bir sayı sıfıra bölünemez!")
    await ctx.send(f"➗ Sonuç: **{a / b}**")

# 40. Gelişmiş Yardım Menüsü
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="📜 Canavar Bot Komut Menüsü (Tam 40 Özellik)", color=discord.Color.purple())
    embed.description = (
        "**Eğlence:** `!yazitura`, `!8ball`, `!zar`, `!askolcer`, `!sayitahmin`, `!tkm`, `!espri`, `!tokat`, `!iq`, `!sanslisayi`, `!firlat`, `!saka` \n"
        "**Araçlar & Bilgi:** `!sunucubilgi`, `!kullanıcı`, `!ping`, `!avatar`, `!sunucuresmi`, `!terscevir`, `!sec`, `!buyut`, `!kucult`, `!botyas`, `!kacgun`, `!havali`, `!renk` \n"
        "**Matematik:** `!topla`, `!cikar`, `!carp`, `!bol` \n"
        "**Moderasyon:** `!sil`, `!ban`, `!kick`, `!rolver`, `!rolal`, `!kilitle`, `!kilitac`, `!nickdegis` \n"
        "**Olaylar:** Sunucuya yeni biri gelince otomatik karşılama ve oynuyor durumu!"
    )
    await ctx.send(embed=embed)

# Varsayılan yardım komutunu kapatıp kendi yazdığımızı aktif ediyoruz
bot.remove_command('help')

bot.run(TOKEN)
