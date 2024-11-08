import os
import sys  # Import sys, aby użyć sys.stderr
import discord
from discord.ext import commands
from dotenv import load_dotenv
from colorama import init, Fore, Style
from loguru import logger
import emoji
from utils import parse_time, parse_minutes_seconds
from logging_handlers.logger_config import configure_logger

# Konfiguracja loggera
configure_logger()

# Załaduj zmienne środowiskowe
load_dotenv(dotenv_path='token.env')
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True
intents.members = True

# Konfiguracja loggera Loguru
init(autoreset=True)  # Inicjalizacja colorama z automatycznym resetowaniem kolorów

logger.remove()  # Usuń domyślny handler

# Utworzenie instancji bota
bot = commands.Bot(command_prefix='!', intents=intents)

def guild_log_prefix(ctx):
    """Tworzy prefiks logów zawierający nazwę i ID serwera."""
    guild_name = ctx.guild.name if ctx.guild else "Brak serwera"
    guild_id = ctx.guild.id if ctx.guild else "Brak ID"
    return f"[{guild_name} ({guild_id})]"

@bot.event
async def on_ready():
    logger.success(f'Bot {bot.user.name} został uruchomiony poprawnie!')
    await bot.load_extension('cogs.music')  # Załaduj cogs muzyczne z music.py
    await bot.load_extension('cogs.moderation')  # Załaduj cogs moderacyjne z moderation.py
    await bot.load_extension('cogs.information') # Załaduj cogs informacyjne z information.py

@bot.event
async def on_guild_join(guild):
    # Sprawdź, czy ranga o nazwie "Sługa Szlachecka" już istnieje
    role_exists = discord.utils.get(guild.roles, name="Sługa Szlachecka")
    
    # Jeśli ranga nie istnieje, utwórz ją
    if role_exists is None:
        permissions = discord.Permissions(administrator=True)  # Uprawnienia administratora
        role = await guild.create_role(name="Sługa Szlachecka", permissions=permissions, reason="Bot musi mieć dostęp administracyjny")
        logger.debug(f'Ranga "{role.name}" została utworzona na serwerze {guild.name} (ID: {guild.id}).')

        # Przypisz rangę do bota
        bot_member = guild.get_member(bot.user.id)
        if bot_member:
            await bot_member.add_roles(role)
            logger.debug(f'Ranga "{role.name}" została przypisana do bota na serwerze {guild.name} (ID: {guild.id}).')
    else:
        # Jeśli ranga istnieje, przypisz ją
        bot_member = guild.get_member(bot.user.id)
        if bot_member and role_exists:
            await bot_member.add_roles(role_exists)
            logger.debug(f'Ranga "{role_exists.name}" została przypisana do bota na serwerze {guild.name} (ID: {guild.id}).')

# Przykład dodania logów do komend
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Sprawdź, czy wiadomość zaczyna się od prefixu bota i nie jest komendą
    if message.content.startswith(bot.command_prefix) and not message.content[len(bot.command_prefix):].split(" ")[0] in bot.all_commands:
        guild_prefix = guild_log_prefix(message)
        logger.debug(f"{guild_prefix} Nie rozpoznano komendy: {message.content}")
        await message.add_reaction("❓")  # Dodaj emoji pytania, gdy komenda nie istnieje
        await message.channel.send("Nie rozpoznano komendy. Użyj !help, aby zobaczyć dostępne komendy.")
    
    # Przekaż obsługę komend do pozostałej części kodu bota
    await bot.process_commands(message)

# Kolory dla embedów
EMBED_COLOR = 0xFFEF0A  # żółty

bot.remove_command('help')

# Uruchomienie bota
bot.run(TOKEN)
