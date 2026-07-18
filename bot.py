import discord
from discord.ext import commands
import asyncio
import random
import datetime

# Senin emanet token
TOKEN = 'MTUyNzMyMTQxNjA4NzYzODAxNg.GUXMHz.hLeEQn5LI-LtCLrs8Yh5P2H6iKnyMonb5Mqdgc'

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

    def check(m):
        return m.author == member and m.channel == ctx.channel and m.content.lower() == rastgele_kelime

    toplanan_mesaj_sayisi = 0
    bitis_zamani = asyncio.get_event_loop().time() + 23.0

    while toplanan_mesaj_sayisi < 10:
        kalan_sure = bitis_zamani - asyncio.get_event_loop().time()
        
        if kalan_sure <= 0:
            break
            
        try:
            msg = await bot.wait_for('message', check=check, timeout=kalan_sure)
            await msg.add_reaction('✅')
            toplanan_mesaj_sayisi += 1
        except asyncio.TimeoutError:
            break

    if toplanan_mesaj_sayisi >= 10:
        await ctx.send(f"Helal lan {member.mention}, klavyeyi parçaladın ama yırttın. Cezan iptal edildi!")
    else:
        await ctx.send(f"⏱️ Süre doldu! Sadece {toplanan_mesaj_sayisi} kere yazabildin. Acımam aga, yedin 28 gün mutesini! 🔨")
        
        try:
            # DİSCORD MAX LİMİTİ: 28 GÜN
            sure = datetime.timedelta(days=28)
            await member.timeout(sure, reason="23 saniye kuralında çuvalladı.")
            await ctx.send(f"💀 {member.mention} tam 28 gün boyunca susturuldu. Kurtarmak isteyen `!af @kisi` yazsın tabi cesareti varsa...")
        except discord.errors.Forbidden:
            await ctx.send("Hata: Aga bu adamın yetkisi benden yüksek! Vuramadım kafasına. Rolümü en üste çek!")

# --- YENİ EKLENEN AF KOMUTU ---
@bot.command()
async def af(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Kimi affediyoruz aga? Birini etiketle de zincirlerini kıralım. (Örn: !af @Ahmet)")
        return
    
    try:
        # Timeout süresini None yaparak cezayı kaldırıyoruz
        await member.timeout(None, reason="Aga affetti.")
        await ctx.send(f"🕊️ {member.mention} şanslısın! <@{ctx.author.id}> sana acıdı ve cezanı kaldırdı. Bi daha bulaşma!")
    except discord.errors.Forbidden:
        await ctx.send("Hata: Bu adamın cezasını kaldırmaya yetkim yetmiyor, rolümü üste al!")

bot.run(TOKEN)
