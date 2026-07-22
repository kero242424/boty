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
    msg = await ctx.send(f"🔍 `{username}` evrensel olarak taranıyor, her şey çekiliyor...")

    try:
        # 1. Kullanıcı ID ve Temel Bilgiler
        search_res = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [username], "excludeBannedUsers": True}
        )
        search_data = search_res.json()

        if not search_data.get("data") or len(search_data["data"]) == 0:
            await msg.edit(content=f"❌ `{username}` adında aktif/geçerli bir Roblox kullanıcı bulunamadı!")
            return

        user_info = search_data["data"][0]
        user_id = user_info["id"]
        display_name = user_info["displayName"]
        name = user_info["name"]

        # 2. Detaylı Profil Bilgileri (Biyografi, Kayıt, Ban Durumu)
        detail_res = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
        detail_data = detail_res.json()
        
        bio = detail_data.get("description", "Biyografi yok.")
        if len(bio) > 120:  
            bio = bio[:120] + "..."
        if not bio.strip():
            bio = "Boş"

        created_at = detail_data.get("created", "Bilinmiyor")[:10]
        is_banned = detail_data.get("isBanned", False)
        status_text = "🚫 Banlı / Askıda" if is_banned else "🟢 Aktif Hesap"

        # 3. Anlık Durum (Oyunda mı, Çevrim içi mi?)
        presence_res = requests.post(
            "https://presence.roblox.com/v1/presence/users",
            json={"userIds": [user_id]}
        )
        presence_data = presence_res.json().get("userPresences", [{}])[0]
        presence_type = presence_data.get("userPresenceType", 0)
        
        # Durum kodları: 0=Çevrimdışı, 1=Çevrim içi, 2=Oyunda, 3=Stüdyoda
        status_map = {0: "🔴 Çevrimdışı", 1: "🟢 Çevrim İçi", 2: "🎮 Oyunda", 3: "💻 Studio'da"}
        current_status = status_map.get(presence_type, "Bilinmiyor")
        game_name = presence_data.get("lastLocation", "")

        # 4. Takipçi, Takip Edilen ve Arkadaş İstatistikleri
        friends_count = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends/count").json().get("count", 0)
        followers_count = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followers/count").json().get("count", 0)
        following_count = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/following/count").json().get("count", 0)

        # 5. Gruplar (Ana grubu / Rolü)
        groups_res = requests.get(f"https://groups.roblox.com/v1/users/{user_id}/groups/roles")
        groups_data = groups_res.json().get("data", [])
        primary_group = "Yok"
        if groups_data:
            # En üstteki grubu veya ilk grubu alalım
            primary_group = f"{groups_data[0]['group']['name']} ({groups_data[0]['role']['name']})"
            if len(primary_group) > 35: primary_group = primary_group[:32] + "..."

        # 6. Full Boy / Yüksek Kaliteli Avatar Görseli
        thumb_res = requests.get(
            f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=720x720&format=Png&isCircular=false"
        )
        avatar_url = thumb_res.json()["data"][0]["imageUrl"]

        # 7. Rozet İstatistiği
        badges_res = requests.get(f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100")
        badges_count = len(badges_res.json().get("data", []))

        # Discord Embed (Ultra Detaylı Kart Tasarımı)
        embed = discord.Embed(
            title=f"👑 {display_name} (`@{name}`)",
            url=f"https://www.roblox.com/users/{user_id}/profile",
            description=f"**Bio:** ```{bio}```",
            color=0x4f46e5
        )
        
        # Büyük tam boy avatar görseli sağ üst köşeye veya büyük resim olarak eklenir
        embed.set_image(url=avatar_url)
        
        # Alanlar (Fields)
        embed.add_field(name="📌 Hesap ID", value=f"`{user_id}`", inline=True)
        embed.add_field(name="📅 Kayıt Tarihi", value=f"`{created_at}`", inline=True)
        embed.add_field(name="🛡️ Durum", value=status_text, inline=True)
        
        embed.add_field(name="⚡ Anlık Aktivite", value=f"{current_status}", inline=True)
        if game_name and presence_type == 2:
            embed.add_field(name="🕹️ Oynadığı Yer", value=f"`{game_name}`", inline=True)
            
        embed.add_field(name="👥 Arkadaş", value=f"`{friends_count}`", inline=True)
        embed.add_field(name="📥 Takipçi", value=f"`{followers_count}`", inline=True)
        embed.add_field(name="📤 Takip Edilen", value=f"`{following_count}`", inline=True)
        
        embed.add_field(name="⭐ Başlıca Grup", value=f"`{primary_group}`", inline=False)
        embed.add_field(name="🏆 Toplam Rozet", value=f"`{badges_count}+`", inline=True)

        embed.set_footer(text=f"Roblox Ultimate Flex Bot • İsteyen: {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        await msg.edit(content=None, embed=embed)

    except Exception as e:
        print(f"Hata detayı: {e}")
        await msg.edit(content="⚠️ Veriler çekilirken beklenmeyen bir hata oluştu veya Roblox API limiti aşıldı.")

token = os.environ.get('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("HATA: DISCORD_TOKEN bulunamadı!")
