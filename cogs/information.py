import discord
from discord.ext import commands
import asyncio
import psutil
from utils.constants import EMBED_COLOR_BLUE

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Komenda wyświetlania dostępnych komend
    @commands.command(name='commands', aliases=['komendy'], help='Wyświetl listę wszystkich komend. Użyj: !commands lub !komendy')
    async def commands_list(self, ctx):
        message = await ctx.send(
            "Jakie komendy chcesz? Wybierz odpowiednią emotkę:\n"
            "🔨 Moderacyjne\n"
            "ℹ️ Informacyjne\n"
            "🔧 Narzędzia (Utilities)\n"
            "🎶 Muzyczne"
        )
        
        # Dodanie reakcji do wiadomości
        await message.add_reaction("🔨")
        await message.add_reaction("ℹ️")
        await message.add_reaction("🔧")
        await message.add_reaction("🎶")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["🔨", "ℹ️", "🔧", "🎶"] and reaction.message.id == message.id

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Nie otrzymano odpowiedzi w odpowiednim czasie. Spróbuj ponownie później.")
            return

        # Usunięcie wszystkich reakcji
        await message.clear_reactions()

        if str(reaction.emoji) == "🔨":
            commands_list = [
                {"name": "!kick [użytkownik]", "aliases": None, "description": "Wyrzuć użytkownika z serwera."},
                {"name": "!ban [użytkownik] [czas]", "aliases": None, "description": "Zbanuj użytkownika na określony czas."},
                {"name": "!mute [użytkownik] [czas]", "aliases": None, "description": "Wycisz użytkownika na określony czas."},
                {"name": "!unmute [użytkownik]", "aliases": None, "description": "Odblokuj użytkownika."},
                {"name": "!purge [liczba]", "aliases": None, "description": "Usuń określoną liczbę wiadomości z możliwością użycia filtrów."}
            ]
            title = "Komendy Moderacyjne"
        elif str(reaction.emoji) == "ℹ️":
            commands_list = [
                {"name": "!info", "aliases": None, "description": "Wyświetl informacje o bocie."},
                {"name": "!ping", "aliases": None, "description": "Sprawdź opóźnienie bota."},
                {"name": "!memory", "aliases": None, "description": "Pokaż zużycie pamięci przez bota."},
                {"name": "!commands", "aliases": "komendy", "description": "Wyświetl listę wszystkich komend."}
            ]
            title = "Komendy Informacyjne"
        elif str(reaction.emoji) == "🔧":
            commands_list = [
                {"name": "!avatar [użytkownik]", "aliases": None, "description": "Wyświetla avatar użytkownika."},
                {"name": "!serverinfo", "aliases": None, "description": "Wyświetla informacje o serwerze."},
                {"name": "!userinfo [użytkownik]", "aliases": None, "description": "Wyświetla informacje o użytkowniku."}
            ]
            title = "Komendy Narzędziowe (Utilities)"
        elif str(reaction.emoji) == "🎶":
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
                {"name": "!seek [sekundy lub mm:ss]", "aliases": None, "description": "Przewiń aktualnie odtwarzaną piosenkę do określonego czasu."},
                {"name": "!remove [numer]", "aliases": None, "description": "Usuń utwór z kolejki na podstawie jego numeru."},
                {"name": "!clearqueue", "aliases": "cq", "description": "Wyczyść kolejkę."}
            ]
            title = "Komendy Muzyczne"
        
        # Stworzenie embeda z odpowiednią kategorią komend
        embed = discord.Embed(title=title, description="Poniżej znajduje się lista dostępnych komend i ich opis:", color=EMBED_COLOR_BLUE)
        for command in commands_list:
            aliases = f" (alias: {command['aliases']})" if command['aliases'] else ""
            embed.add_field(name=command["name"] + aliases, value=command["description"], inline=False)

        # Edycja istniejącej wiadomości z nowym embedem
        await message.edit(content=None, embed=embed)


    # Komenda wyświetlania informacji o bocie
    @commands.command(name='info', help='Wyświetl informacje o bocie. Użyj: !info')
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
        embed.add_field(name="Dodatkowe informacje", value="Użyj komendy !commands, aby zobaczyć pełną listę komend, lub !help, aby uzyskać dodatkową pomoc.", inline=False)

        # Ustawienie awatara bota jako miniatury w embede
        embed.set_thumbnail(url=bot_avatar_url)

        # Dodanie stopki do embeda
        embed.set_footer(text="Dzięki za korzystanie z bota!")

        # Wysłanie embeda
        await ctx.send(embed=embed)

    @commands.command(name='ping', help='Sprawdź opóźnienie bota. Użyj: !ping')
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)  # Opóźnienie w milisekundach
        await ctx.send(f"Pong! 🏓 Opóźnienie wynosi: {latency} ms")

    @commands.command(name='memory', help='Pokaż zużycie pamięci przez bota. Użyj: !memory')
    async def memory(self, ctx):
        process = psutil.Process()
        memory_info = process.memory_info()

        used_memory_mb = memory_info.rss / 1024 / 1024  # Zużywana pamięć w MB
        total_memory_mb = psutil.virtual_memory().total / 1024 / 1024  # Całkowita dostępna pamięć w MB

        await ctx.send(f"Bot używa: {used_memory_mb:.2f} MB RAM z dostępnych: {total_memory_mb:.2f} MB RAM")

    # Nowa wersja komendy help
    @commands.command(name='help', help='Wyświetl pomoc dla wszystkich komend. Użyj: !help')
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="Pomoc",
            description="Użyj komendy !commands, aby zobaczyć pełną listę komend, lub !info, aby uzyskać informacje o bocie.",
            color=EMBED_COLOR_BLUE
        )
        embed.add_field(name="Dodatkowe wsparcie", value="W razie problemów możesz skontaktować się z twórcą bota: Bartłomiej Rogala (discord: osiol486)", inline=False)
        await ctx.send(embed=embed)

# Funkcja setup, która pozwala zarejestrować cogs w bota
async def setup(bot):
    await bot.add_cog(Information(bot))
