import os
import random
import string
import base64
import asyncio
import discord
from discord import app_commands
from cryptography.fernet import Fernet

# ---------------------------------------------------------------------------
# YAPILANDIRMA VE İSTEMCİ BAŞLATMA
# ---------------------------------------------------------------------------

TOKEN = os.getenv("DISCORD_TOKEN")
TARGET_CHANNEL_NAME = "botcage"  # Botun sadece çalışacağı kanal adı

class SecureGenBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Slash komutlarını Discord'a senkronize et
        await self.tree.sync()
        print(f"[{self.user}] Komut ağacı başarıyla senkronize edildi.")

bot = SecureGenBot()

@bot.event
async def on_ready():
    print(f"Sistem Aktif: {bot.user.name} (ID: {bot.user.id})")
    print("--------------------------------------------------")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"#{TARGET_CHANNEL_NAME} | Güvenli Mod"))

# ---------------------------------------------------------------------------
# KANAL KONTROL FİLTRESİ (Sadece #botcage için)
# ---------------------------------------------------------------------------

def is_allowed_channel():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            return True
            
        if interaction.channel.name != TARGET_CHANNEL_NAME:
            await interaction.response.send_message(
                f"❌ Bu botun komutları sadece **#{TARGET_CHANNEL_NAME}** kanalında kullanılabilir! Lütfen oraya geç.", 
                ephemeral=True
            )
            return False
        return True
    return app_commands.check(predicate)

# ---------------------------------------------------------------------------
# YARDIMCI MATEMATİKSEL & KRİPTOGRAFİK FONKSİYONLAR
# ---------------------------------------------------------------------------

def calculate_entropy(length: int, pool_size: int) -> float:
    if length <= 0 or pool_size <= 0:
        return 0.0
    import math
    return length * math.log2(pool_size)

def get_entropy_rating(entropy: float) -> tuple[str, str]:
    if entropy < 28:
        return "Çok Zayıf (Kırılabilir)", "🔴"
    elif entropy < 36:
        return "Zayıf", "🟠"
    elif entropy < 60:
        return "Orta / Kabul Edilebilir", "🟡"
    elif entropy < 80:
        return "Güçlü", "🟢"
    else:
        return "Askeri Düzey / Mükemmel", "🟣"

# ---------------------------------------------------------------------------
# MODAL: Güvenli Not / Şifreleme Paneli
# ---------------------------------------------------------------------------

