import os
import random
import string
import hashlib
import discord
from discord.ext import commands
from discord import app_commands

# Botun yetkileri (Intents)
intents = discord.Intents.default()
intents.message_content = True

class SecurityBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Slash komutlarını senkronize et
        await self.tree.sync()
        print(f"[*] Slash komutları senkronize edildi: {self.user}")

    async def on_ready(self):
        print(f"[*] Bot aktif: {self.user.name} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/sifre | Güvenlik Botu"))

bot = SecurityBot()

# --- YARDIMCI FONKSİYONLAR ---
def calculate_entropy_and_time(password: str) -> tuple:
    length = len(password)
    charset_size = 0
    
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)

    if has_lower: charset_size += 26
    if has_upper: charset_size += 26
    if has_digit: charset_size += 10
    if has_symbol: charset_size += 32

    if charset_size == 0 or length == 0:
        return 0, "Çok Zayıf", "Anında"

    # Entropi hesaplama (bit cinsinden)
    import math
    entropy = length * math.log2(charset_size)

    # Kırılma süresi tahmini (Saniyede 10 milyar tahmin varsayımıyla)
    combinations = charset_size ** length
    seconds = combinations / 10_000_000_000

    if seconds < 1:
        time_str = "Anında (< 1 saniye)"
    elif seconds < 60:
        time_str = f"{int(seconds)} saniye"
    elif seconds < 3600:
        time_str = f"{int(seconds / 60)} dakika"
    elif seconds < 86400:
        time_str = f"{int(seconds / 3600)} saat"
    elif seconds < 31536000:
        time_str = f"{int(seconds / 86400)} gün"
    elif seconds < 31536000 * 100:
        time_str = f"{int(seconds / 31536000)} yıl"
    else:
        time_str = "Yüzyıllar / Kırılamaz"

    if entropy < 28:
        strength = "🔴 Çok Zayıf"
    elif entropy < 36:
        strength = "🟠 Zayıf"
    elif entropy < 60:
        strength = "🟡 Orta"
    elif entropy < 80:
        strength = "🟢 Güçlü"
    else:
        strength = "💎 Mükemmel (Askeri Düzey)"

    return entropy, strength, time_str

# --- SLASH KOMUTLARI ---

@bot.tree.command(name="sifre", description="Özelleştirilebilir, yüksek güvenlikli şifre üretir.")
@app_commands.describe(
    uzunluk="Şifre uzunluğu (Varsayılan: 16, Max: 100)",
    ozel_karakter="Özel karakterler (!@#$...) olsun mu?",
    benzerleri_ele="Karıştırılabilecek karakterleri ele (I, l, 1, O, 0)"
)
async def sifre(interaction: discord.Interaction, uzunluk: int = 16, ozel_karakter: bool = True, benzerleri_ele: bool = False):
    if uzunluk < 4 or uzunluk > 100:
        await interaction.response.send_message("❌ Şifre uzunluğu **4 ile 100** arasında olmalıdır.", ephemeral=True)
        return

    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if benzerleri_ele:
        for char in "Il1O0":
            lower = lower.replace(char, "")
            upper = upper.replace(char, "")
            digits = digits.replace(char, "")

    char_pool = lower + upper + digits
    if ozel_karakter:
        char_pool += symbols

    # Her karakter tipinden en az bir tane garantileme
    password_chars = [
        random.choice(lower),
        random.choice(upper),
        random.choice(digits)
    ]
    if ozel_karakter:
        password_chars.append(random.choice(symbols))

    # Kalan uzunluğu tamamla
    for _ in range(uzunluk - len(password_chars)):
        password_chars.append(random.choice(char_pool))

    random.shuffle(password_chars)
    password = "".join(password_chars)

    entropy, strength, crack_time = calculate_entropy_and_time(password)

    embed = discord.Embed(title="🔐 Güvenli Şifre Üretildi", color=discord.Color.blurple())
    embed.add_field(name="🔑 Şifreniz", value=f"```ansi\n\u001b[32m{password}\u001b[0m\n```", inline=False)
    embed.add_field(name="📊 Güvenlik Seviyesi", value=strength, inline=True)
    embed.add_field(name="⏳ Kırılma Süresi", value=crack_time, inline=True)
    embed.add_field(name="📏 Uzunluk", value=str(uzunluk), inline=True)
    embed.set_footer(text="Güvenliğiniz için bu mesajı kimseyle paylaşmayın ve şifreyi kopyaladıktan sonra silin.")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="passphrase", description="Akılda kalıcı ama kırılması çok zor kelime tabanlı şifre üretir.")
