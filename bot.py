import os
import discord
from discord.ext import commands
import requests

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

    username = username.lstrip('@')
    msg = await ctx.send(f"🔍 `{username}` profili derinlemesine taranıyor...")

    try:
        # 1. Kullanıcı ID ve temel bilgileri bulma
        search_res = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [username], "excludeBannedUsers": True}
        )
        search_data = search_res.json()

        if not search_data.get("data") or len(search_data["data"]) == 0:
            await msg.edit(content=f"❌ `{username}` adında aktif bir Roblox kullanıcı bulunamadı!")
            return

        user_info = search_data["data"][0]
        user_id = user_info["id"]
        display_name = user_info["displayName"]
        name = user_info["name"]

        # 2. Detaylı Bilgiler (Biyografi, Kayıt Tarihi, Ban Durumu)
        detail_res = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
        detail_data = detail_res.json()
        
        bio = detail_data.get("description", "Biyografi yok.")
        if len(bio) > 150:  
            bio = bio[:150] + "..."
        if not bio.strip():
            bio = "Boş"

        created_at = detail_data.get("created", "Bilinmiyor")[:10]
        is_banned = detail_data.get("isBanned", False)
        status_text = "🚫 Banlı" if is_banned else "✅ Aktif / Temiz"

        # 3. Avatar Resmi (Tam boy veya Headshot - Yüksek Kalite)
        thumb_res = requests.get(
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false"
        )
        thumb_data = thumb_res.json()
        avatar_url = thumb_data["data"][0]["imageUrl"]

        # 4. Arkadaş, Takipçi ve Takip Edilen Sayıları
        friends_res = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends/count")
        friends_count = friends_res.json().get("count", 0)

        followers_res = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followers/count")
        followers_count = followers_res.json().get("count", 0)

        following_res = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/following/count")
        following_count = following_res.json().get("count", 0)

        # 5. Rozet (Badge) Sayısı
        badges_res = requests.get(f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=10")
        badges_count = len(badges_res.json().get("data", []))
        badges_display = f"{badges_count}+" if badges_count >= 10 else str(badges_count)

        # Discord Embed Tasarımı (Daha detaylı ve zengin)
        embed = discord.Embed(
            title=f"⚡ {display_name} (`@{name}`)",
            url=f"https://www.roblox.com/users/{user_id}/profile",
            color=0x6366f1
        )
        
        embed.set_thumbnail(url=avatar_url)
        
        embed.add_field(name="📜 Biyografi", value=f"```{bio}```", inline=False)
        embed.add_field(name="📅 Kayıt Tarihi", value=f"`{created_at}`", inline=True)
        embed.add_field(name="🛡️ Hesap Durumu", value=status_text, inline=True)
        embed.add_field(name="🏆 Rozetler", value=f"`{badges_display}`", inline=True)
        
        embed.add_field(name="👥 Arkadaş", value=f"`{friends_count}`", inline=True)
        embed.add_field(name="📥 Takipçi", value=f"`{followers_count}`", inline=True)
        embed.add_field(name="📤 Takip Edilen", value=f"`{following_count}`", inline=True)
        
        embed.set_footer(text=f"ID: {user_id} • Roblox Flex Bot 🚀", icon_url=avatar_url)

        await msg.edit(content=None, embed=embed)

    except Exception as e:
        print(f"Hata oluştu: {e}")
        await msg.edit(content="⚠️ Bilgiler çekilirken bir hata oluştu.")

token = os.environ.get('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("HATA: DISCORD_TOKEN bulunamadı!")
