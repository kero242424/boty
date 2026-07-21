import os
import sys
import discord
from discord.ext import commands

# Botun yetkilerini (intents) açıyoruz (mesajları okuyabilmesi için message_content şart)
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot aktif ve online: {bot.user}")
    
    # Bot ilk açıldığında GitHub'dan tetiklendiyse otomatik commit bildirimi atabilir
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

        # Sadece GitHub Actions üzerinden tetiklendiyse bu env değişkeni dolu gelir
        commit_message = os.getenv("GITHUB_COMMIT_MESSAGE")
        if not commit_message:
            return # Normal manuel açılışta commit bildirimi atıp spam yapmasın

        commit_author = os.getenv("GITHUB_ACTOR", "Bilinmeyen Yazar")
        repo_name = os.getenv("GITHUB_REPOSITORY", "Bilinmeyen Repo")
        commit_sha_full = os.getenv("GITHUB_SHA", "0000000")
        commit_sha = commit_sha_full[:7] if commit_sha_full else "0000000"
        commit_url = f"https://github.com/{repo_name}/commit/{commit_sha_full}"
        ref_name = os.getenv("GITHUB_REF_NAME", "main")
        workflow_name = os.getenv("GITHUB_WORKFLOW", "GitHub Actions")

        embed = discord.Embed(
            title="🚀 Yeni Kod Güncellemesi Alındı!",
            description="Depoda hareketlilik var! Yeni commit başarıyla sisteme işlendi.",
            color=0x00FF7F,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="📁 Proje / Depo", value=f"`{repo_name}`", inline=True)
        embed.add_field(name="🌿 Hedef Dal (Branch)", value=f"`{ref_name}`", inline=True)
        embed.add_field(name="👤 Geliştirici", value=f"**{commit_author}**", inline=True)
        embed.add_field(name="📝 Commit Mesajı", value=f">>> {commit_message}", inline=False)
        embed.add_field(name="🔗 Commit Kodu & Link", value=f"[{commit_sha}]({commit_url})", inline=True)
        embed.add_field(name="⚙️ Çalışan İşlem", value=f"`{workflow_name}`", inline=True)
        embed.set_thumbnail(url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
        embed.set_footer(text="Python Sürekli Aktif Bot • Komut Modu", icon_url="https://cdn-icons-png.flaticon.com/512/25/25231.png")

        await channel.send(embed=embed)
    except Exception as e:
        print(f"Commit bildirimi gönderilemedi: {e}")

# --- BOT KOMUTLARI ---

@bot.command(name="ping", help="Botun gecikme süresini (ms) gösterir.")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! 🏓 Gecikme süresi: **{latency}ms**")

@bot.command(name="selam", help="Bota selam verirsin.")
async def selam(ctx):
    await ctx.send(f"Aleykümselam kralsın! 👑 Nasılsın {ctx.author.mention}?")

@bot.command(name="bilgi", help="Bot ve sistem hakkında bilgi verir.")
async def bilgi(ctx):
    embed = discord.Embed(
        title="🤖 Bot Bilgi Paneli",
        description="Bu bot GitHub entegrasyonlu ve sohbet komutlarına duyarlı özel bir Python botudur.",
        color=0x3498DB
    )
    embed.add_field(name="🛠️ Altyapı", value="Python & Discord.py", inline=True)
    embed.add_field(name="📌 Komut Öneki", value="`!`", inline=True)
    embed.add_field(name="⚡ Durum", value="7/24 Aktif", inline=True)
    embed.set_footer(text=f"İsteyen: {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)

token = os.getenv("DISCORD_TOKEN")
if not token:
    print("Hata: DISCORD_TOKEN bulunamadı!")
    sys.exit(1)

bot.run(token)
