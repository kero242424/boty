import os
import discord
from discord.ext import commands
import requests

# Botun yetkileri (Intents)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot aktif ve bağlandı: {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="!ara <roblox_adi>"))

@bot.command(name="ara")
async def roblox_ara(ctx, username: str = None):
    if not username:
        await ctx.send("⚠️ Lütfen bir Roblox kullanıcı adı gir! Örnek: `!ara kerocu24`")
        return

    # Başındaki @ işaretini temizle
    username = username.lstrip('@')
    
    # Bekliyor mesajı
    msg = await ctx.send(f"🔍 `{username}` aranıyor...")

    try:
        # 1. Kullanıcı ID ve temel bilgilerini bulma
        search_res = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [username], "excludeBannedUsers": True}
        )
        search_data = search_res.json()

        if not search_data.get("data") or len(search_data["data"]) == 0:
            await msg.edit(content=f"❌ `{username}` adında bir Roblox kullanıcı bulunamadı!")
            return

        user_info = search_data["data"][0]
        user_id = user_info["id"]
        display_name = user_info["displayName"]
        name = user_info["name"]

        # 2. Detaylı Bilgiler (Biyografi ve Kayıt Tarihi)
        detail_res = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
        detail_data = detail_res.json()
        
        bio = detail_data.get("description", "Biyografi yok.")
        if len(bio) > 100:  
            bio = bio[:100] + "..."
        if not bio.strip():
            bio = "Boş"

        created_at = detail_data.get("created", "Bilinmiyor")[:10] # Sadece YYYY-MM-DD

        # 3. Avatar Resmi (Headshot)
        thumb_res = requests.get(
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false"
        )
        thumb_data = thumb_res.json()
        avatar_url = thumb_data["data"][0]["imageUrl"]

        # 4. Arkadaş Sayısı
        friends_res = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends/count")
        friends_count = friends_res.json().get("count", "Gizli")

        # Discord Embed (Guns.lol tarzı şık kart)
        embed = discord.Embed(
            title=f"{display_name} (@{name})",
            url=f"https://www.roblox.com/users/{user_id}/profile",
            description=f"```{bio}```",
            color=0x3b82f6
        )
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="👥 Arkadaş", value=str(friends_count), inline=True)
        embed.add_field(name="📅 Kayıt Tarihi", value=str(created_at), inline=True)
        embed.set_footer(text="Roblox Flex Bot ⚡", icon_url=avatar_url)

        await msg.edit(content=None, embed=embed)

    except Exception as e:
        print(f"Hata oluştu: {e}")
        await msg.edit(content="⚠️ Bilgiler çekilirken bir hata oluştu.")

# Tokeni GitHub Secrets içinden (DISCORD_TOKEN) güvenle alır
token = os.environ.get('DISCORD_TOKEN')

if not token:
    print("HATA: DISCORD_TOKEN bulunamadı!")
else:
    bot.run(token)
