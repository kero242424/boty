import os
import sys
import random
import asyncio
import logging
import datetime
from typing import Optional
import discord
from discord.ext import commands

# GitHub Actions log akışı için optimize edilmiş loglama
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('CoreEngine')

# Güvenlik ve sürdürülebilirlik için Token environment variable üzerinden çekilir.
# Yerel testlerde veya Actions üzerinde 'DISCORD_TOKEN' adıyla tanımlanmalıdır.
TOKEN = os.getenv("DISCORD_TOKEN", "MTUyNzMyMTQxNjA4NzYzODAxNg.GUXMHz.hLeEQn5LI-LtCLrs8Yh5P2H6iKnyMonb5Mqdgc")

class EnterpriseBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix="!", 
            intents=intents,
            help_command=None
        )
        self.launch_time = datetime.datetime.now(datetime.timezone.utc)
        self.run_once = os.getenv("RUN_ONCE", "false").lower() == "true"

    async def on_ready(self) -> None:
        logger.info(f"Sistem Doğrulandı. Hesap: {self.user} | ID: {self.user.id}")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!yardim"))
        
        # Bot uyandığında sunuculardaki ilk yazılabilir metin kanalına duyuru gönderir
        for guild in self.guilds:
            target_channel = None
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    target_channel = channel
                    break
            
            if target_channel:
                try:
                    embed = discord.Embed(
                        title="🚀 Bot Çevrimiçi!",
                        description="Sistem başarıyla başlatıldı ve GitHub Actions üzerinden aktif edildi.",
                        color=discord.Color.from_rgb(16, 185, 129), # Emerald v4
                        timestamp=datetime.datetime.now(datetime.timezone.utc)
                    )
                    embed.add_field(name="Gecikme Süresi", value=f"⚡ `{round(self.latency * 1000)}ms`", inline=True)
                    embed.add_field(name="Komut Ön Eki", value="⚙️ `!`", inline=True)
                    embed.set_footer(text="Tüm sistemler çalışır durumda. Yardım için: !yardim")
                    
                    await target_channel.send(embed=embed)
                    logger.info(f"Açılış mesajı başarıyla gönderildi: {guild.name} -> #{target_channel.name}")
                except Exception as e:
                    logger.error(f"Açılış mesajı gönderilirken hata oluştu ({guild.name}): {str(e)}")

        if self.run_once:
            logger.info("GitHub Actions tek seferlik mod aktif, bağlantı sonlandırılıyor...")
            await self.close()

    async def on_command_error(self, ctx: commands.Context, error: commands.errors.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ **Yetki Hatası:** Bu komutu çalıştırmak için yetkiniz yetersiz.")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⚠️ **Eksik Parametre:** Komutun kullanım biçimi hatalı. `!yardim` yazarak kontrol edin.")
            return
        
        logger.error(f"Komut Hatası [{ctx.command}]: {str(error)}")
        await ctx.send(f"🔧 **Sistem Hatası:** `{str(error)}`")

bot = EnterpriseBot()

# ==========================================
# MODÜL 1: GENEL & ARAÇLAR (7 Komut)
# ==========================================

@bot.command(name="yardim")
async def yardim(ctx: commands.Context):
    embed = discord.Embed(
        title="🤖 Sistem Kontrol Arayüzü",
        description="Aşağıda listelenen tüm komut setleri anlık olarak kullanıma hazırdır.",
        color=discord.Color.from_rgb(99, 102, 241) # Indigo v4
    )
    embed.add_field(name="🛠️ Araçlar", value="`!ping`, `!sunucu`, `!profil`, `!avatar`, `!istatistik`, `!davet`", inline=False)
    embed.add_field(name="🎲 Eğlence & Şans", value="`!zar`, `!yazitura`, `!roll [min] [max]`, `!secim [a,b,c]`, `!sifre [uzunluk]`", inline=False)
    embed.add_field(name="🛡️ Moderasyon", value="`!temizle [miktar]`, `!sustur [@üye] [süre]`, `!susturac [@üye]`, `!ban [@üye]`, `!kick [@üye]`, `!kullaniciadi [@üye] [yeni_isim]`", inline=False)
    embed.add_field(name="🔤 Metin İşlemleri", value="`!say [mesaj]`, `!ters [metin]`, `!buyuk [metin]`, `!kucuk [metin]`", inline=False)
    embed.set_footer(text=f"Talep Sahibi: {ctx.author.name} • Toplam 22 Aktif Komut", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="ping")
