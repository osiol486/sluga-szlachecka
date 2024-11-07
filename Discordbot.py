import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import re
import logging
from colorama import Fore, Style



# Załaduj zmienne środowiskowe
load_dotenv(dotenv_path='token.env')
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True
intents.members = True

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format logu z datą, godziną i poziomem logowania
    datefmt='%Y-%m-%d %H:%M:%S'  # Format daty i godziny
)

# Ustawienie poziomu logowania dla loggera discord.py
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.WARNING)  # Możesz ustawić na WARNING lub ERROR, aby ograniczyć ilość logów

# Utworzenie instancji bota
bot = commands.Bot(command_prefix='!', intents=intents)

# Dodanie filtra, aby zapobiegać duplikatom logów
class NoDuplicateFilter(logging.Filter):
    def __init__(self):
        self.logged_messages = set()

    def filter(self, record):
        if record.msg in self.logged_messages:
            return False
        self.logged_messages.add(record.msg)
        return True

# Dodanie filtra do loggera głównego
logger = logging.getLogger()
logger.addFilter(NoDuplicateFilter())

@bot.event
async def on_ready():
    print(Fore.GREEN + f'Bot {bot.user.name} został uruchomiony!' + Style.RESET_ALL)
    await load_cogs()

@bot.event
async def on_guild_join(guild):
    # Sprawdź, czy ranga o nazwie "Sługa Szlachecka" już istnieje
    role_exists = discord.utils.get(guild.roles, name="Sługa Szlachecka")
    
    # Jeśli ranga nie istnieje, utwórz ją
    if role_exists is None:
        permissions = discord.Permissions(administrator=True)  # Uprawnienia administratora
        role = await guild.create_role(name="Sługa Szlachecka", permissions=permissions, reason="Bot musi mieć dostęp administracyjny")
        print(f'Ranga "{role.name}" została utworzona.')

        # Przypisz rangę do bota
        bot_member = guild.get_member(bot.user.id)
        if bot_member:
            await bot_member.add_roles(role)
            print(f'Ranga "{role.name}" została przypisana do bota.')
    else:
        # Jeśli ranga istnieje, przypisz ją
        bot_member = guild.get_member(bot.user.id)
        if bot_member and role_exists:
            await bot_member.add_roles(role_exists)
            print(f'Ranga "{role_exists.name}" została przypisana do bota.')

# Kolory dla embedów
EMBED_COLOR = 0xFFEF0A  # żółty

# Funkcja do parsowania czasu (przykład funkcji użytkowej)
def parse_time(time_str):
    match = re.match(r"(\d+)([smhd])", time_str)
    if match:
        value, unit = match.groups()
        value = int(value)
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
    return None

# Funkcja do parsowania czasu w formacie MM:SS (przykład funkcji użytkowej)
def parse_minutes_seconds(time_str):
    match = re.match(r"(\d+):(\d+)", time_str)
    if match:
        minutes, seconds = match.groups()
        return int(minutes) * 60 + int(seconds)
    return None

bot.remove_command('help')


# Załaduj cogs
async def load_cogs():
    await bot.load_extension('cogs.music')  # Załaduj cogs muzyczne z music.py
    await bot.load_extension('cogs.moderation')  # Załaduj cogs moderacyjne z moderation.py
    await bot.load_extension('cogs.information') # Załaduj cogs informacyjne z information.py


# Uruchomienie bota
bot.run(TOKEN)