@app_commands.describe(kelime_sayisi="Kelime sayısı (Varsayılan: 4, Max: 8)")
async def passphrase(interaction: discord.Interaction, kelime_sayisi: int = 4):
    if kelime_sayisi < 3 or kelime_sayisi > 8:
        await interaction.response.send_message("❌ Kelime sayısı **3 ile 8** arasında olmalıdır.", ephemeral=True)
        return

    kelimeler = [
        "elma", "masa", "bulut", "kalem", "deniz", "kitap", "sehpa", "kahve", 
        "gitar", "orman", "yildiz", "bilgisayar", "yaprak", "telefon", "toprak", 
        "bayrak", "sabun", "bardak", "çiçek", "rüzgar", "mavi", "gece", "güneş"
    ]

    secilenler = [random.choice(kelimeler) for _ in range(kelime_sayisi)]
    # Rastgele bir kelimeyi büyük harf yap ve sonuna sayı/sembol ekle
    secilenler[0] = secilenler[0].capitalize()
    passphrase_str = "-".join(secilenler) + str(random.randint(10, 99)) + "!"

    embed = discord.Embed(title="🌿 Passphrase (Anlamlı Şifre) Üretildi", color=discord.Color.green())
    embed.add_field(name="🔑 Şifreniz", value=f"```ansi\n\u001b[32m{passphrase_str}\u001b[0m\n```", inline=False)
    embed.set_footer(text="Bu şifreyi hatırlamak kolay, kırmak oldukça zordur.")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="guvenlik", description="Bir şifrenin güvenlik gücünü ve kırılma süresini test eder.")
@app_commands.describe(sifre="Test etmek istediğiniz şifre")
async def guvenlik(interaction: discord.Interaction, sifre: str):
    entropy, strength, crack_time = calculate_entropy_and_time(sifre)

    embed = discord.Embed(title="🔍 Şifre Analiz Raporu", color=discord.Color.gold())
    embed.add_field(name="📊 Güvenlik Durumu", value=strength, inline=False)
    embed.add_field(name="⏳ Tahmini Kırılma Süresi", value=crack_time, inline=False)
    embed.add_field(name="📏 Uzunluk", value=f"{len(sifre)} karakter", inline=True)
    embed.add_field(name="🧮 Entropi Değeri", value=f"{entropy:.2f} bit", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="hash", description="Metinleri MD5 veya SHA algoritmalarıyla şifreler (Hash).")
@app_commands.describe(algoritma="Algoritma seçin", metin="Hashlenecek metin")
@app_commands.choices(algoritma=[
    app_commands.Choice(name="MD5", value="md5"),
    app_commands.Choice(name="SHA-256", value="sha256"),
    app_commands.Choice(name="SHA-512", value="sha512")
])
async def hash_komut(interaction: discord.Interaction, algoritma: app_commands.Choice[str], metin: str):
    if algoritma.value == "md5":
        h = hashlib.md5(metin.encode()).hexdigest()
    elif algoritma.value == "sha256":
        h = hashlib.sha256(metin.encode()).hexdigest()
    elif algoritma.value == "sha512":
        h = hashlib.sha512(metin.encode()).hexdigest()

    embed = discord.Embed(title=f"🔒 Hash Sonucu ({algoritma.name})", color=discord.Color.dark_purple())
    embed.add_field(name="Girdi", value=f"`{metin}`", inline=False)
    embed.add_field(name="Çıktı (Hash)", value=f"```code\n{h}\n```", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# Botu Çalıştır
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ HATA: DISCORD_TOKEN çevresel değişkeni (Secret) bulunamadı!")
else:
    bot.run(TOKEN)
