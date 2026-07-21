import os
import sys
import discord

intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot giriş yaptı: {client.user}")
    try:
        channel_id = os.getenv("DISCORD_CHANNEL_ID")
        channel = None

        # 1. Önce verilen ID'yi bulmaya çalışalım
        if channel_id and channel_id.strip():
            try:
                channel = await client.fetch_channel(int(channel_id))
            except Exception:
                print("Girilen Kanal ID geçersiz, sunucudaki ilk kanal aranıyor...")

        # 2. Bulunamadıysa sunucudaki ilk uygun metin kanalını seç
        if not channel:
            for guild in client.guilds:
                for c in guild.text_channels:
                    # Yazma iznimiz var mı kontrol et
                    if c.permissions_for(guild.me).send_messages:
                        channel = c
                        break
                if channel:
                    break

        if not channel:
            print("Hata: Mesaj atılabilecek hiçbir metin kanalı bulunamadı!")
            sys.exit(1)

        # GitHub Actions ortam değişkenleri
        commit_message = os.getenv("GITHUB_COMMIT_MESSAGE", "Commit mesajı bulunamadı")
        commit_author = os.getenv("GITHUB_ACTOR", "Bilinmeyen Yazar")
        repo_name = os.getenv("GITHUB_REPOSITORY", "Bilinmeyen Repo")
        commit_sha_full = os.getenv("GITHUB_SHA", "0000000")
        commit_sha = commit_sha_full[:7] if commit_sha_full else "0000000"
        commit_url = f"https://github.com/{repo_name}/commit/{commit_sha_full}"
        ref_name = os.getenv("GITHUB_REF_NAME", "main")
        workflow_name = os.getenv("GITHUB_WORKFLOW", "GitHub Actions")

        # Havalı Python Embed tasarımı
        embed = discord.Embed(
            title="🚀 Yeni Kod Güncellemesi Alındı!",
            description="Depoda hareketlilik var! Yeni commit başarıyla sisteme işlendi ve Discord'a bildirildi.",
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
        embed.set_footer(text="GitHub Actions Python Bot • Otomatik Bildirim", icon_url="https://cdn-icons-png.flaticon.com/512/25/25231.png")

        # Mesajı çak
        await channel.send(embed=embed)
        print(f"Bildirim başarıyla '{channel.name}' kanalına fırlatıldı!")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        await client.close()
        sys.exit(0)

token = os.getenv("DISCORD_TOKEN")
if not token:
    print("Hata: DISCORD_TOKEN bulunamadı!")
    sys.exit(1)

client.run(token)
