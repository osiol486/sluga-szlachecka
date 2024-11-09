import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from colorama import init, Fore, Style
from loguru import logger
from logger_config import configure_logger, guild_log_prefix
from utils.constants import COMMAND_PREFIX

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

# Utworzenie instancji bota
bot = commands.Bot(COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    logger.success(f'Bot {bot.user.name} został uruchomiony poprawnie!')
    await bot.load_extension('cogs.music')  # Załaduj cogs muzyczne z music.py
    await bot.load_extension('cogs.moderation')  # Załaduj cogs moderacyjne z moderation.py
    await bot.load_extension('cogs.information')  # Załaduj cogs informacyjne z information.py
    await bot.load_extension('cogs.utility')  # Załaduj cogs utility z utility.py
    await bot.load_extension('cogs.antispam')

# Przykład dodania logów do komend
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Sprawdź, czy wiadomość zaczyna się od prefixu bota i nie jest komendą
    if message.content.startswith(bot.command_prefix) and not message.content[len(bot.command_prefix):].split(" ")[0] in bot.all_commands:
        guild_prefix = guild_log_prefix(message)
        logger.debug(f"{guild_prefix} Nie rozpoznano komendy: {message.content}")
        await message.channel.send("Nie rozpoznano komendy. Użyj !komendy, aby zobaczyć dostępne komendy.")
    
    # Przekaż obsługę komend do pozostałej części kodu bota
    await bot.process_commands(message)

bot.remove_command('help')

# Uruchomienie bota
bot.run(TOKEN)
