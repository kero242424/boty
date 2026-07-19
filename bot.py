import os
import sys
import random
import asyncio
import logging
import discord
from discord.ext import commands

# GitHub Actions loglarında temiz görünmesi için loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('DiscordBot')

# Doğrudan koda gömdüğümüz burner token
TOKEN = "MTUyNzMyMTQxNjA4NzYzODAxNg.GUXMHz.hLeEQn5LI-LtCLrs8Yh5P2H6iKnyMonb5Mqdgc"

class MyBot(commands.Bot):
    def __init__(self):
        # Modern Discord API v10 için gerekli yetkileri (intents) tanımlıyoruz
        intents = discord.Intents.default()
        intents.message_content = True  # Mesaj içeriklerini okuyabilmek için şart
        intents.members = True          # Sunucu üyelerinin bilgilerini çekebilmek için
        
        super().__init__(
            command_prefix="!", 
            intents=intents,
            help_command=None # Varsayılan çirkin help komutunu deaktif ediyoruz
        )
        
        # GitHub Actions 6 saatlik limiti aşmasın diye opsiyonel görev modu
        # Eğer ortam değişkenlerinde RUN_ONCE=true verilirse bot tek bir iş yapıp kapanır.
        self.run_once = os.getenv("RUN_ONCE", "false").lower() == "true"

    async def on_ready(self) -> None:
        """Bot Discord sunucularına başarıyla bağlandığında tetiklenen tetikleyici."""
        logger.info(f"Bot aktif! Giriş yapılan hesap: {self.user} (ID: {self.user.id})")
        
        # Botun durum (activity) yazısını ayarlıyoruz
        await self.change_presence(activity=discord.Game(name="!yardim | v1.0.0"))
        
        # GitHub Actions üzerinde zamanlanmış görev tetiklendiyse çalışacak blok
        if self.run_once:
            logger.info("GitHub Actions zamanlanmış görev modu aktif. Görev çalıştırılıyor...")
            await self.execute_automated_task()
            logger.info("Görev tamamlandı. Bot kapatılıyor.")
            await self.close()

    async def execute_automated_task(self) -> None:
        """GitHub Actions cron modu için buraya otomatik yaptırmak istediğin işleri yazabilirsin."""
        logger.info("Otomatik rutin başarıyla tamamlandı.")

    async def on_command_error(self, ctx: commands.Context, error: commands.errors.CommandError) -> None:
        """Komut çalışırken hata oluşursa botun çökmesini engelleyen global yakalayıcı."""
        if isinstance(error, commands.CommandNotFound):
            return # Tanımsız komutlarda logları kirletmemek için sessizce geçiyoruz
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Bu komutu kullanmak için gerekli yetkilere sahip değilsin!")
            return
            
        logger.error(f"Hata Oluştu ({ctx.command}): {str(error)}")
        await ctx.send(f"⚠️ Bir hata meydana geldi: `{str(error)}`")

# Bot nesnesini türetiyoruz
bot = MyBot()

# --- KOMUTLAR (COMMANDS) ---

@bot.command(name="yardim")
async def yardim(ctx: commands.Context):
    """Kullanıcılara botun kullanabileceği tüm komutları gösteren modern Embed arayüzü."""
    embed = discord.Embed(
        title="🤖 Bot Komut Paneli",
        description="Botta kullanabileceğin aktif komutların listesi aşağıdadır:",
        color=discord.Color.indigo()
    )
    embed.add_field(name="`!ping`", value="Botun anlık gecikme (latency) süresini ölçer.", inline=False)
    embed.add_field(name="`!zar`", value="1 ile 6 arasında rastgele bir zar atar.", inline=False)
    embed.add_field(name="`!yazitura`", value="Yazı mı tura mı? Şansını dene.", inline=False)
    embed.add_field(name="`!temizle [sayı]`", value="Belirtilen miktarda mesajı kanaldan siler (Yönetici yetkisi ister).", inline=False)
    embed.add_field(name="`!sunucu`", value="Bulunduğunuz sunucu hakkında teknik bilgi verir.", inline=False)
    
    embed.set_footer(text=f"Talep eden: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="ping")
async def ping(ctx: commands.Context):
    """Gecikme süresini milisaniye cinsinden hesaplar."""
    latency_ms = round(bot.latency * 1000)
    await ctx.send(f"🏓 **Pong!** Gecikme Süresi: `{latency_ms}ms`")

@bot.command(name="zar")
async def zar(ctx: commands.Context):
    """Rastgele zar atma mantığı."""
    sonuc = random.randint(1, 6)
    await ctx.send(f"🎲 Zarı attın! Gelen sayı: **{sonuc}**")

@bot.command(name="yazitura")
async def yazitura(ctx: commands.Context):
    """Yazı tura algoritması."""
    sonuc = random.choice(["Yazı", "Tura"])
    await ctx.send(f"🪙 Para havaya atıldı ve... **{sonuc}** geldi!")

@bot.command(name="temizle")
@commands.has_permissions(manage_messages=True)
async def temizle(ctx: commands.Context, miktar: int = 5):
    """Kanaldaki mesajları toplu silen moderasyon komutu."""
    if miktar < 1 or miktar > 100:
        await ctx.send("❌ Tek seferde en az 1, en fazla 100 mesaj silebilirsin.")
        return
    
    # Komutun kendisini de silmesi için miktar+1 yapıyoruz
    silinen = await ctx.channel.purge(limit=miktar + 1)
    # Bilgi mesajı gönderip 3 saniye sonra otomatik siliyoruz
    onay_mesaji = await ctx.send(f"🗑️ `{len(silinen) - 1}` adet mesaj başarıyla temizlendi.")
    await asyncio.sleep(3)
    await onay_mesaji.delete()

@bot.command(name="sunucu")
async def sunucu(ctx: commands.Context):
    """Sunucu istatistiklerini derleyen embed arayüzü."""
    guild = ctx.guild
    if not guild:
        return

    embed = discord.Embed(
        title=f"📊 {guild.name} Sunucu Bilgileri",
        color=discord.Color.dark_slate_grey()
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        
    embed.add_field(name="Sunucu Sahibi", value=f"{guild.owner}", inline=True)
    embed.add_field(name="Üye Sayısı", value=f"{guild.member_count}", inline=True)
    embed.add_field(name="Oluşturulma Tarihi", value=f"{guild.created_at.strftime('%d/%m/%Y')}", inline=False)
    
    await ctx.send(embed=embed)

def main():
    """Botu başlatan ana giriş fonksiyonu."""
    if not TOKEN or TOKEN == "BURAYA_TOKEN_GELECEK":
        logger.critical("Hata: Geçerli bir Discord Token bulunamadı!")
        sys.exit(1)
        
    try:
        bot.run(TOKEN, reconnect=True)
    except discord.LoginFailure:
        logger.critical("Hata: Girdiğin Discord Tokenı geçersiz veya patlamış!")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Bot başlatılırken beklenmedik hata oluştu: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
