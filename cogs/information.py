import discord
from discord.ext import commands
import re
import asyncio
import logging


# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format logu z datą, godziną i poziomem logowania
    datefmt='%Y-%m-%d %H:%M:%S'  # Format daty i godziny
)


# Kolor embedu
EMBED_COLOR = 0x3498DB  # niebieski

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Komenda wyświetlania dostępnych komend
    @commands.command(name='pomoc', aliases=['help'], help='Wyświetl listę dostępnych komend.')
    async def pomoc(self, ctx):
        embed = discord.Embed(title="Lista dostępnych komend", description="Poniżej znajduje się lista dostępnych komend i ich opis:", color=EMBED_COLOR)

        commands_list = [
            {"name": "!play [nazwa utworu / URL]", "aliases": "p", "description": "Odtwórz muzykę z YouTube."},
            {"name": "!skip", "aliases": "s", "description": "Przewiń do następnej piosenki w kolejce."},
            {"name": "!loop", "aliases": None, "description": "Zapętlaj aktualnie odtwarzaną piosenkę."},
            {"name": "!loopqueue", "aliases": "lq", "description": "Zapętlaj kolejkę."},
            {"name": "!stop", "aliases": "pause", "description": "Wstrzymaj odtwarzanie muzyki."},
            {"name": "!resume", "aliases": None, "description": "Wznów odtwarzanie muzyki."},
            {"name": "!disconnect", "aliases": "dc", "description": "Rozłącz bota z kanału głosowego."},
            {"name": "!queue", "aliases": "q", "description": "Wyświetl listę piosenek w kolejce."},
            {"name": "!now_playing", "aliases": "np", "description": "Wyświetl aktualnie odtwarzaną piosenkę."},
            {"name": "!info", "aliases": None, "description": "Wyświetl informacje o bocie."}
        ]

        for command in commands_list:
            aliases = f" (alias: {command['aliases']})" if command['aliases'] else ""
            embed.add_field(name=command["name"] + aliases, value=command["description"], inline=False)

        await ctx.send(embed=embed)

    # Komenda wyświetlania informacji o bocie
    @commands.command(name='info', help='Wyświetl informacje o bocie.')
    async def info(self, ctx):
        # Pobierz URL do awatara bota oraz jego nazwę
        bot_avatar_url = self.bot.user.avatar.url
        bot_name = self.bot.user.name

        # Stwórz embed z informacjami o bocie
        embed = discord.Embed(
            title=f"Informacje o bocie: {bot_name}",  # Dodaj imię bota w tytule
            description="Bot stworzony przez ChatGPT, zaprojektowany do zarządzania muzyką oraz serwerem Discord. Póki co ma podstawowe funkcje, ale planuje go jakoś rozbudować.",
            color=0xA8E6CF  # Możesz ustawić swój kolor lub użyć zmiennej EMBED_COLOR
        )
        embed.add_field(name="Twórca", value="Bartłomiej Rogala / discord: osiol486", inline=False)
        embed.add_field(name="Repozytorium GitHub", value="[Kliknij tutaj](https://github.com/osiol486/discordbot)", inline=False)
        
        # Ustawienie awatara bota jako miniatury w embede
        embed.set_thumbnail(url=bot_avatar_url)

        # Dodanie stopki do embeda
        embed.set_footer(text="Dzięki za korzystanie z bota!")

        # Wysłanie embeda
        await ctx.send(embed=embed)

# Funkcja setup, która pozwala zarejestrować cogs w bota
async def setup(bot):
    await bot.add_cog(Information(bot))