class SecretModal(discord.ui.Modal, title="🔒 Güvenli Metin / Şifre Saklayıcı"):
    secret_input = discord.ui.TextInput(
        label="Şifrelenecek Gizli Metin",
        style=discord.TextStyle.paragraph,
        placeholder="Buraya başkalarının görmesini istemediğin metni yaz...",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        key = Fernet.generate_key()
        f = Fernet(key)
        
        encoded_text = self.secret_input.value.encode('utf-8')
        encrypted_text = f.encrypt(encoded_text).decode('utf-8')
        
        embed = discord.Embed(
            title="🔐 Metin Başarıyla Şifrelendi",
            description="Metniniz Fernet algoritması ile koruma altına alındı.",
            color=discord.Color.dark_embed()
        )
        embed.add_field(name="Şifrelenmiş Veri (Ciphertext)", value=f"```{encrypted_text}```", inline=False)
        embed.add_field(name="Çözme Anahtarı (Key)", value=f"```{key.decode('utf-8')}```", inline=False)
        embed.set_footer(text="Bu anahtarı kaybederseniz metne tekrar ulaşamazsınız!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ---------------------------------------------------------------------------
# SLASH KOMUTLARI
# ---------------------------------------------------------------------------

@bot.tree.command(name="sifre", description="Özelleştirilebilir, yüksek entropili güvenli bir şifre üretir.")
@app_commands.describe(
    uzunluk="Şifre uzunluğu (Varsayılan: 16, Maks: 128)",
    rakam="Rakamlar (0-9) dahil edilsin mi?",
    sembol="Özel karakterler (!@#$...) dahil edilsin mi?",
    benzersiz="Karıştırılması muhtemel karakterler (I, l, O, 0) hariç tutulsun mu?"
)
@is_allowed_channel()
async def sifre(
    interaction: discord.Interaction, 
    uzunluk: int = 16, 
    rakam: bool = True, 
    sembol: bool = True,
    benzersiz: bool = False
):
    if uzunluk < 4 or uzunluk > 128:
        await interaction.response.send_message("❌ Uzunluk en az **4**, en fazla **128** karakter olabilir.", ephemeral=True)
        return

    chars = string.ascii_letters
    pool_size = len(string.ascii_lowercase) + len(string.ascii_uppercase)

    if rakam:
        chars += string.digits
        pool_size += 10
    if sembol:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        pool_size += 28
    
    if benzersiz:
        ambiguous = "IlO01"
        chars = "".join(c for c in chars if c not in ambiguous)

    rnd = random.SystemRandom()
    password = "".join(rnd.choice(chars) for _ in range(uzunluk))

    entropy = calculate_entropy(uzunluk, len(chars))
    rating, emoji = get_entropy_rating(entropy)

    embed = discord.Embed(title="🛡️ Şifre Üreticisi - Sonuç", color=discord.Color.blurple())
    embed.add_field(name="Oluşturulan Parola", value=f"```{password}```", inline=False)
    embed.add_field(name="Karakter Uzunluğu", value=f"`{uzunluk} karakter`", inline=True)
    embed.add_field(name="Güvenlik Skoru", value=f"{emoji} `{rating}`", inline=True)
    embed.add_field(name="Entropi", value=f"`{entropy:.1f} bit`", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


@app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
@bot.tree.command(name="passphrase", description="Okunması kolay, kelime tabanlı güvenli bir parola cümlesi üretir.")
@app_commands.describe(kelime_sayisi="Kelime sayısı (Varsayılan: 4, Maks: 10)")
@is_allowed_channel()
async def passphrase(interaction: discord.Interaction, kelime_sayisi: int = 4):
    if kelime_sayisi < 3 or kelime_sayisi > 10:
        await interaction.response.send_message("❌ Kelime sayısı 3 ile 10 arasında olmalıdır.", ephemeral=True)
        return

    word_list = [
        "yildiz", "gezegen", "bilgisayar", "kahve", "kitap", "orman", "deniz", 
        "ruzgar", "bulut", "kalem", "telefon", "muzik", "sanat", "yaprak", 
        "kopru", "liman", "marti", "toprak", "yazilim", "donanim", "atlas", 
        "pusula", "mercan", "galaksi", "safir", "volkan", "gokyuzu", "ritim"
    ]
    
    rnd = random.SystemRandom()
    selected_words = [rnd.choice(word_list) for _ in range(kelime_sayisi)]
    
    separator = rnd.choice(["-", "_", ".", ""])
    formatted_words = []
    for w in selected_words:
        if rnd.random() > 0.5:
            w = w.capitalize()
        if rnd.random() > 0.7:
            w += str(rnd.randint(10, 99))
        formatted_words.append(w)

    final_passphrase = separator.join(formatted_words)
    
    embed = discord.Embed(title="🧠 Passphrase (Parola Cümlesi)", color=discord.Color.green())
    embed.add_field(name="Cümle", value=f"```{final_passphrase}```", inline=False)
    embed.add_field(name="Bilgi", value="Hatırlaması kolay, kaba kuvvet saldırılarına karşı son derece dirençlidir.", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="pin", description="Hızlı kullanım için sayısal bir PIN kodu üretir.")
@app_commands.describe(hane="PIN uzunluğu (Varsayılan: 4, Maks: 16)")
@is_allowed_channel()
async def pin(interaction: discord.Interaction, hane: int = 4):
    if hane < 3 or hane > 16:
        await interaction.response.send_message("❌ PIN uzunluğu 3 ile 16 hane arasında olmalıdır.", ephemeral=True)
        return

    rnd = random.SystemRandom()
    pin_code = "".join(rnd.choice(string.digits) for _ in range(hane))

    embed = discord.Embed(title="🔢 Güvenli PIN Kodu", color=discord.Color.gold())
    embed.add_field(name="PIN", value=f"```{pin_code}```", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="sifrele", description="Bir metni şifreli formata dönüştürür (Açılır panel açar).")
@is_allowed_channel()
async def sifrele(interaction: discord.Interaction):
    await interaction.response.send_modal(SecretModal())


@bot.tree.command(name="yardim", description="Botun komutları ve özellikleri hakkında bilgi verir.")
@is_allowed_channel()
async def yardim(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 SecureGen Bot - Yardım Menüsü",
        description=f"Bu botun tüm komutları yalnızca **#{TARGET_CHANNEL_NAME}** kanalında çalışacak şekilde yapılandırılmıştır.",
        color=discord.Color.dark_theme()
    )
    embed.add_field(
        name="🛠️ Komutlar",
        value=(
            "**/sifre** - Özelleştirilebilir güçlü şifre üretir.\n"
            "**/passphrase** - Kelime tabanlı, akılda kalıcı parola cümlesi üretir.\n"
            "**/pin** - Sayısal PIN kodu üretir.\n"
            "**/sifrele** - Hassas verileriniz için şifreli metin bloğu oluşturur."
        ),
        inline=False
    )
    embed.set_footer(text="Tüm şifre üretim işlemleri gizli (ephemeral) olarak yürütülür.")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@sifre.error
@passphrase.error
@pin.error
async def command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"⏳ Bu komut bekleme süresindedir. Lütfen `{error.retry_after:.1f}` saniye sonra tekrar deneyin.", ephemeral=True)
    else:
        pass

# ---------------------------------------------------------------------------
# ÇALIŞTIRMA
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not TOKEN:
        print("HATA: DISCORD_TOKEN ortam değişkeni bulunamadı!")
    else:
        bot.run(TOKEN)
