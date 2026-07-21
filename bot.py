import os
import sys
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
        embed.set_footer(text="Python Ultra Bot v3.0", icon_url="https://cdn-icons-png.flaticon.com/512/25/25231.png")

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

@bot.command(name="havadurumu", help="Belirtilen şehrin anlık hava durumunu gösterir.")
async def havadurumu(ctx, *, sehir: str = "Istanbul"):
    try:
        url = f"https://wttr.in/{sehir}?format=j1"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            await ctx.send("❌ Hava durumu bilgisi alınamadı, şehir adını kontrol et.")
            return

        data = response.json()
        current = data['current_condition'][0]
        temp = current['temp_C']
        feels = current['FeelsLikeC']
        desc = current['weatherDesc'][0]['value']
        humidity = current['humidity']
        wind = current['windspeedKmph']

        embed = discord.Embed(
            title=f"🌤️ {sehir.capitalize()} İçin Hava Durumu",
            color=0x3498DB,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="🌡️ Sıcaklık", value=f"**{temp}°C** (Hissedilen: {feels}°C)", inline=True)
        embed.add_field(name="☁️ Durum", value=f"**{desc}**", inline=True)
        embed.add_field(name="💧 Nem Oranı", value=f"%{humidity}", inline=True)
        embed.add_field(name="💨 Rüzgar Hızı", value=f"{wind} km/s", inline=True)
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Bir hata oluştu: {e}")

@bot.command(name="seviye", help="Kullanıcının anlık XP ve seviye durumunu gösterir.")
async def seviye(ctx, member: discord.Member = None):
    target = member or ctx.author
    xp = user_xp.get(target.id, 0)
    level = xp // 100

    embed = discord.Embed(title=f"📊 {target.name} - Seviye Kartı", color=0xE74C3C)
    embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
    embed.add_field(name="⭐ Toplam XP", value=f"{xp} XP", inline=True)
    embed.add_field(name="🏆 Seviye", value=f"Level {level}", inline=True)
    embed.set_footer(text="Sohbet ettikçe XP kazanırsın!")
    
    await ctx.send(embed=embed)

@bot.command(name="anket", help="Sunucuda hızlıca anket açar.")
async def anket(ctx, *, soru: str):
    await ctx.message.delete()
    embed = discord.Embed(
        title="📊 Sunucu Anketi",
        description=f"**{soru}**",
        color=0xF1C40F,
        timestamp=discord.utils.utcnow()
    )
    # Hatanın düzeltildiği yer: tırnaklar düzgünce kapatıldı
    embed.set_footer(text=f"Başlatan: {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    poll_msg = await ctx.send(embed=embed)
    await poll_msg.add_reaction("👍")
    await poll_msg.add_reaction("👎")
    await poll_msg.add_reaction("🤔")

@bot.command(name="ping", help="Gecikme süresini ölçer.")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Roket hızında çalışıyoruz! 🚀 Gecikme: **{latency}ms**")

token = os.getenv("DISCORD_TOKEN")
if not token:
    print("Hata: Token bulunamadı!")
    sys.exit(1)

bot.run(token)
