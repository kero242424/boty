import discord
from discord.ext import commands
import asyncio
import random
import datetime

# Senin emanet token
TOKEN = 'MTUyNzMyMTQxNjA4NzYzODAxNg.GUXMHz.hLeEQn5LI-LtCLrs8Yh5P2H6iKnyMonb5Mqdgc'

# İzinleri ayarlıyoruz
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

kelimeler = ['kaos', 'af', 'patates', 'cezami_kaldir', 'zindan']

@bot.event
async def on_ready():
    print(f'🔥 Cezacı Bot {bot.user.name} aktif! Yılan operasyona hazır.')

@bot.command()
async def ceza(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Kimi cezalandırıyoruz aga? Birini etiketlemen lazım. (Örn: !ceza @Ahmet)")
        return

    rastgele_kelime = random.choice(kelimeler)
    
    await ctx.send(f"🚨 {member.mention} **CEZALANDIRILDIN!** 🚨\nSadece **23 saniyen** var. Hemen ayrı ayrı mesajlarla tam **10 kere** `{rastgele_kelime}` yazman lazım. Süren başladı!")

    # Hedefin doğru kelimeyi yazdığını kontrol eden filtre
    def check(m):
        return m.author == member and m.channel == ctx.channel and m.content.lower() == rastgele_kelime

    toplanan_mesaj_sayisi = 0
    # 23 saniyelik bir zamanlayıcı kuruyoruz
    bitis_zamani = asyncio.get_event_loop().time() + 23.0

    while toplanan_mesaj_sayisi < 10:
        kalan_sure = bitis_zamani - asyncio.get_event_loop().time()
        
        # Süre bittiyse döngüyü kır
        if kalan_sure <= 0:
            break
            
        try:
            # Belirlenen süre içinde mesaj bekle
            msg = await bot.wait_for('message', check=check, timeout=kalan_sure)
            await msg.add_reaction('✅')
            toplanan_mesaj_sayisi += 1
        except asyncio.TimeoutError:
            # Süre dolarsa döngüyü kır
            break

    # Sonuç kısmı
    if toplanan_mesaj_sayisi >= 10:
        await ctx.send(f"Helal lan {member.mention}, klavyeyi parçaladın ama yırttın. Cezan iptal edildi!")
    else:
        await ctx.send(f"⏱️ Süre doldu! Sadece {toplanan_mesaj_sayisi} kere yazabildin. Acımam aga, yedin timeoutu! 🔨")
        
        try:
            # 1 dakikalık (60 saniye) timeout atıyoruz
            sure = datetime.timedelta(minutes=1)
            await member.timeout(sure, reason="23 saniye kuralında çuvalladı.")
            await ctx.send(f"{member.mention} 1 dakikalığına kafasını dinlemeye gönderildi. Sıradaki gelsin...")
        except discord.errors.Forbidden:
            await ctx.send("Hata: Aga bu adamın yetkisi benden yüksek veya bende 'Üyelere Zaman Aşımı Uygula' yetkisi yok! Çarpamadım.")

bot.run(TOKEN)