async def ping(ctx: commands.Context):
    await ctx.send(f"🏓 **Pong!** Gateway Gecikmesi: `{round(bot.latency * 1000)}ms`")

@bot.command(name="sunucu")
async def sunucu(ctx: commands.Context):
    guild = ctx.guild
    if not guild: return
    embed = discord.Embed(title=f"📊 Sunucu Bilgileri: {guild.name}", color=discord.Color.from_rgb(30, 41, 59)) # Slate 800
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Sunucu Sahibi ID", value=f"`{guild.owner_id}`", inline=True)
    embed.add_field(name="Üye Sayısı", value=f"👥 `{guild.member_count}`", inline=True)
    embed.add_field(name="Rol Sayısı", value=f"🎭 `{len(guild.roles)}`", inline=True)
    embed.add_field(name="Oluşturulma Tarihi", value=f"📅 `{guild.created_at.strftime('%d/%m/%Y')}`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="profil")
async def profil(ctx: commands.Context, üye: Optional[discord.Member] = None):
    target = üye or ctx.author
    embed = discord.Embed(title=f"👤 Profil Kartı: {target.display_name}", color=target.color)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="Hesap ID", value=f"`{target.id}`", inline=False)
    embed.add_field(name="Sunucuya Katılım", value=f"`{target.joined_at.strftime('%d/%m/%Y %H:%M') if target.joined_at else 'Bilinmiyor'}`", inline=True)
    embed.add_field(name="Discord Kayıt", value=f"`{target.created_at.strftime('%d/%m/%Y %H:%M')}`", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="avatar")
async def avatar(ctx: commands.Context, üye: Optional[discord.Member] = None):
    target = üye or ctx.author
    await ctx.send(f"🖼️ **{target.display_name}** kullanıcısının avatarı:\n{target.display_avatar.with_size(1024).url}")

@bot.command(name="istatistik")
async def istatistik(ctx: commands.Context):
    uptime = datetime.datetime.now(datetime.timezone.utc) - bot.launch_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    embed = discord.Embed(title="⚙️ Altyapı Operasyonel Durumu", color=discord.Color.from_rgb(16, 185, 129))
    embed.add_field(name="Çalışma Süresi", value=f"`{hours} saat {minutes} dakika {seconds} saniye`", inline=False)
    embed.add_field(name="Bağlı Sunucu", value=f"🌐 `{len(bot.guilds)}`", inline=True)
    embed.add_field(name="Toplam İzlenen Kullanıcı", value=f"👥 `{len(bot.users)}`", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="davet")
async def davet(ctx: commands.Context):
    await ctx.send(f"🔗 Bot Yetkilendirme Linki: https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot")

# ==========================================
# MODÜL 2: EĞLENCE & ŞANS (5 Komut)
# ==========================================

@bot.command(name="zar")
async def zar(ctx: commands.Context):
    await ctx.send(f"🎲 Rastgele zar sonucu: **{random.randint(1, 6)}**")

@bot.command(name="yazitura")
async def yazitura(ctx: commands.Context):
    await ctx.send(f"🪙 Madeni para atıldı: **{random.choice(['Yazı', 'Tura'])}**")

@bot.command(name="roll")
async def roll(ctx: commands.Context, minimum: int = 1, maksimum: int = 100):
    if minimum >= maksimum:
        await ctx.send("❌ Hata: Minimum değer maksimum değerden büyük veya eşit olamaz.")
        return
    await ctx.send(f"🔢 [{minimum} - {maksimum}] aralığında gelen sayı: **{random.randint(minimum, maksimum)}**")

@bot.command(name="secim")
async def secim(ctx: commands.Context, *, seçenekler: str):
    liste = [item.strip() for item in seçenekler.split(",") if item.strip()]
    if len(liste) < 2:
        await ctx.send("❌ Hata: Lütfen virgülle ayırarak en az 2 seçenek belirtin. Örn: `!secim Elma, Armut`")
        return
    await ctx.send(f"🤔 Karar mekanizması seçti: **{random.choice(liste)}**")

