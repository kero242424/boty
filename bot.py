import os
import random
import string
import math
import discord
from discord import app_commands
from cryptography.fernet import Fernet, InvalidToken

TOKEN = os.getenv("DISCORD_TOKEN")
TARGET_CHANNEL_NAME = "botcage"

class SecureGenBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = SecureGenBot()

@bot.event
async def on_ready():
    print(f"Bot aktif: {bot.user.name}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"#{TARGET_CHANNEL_NAME}"))

def is_allowed_channel():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            return True
        if interaction.channel.name != TARGET_CHANNEL_NAME:
            await interaction.response.send_message(
                f"Burada çalışmıyorum, #{TARGET_CHANNEL_NAME} kanalına geç.", 
                ephemeral=True
            )
            return False
        return True
    return app_commands.check(predicate)

def calculate_entropy(length: int, pool_size: int) -> float:
    if length <= 0 or pool_size <= 0:
        return 0.0
    return length * math.log2(pool_size)

def get_entropy_rating(entropy: float) -> tuple[str, str]:
    if entropy < 28:
        return "Çok Zayıf", "🔴"
    elif entropy < 36:
        return "Zayıf", "🟠"
    elif entropy < 60:
        return "Orta", "🟡"
    elif entropy < 80:
        return "Güçlü", "🟢"
    else:
        return "Askeri Düzey", "🟣"

class SecretModal(discord.ui.Modal, title="Gizli Metin Şifreleyici"):
    secret_input = discord.ui.TextInput(
        label="Metin",
        style=discord.TextStyle.paragraph,
        placeholder="Şifrelenecek metni buraya yaz...",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        key = Fernet.generate_key()
        f = Fernet(key)
        encrypted = f.encrypt(self.secret_input.value.encode('utf-8')).decode('utf-8')
        
        embed = discord.Embed(title="Şifrelendi", color=0x2b2d31)
        embed.add_field(name="Ciphertext", value=f"```{encrypted}```", inline=False)
        embed.add_field(name="Anahtar (Key)", value=f"```{key.decode('utf-8')}```", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="sifre", description="Güvenli şifre üretir.")
@app_commands.describe(uzunluk="Uzunluk (4-128)", rakam="Rakam olsun mu?", sembol="Sembol olsun mu?")
@is_allowed_channel()
async def sifre(interaction: discord.Interaction, uzunluk: int = 16, rakam: bool = True, sembol: bool = True):
    if uzunluk < 4 or uzunluk > 128:
        await interaction.response.send_message("Uzunluk 4 ile 128 arasında olmalı.", ephemeral=True)
        return

    chars = string.ascii_letters
    pool = 52
    if rakam:
        chars += string.digits
        pool += 10
    if sembol:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        pool += 28

    password = "".join(random.SystemRandom().choice(chars) for _ in range(uzunluk))
    entropy = calculate_entropy(uzunluk, pool)
    rating, emoji = get_entropy_rating(entropy)

    embed = discord.Embed(title="Şifre Sonucu", color=0x5865F2)
    embed.add_field(name="Parola", value=f"```{password}```", inline=False)
    embed.add_field(name="Boyut", value=f"{uzunluk}", inline=True)
    embed.add_field(name="Seviye", value=f"{emoji} {rating}", inline=True)
    embed.add_field(name="Entropi", value=f"{entropy:.1f} bit", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="coz", description="Şifrelenmiş metni (ciphertext) anahtarla çözer.")
@app_commands.describe(anahtar="Fernet anahtari", ciphertext="Sifreli metin")
@is_allowed_channel()
async def coz(interaction: discord.Interaction, anahtar: str, ciphertext: str):
    try:
        f = Fernet(anahtar.strip().encode())
        decrypted = f.decrypt(ciphertext.strip().encode()).decode('utf-8')
        
        embed = discord.Embed(title="Çözüldü", color=0x57F287)
        embed.add_field(name="Orijinal Metin", value=f"```{decrypted}```", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except InvalidToken:
        await interaction.response.send_message("Anahtar veya ciphertext hatalı!", ephemeral=True)
    except Exception:
        await interaction.response.send_message("Bir hata oluştu, verileri kontrol et.", ephemeral=True)

@bot.tree.command(name="sifrele", description="Metni şifreler.")
@is_allowed_channel()
async def sifrele(interaction: discord.Interaction):
    await interaction.response.send_modal(SecretModal())

@bot.tree.command(name="yardim", description="Komutları gösterir.")
@is_allowed_channel()
async def yardim(interaction: discord.Interaction):
    embed = discord.Embed(title="Komutlar", description="/sifre, /coz, /sifrele", color=0x2b2d31)
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