@bot.command(name="sifre")
async def sifre(ctx: commands.Context, uzunluk: int = 12):
    if uzunluk < 6 or uzunluk > 32:
        await ctx.send("❌ Güvenlik hatası: Şifre uzunluğu en az 6, en fazla 32 olmalıdır.")
        return
    karakterler = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    üretilen = "".join(random.choice(karakterler) for _ in range(uzunluk))
    try:
        await ctx.author.send(f"🔒 İstediğin rastgele şifre üretildi: `{üretilen}`")
        await ctx.send("📥 Şifreniz güvenlik sebebiyle DM kutunuza gönderildi.")
    except discord.Forbidden:
        await ctx.send("❌ DM kutunuz kapalı olduğu için şifreyi iletemedim.")

# ==========================================
# MODÜL 3: MODERASYON (6 Komut)
# ==========================================

@bot.command(name="temizle")
@commands.has_permissions(manage_messages=True)
async def temizle(ctx: commands.Context, miktar: int = 10):
    if miktar < 1 or miktar > 100:
        await ctx.send("❌ Sınır Aşımı: Tek seferde 1 ila 100 adet mesaj temizlenebilir.")
        return
    silinen = await ctx.channel.purge(limit=miktar + 1)
    msg = await ctx.send(f"🗑️ `{len(silinen) - 1}` adet mesaj temizlendi.")
    await asyncio.sleep(3)
    try: await msg.delete()
    except discord.NotFound: pass

@bot.command(name="sustur")
@commands.has_permissions(moderate_members=True)
async def sustur(ctx: commands.Context, üye: discord.Member, dakika: int = 10):
    süre = datetime.timedelta(minutes=dakika)
    await üye.timeout(süre, reason=f"Mod: {ctx.author.name} tarafından susturuldu.")
    await ctx.send(f"🤫 **{üye.display_name}**, {dakika} dakika boyunca susturuldu.")

@bot.command(name="susturac")
@commands.has_permissions(moderate_members=True)
async def susturac(ctx: commands.Context, üye: discord.Member):
    await üye.timeout(None, reason=f"Mod: {ctx.author.name} susturmayı kaldırdı.")
    await ctx.send(f"🔊 **{üye.display_name}** üzerindeki susturma kaldırıldı.")

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx: commands.Context, üye: discord.Member, *, neden: str = "Belirtilmedi"):
    await üye.ban(reason=neden)
    await ctx.send(f"💥 **{üye.display_name}** sunucudan banlandı. Gerekçe: `{neden}`")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx: commands.Context, üye: discord.Member, *, neden: str = "Belirtilmedi"):
    await üye.kick(reason=neden)
    await ctx.send(f"👢 **{üye.display_name}** sunucudan atıldı. Gerekçe: `{neden}`")

@bot.command(name="kullaniciadi")
@commands.has_permissions(manage_nicknames=True)
async def kullaniciadi(ctx: commands.Context, üye: discord.Member, *, yeni_isim: str):
    await üye.edit(nick=yeni_isim)
    await ctx.send(f"📝 **{üye.name}** kullanıcısının takma adı `{yeni_isim}` olarak değiştirildi.")

# ==========================================
# MODÜL 4: METİN İŞLEMLERİ (4 Komut)
# ==========================================

@bot.command(name="say")
async def say(ctx: commands.Context, *, mesaj: str):
    try: await ctx.message.delete()
    except discord.Forbidden: pass
    await ctx.send(mesaj)

@bot.command(name="ters")
async def ters(ctx: commands.Context, *, metin: str):
    await ctx.send(metin[::-1])

@bot.command(name="buyuk")
async def buyuk(ctx: commands.Context, *, metin: str):
    await ctx.send(metin.upper())

@bot.command(name="kucuk")
async def kucuk(ctx: commands.Context, *, metin: str):
    await ctx.send(metin.lower())

# ==========================================
# ANA BAŞLATICI
# ==========================================
def main():
    if not TOKEN:
        logger.critical("Hata: Geçerli bir token bulunamadı.")
        sys.exit(1)
    try:
        bot.run(TOKEN, reconnect=True)
    except discord.LoginFailure:
        logger.critical("Hata: Sağlanan Discord tokenı geçersiz veya Discord tarafından iptal edilmiş.")
        sys.exit(1)

if __name__ == "__main__":
    main()
