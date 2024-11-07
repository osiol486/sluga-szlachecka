import os
import sys
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import re
import threading
import json
from colorama import Fore, Style
from loguru import logger
from utils import parse_time, parse_minutes_seconds

# Usuń poprzednią konfigurację loggera
logger.remove()

# Dodaj handler do logowania do pliku bez kolorów
logger.add(
    "bot.log",
    rotation="5 MB",
    retention="7 days",
    level="INFO",
    format="{time} {level} {message}",
    colorize=False
)

# Dodaj handler do logowania w konsoli z kolorami
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
    colorize=True
)

# Funkcja logująca wiadomości na poziomie INFO z kolorem magenta
def pink_log(ctx, message):
    guild_info = f"[{ctx.guild.name} ({ctx.guild.id})]" if ctx.guild else "[Brak serwera]"
    logger.info(f"{guild_info} {message}")

# Folder do przechowywania cache'u
CACHE_FOLDER = "cache"
CACHE_FILE_PATH = os.path.join(CACHE_FOLDER, "music_cache.json")

# Sprawdź, czy folder cache istnieje, jeśli nie - utwórz go
if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)

# Inicjalizacja cache'u dla utworów
try:
    # Odczytaj cache z pliku, jeśli istnieje
    if os.path.exists(CACHE_FILE_PATH):
        with open(CACHE_FILE_PATH, 'r', encoding='utf-8') as f:
            song_cache = json.load(f)
        logger.info('Załadowano cache utworów.')
    else:
        song_cache = {}
        logger.info('Cache utworów jest pusty.')
except (FileNotFoundError, json.JSONDecodeError) as e:
    song_cache = {}
    logger.warning(f'Nie znaleziono pliku cache lub plik jest uszkodzony ({e}), zaczynamy od pustego cache.')

# Funkcja zapisywania cache
def save_cache():
    try:
        with open(CACHE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(song_cache, f, ensure_ascii=False, indent=4)
        logger.info('Cache został zapisany poprawnie.')
    except Exception as e:
        logger.error(f'Błąd podczas zapisywania cache: {e}')

# Opcje FFMPEG
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -loglevel panic -bufsize 256k'  # Zwiększenie buforu na 256k
}

queues = []
current_song = None
loop_song = False
loop_queue = False
voice_channel = None
voice_client = None
start_time = None

disconnect_task = None

# Kolory dla embedów
EMBED_COLOR = 0xA8E6CF  # pastelowy zielony

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Funkcja do odtwarzania muzyki w tle
    def play_music(self, voice_client, source, after_callback):
        voice_client.play(discord.FFmpegPCMAudio(executable="C:/Users/broga/Desktop/Programming/gpt dsc bot/ffmpeg/bin/ffmpeg.exe", source=source, **FFMPEG_OPTIONS), after=after_callback)

    # Komenda odtwarzania muzyki
    @commands.command(name='play', aliases=['p'], help='Odtwórz muzykę z YouTube. Użyj: !play [nazwa utworu / URL]')
    async def play(self, ctx, *url):
        global current_song, loop_song, voice_channel, voice_client, disconnect_task
        try:
            # Przechodzimy na kanał głosowy użytkownika
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                voice_client = await channel.connect()
                voice_channel = channel
            else:
                voice_client = ctx.voice_client
                # Jeśli bot gra na innym kanale, blokujemy
                if voice_client.channel != channel:
                    await ctx.send("Bot jest już połączony na innym kanale głosowym. 🎶")
                    return
        except AttributeError:
            await ctx.send("Musisz być na kanale głosowym, aby użyć tej komendy. 🎶")
            return

        # Jeśli istnieje zadanie rozłączenia, anulujemy je
        if disconnect_task:
            disconnect_task.cancel()
            disconnect_task = None

        # Łączenie URL jeśli użytkownik podał frazę zamiast linku
        url = ' '.join(url)

        # Sprawdź, czy utwór jest już w cache
        if url in song_cache:
            info = song_cache[url]
            logger.info(f'Użycie cache dla utworu: {info.get("title", "Nieznany tytuł")}')
        else:
            # Jeśli utwór nie jest w cache, wykonujemy zapytanie do YouTube
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'default_search': 'ytsearch',  # Domyślne wyszukiwanie na YouTube
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True  # Ustawienie 'quiet', aby ograniczyć logi yt_dlp
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)

                    # Jeśli to wyszukiwanie, bierzemy pierwszy wynik
                    if 'entries' in info:
                        info = info['entries'][0]

                    # Zapisz informacje o utworze w cache'u
                    song_cache[url] = info
                    logger.info(f'Dodano do cache utwór: {info.get("title", "Nieznany tytuł")}')
                    save_cache()

                except youtube_dl.utils.DownloadError:
                    await ctx.send("Nie udało się znaleźć lub odtworzyć tej piosenki. Spróbuj jeszcze raz. 🎶")
                    return

        # Odtwarzanie utworu
        url2 = info['url']
        title = info.get('title', 'Nieznany tytuł')
        webpage_url = info.get('webpage_url', '')
        thumbnail = info.get('thumbnail', '')
        duration = info.get('duration', 0)

        # Przygotowanie embedu z informacjami o utworze
        embed = discord.Embed(title="Odtwarzanie muzyki", description=f"[{title}]({webpage_url})", color=EMBED_COLOR)
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name="Czas trwania", value=f"{duration // 60}:{duration % 60:02d}", inline=True)

        if voice_client.is_playing() or voice_client.is_paused():
            queues.append((url, title, webpage_url, thumbnail, duration))
            embed = discord.Embed(title="Dodano do kolejki", description=f"[{title}]({webpage_url})", color=EMBED_COLOR)
            embed.set_thumbnail(url=thumbnail)
            embed.add_field(name="Czas trwania", value=f"{duration // 60}:{duration % 60:02d}", inline=True)
            await ctx.send(embed=embed)
        else:
            def after_song(err):
                global loop_song, loop_queue, disconnect_task
                if loop_song:
                    threading.Thread(target=self.play_music, args=(voice_client, url2, after_song)).start()
                elif queues and loop_queue:
                    next_song = queues.pop(0)
                    queues.append(next_song)
                    ctx.bot.loop.create_task(self.play(ctx, next_song[0]))
                elif queues:
                    next_song = queues.pop(0)
                    ctx.bot.loop.create_task(self.play(ctx, next_song[0]))
                else:
                    disconnect_task = ctx.bot.loop.create_task(self.disconnect_after_delay(ctx))

            threading.Thread(target=self.play_music, args=(voice_client, url2, after_song)).start()
            current_song = (url, title, webpage_url, thumbnail, duration)
            pink_log(ctx, "Odtwarzanie muzyki w tle")
            await ctx.send(embed=embed)

    # Funkcja rozłączenia po opóźnieniu
    async def disconnect_after_delay(self, ctx):
        await asyncio.sleep(300)  # 5 minut
        if not ctx.voice_client.is_playing():
            await ctx.voice_client.disconnect()
            pink_log(ctx, "Bot został rozłączony z powodu braku aktywności.")
            await ctx.send("Bot został rozłączony z powodu braku aktywności. 🎶")

    # Komenda pomijania utworu
    @commands.command(name='skip', aliases=['s'], help='Przewiń do następnej piosenki w kolejce. Użyj: !skip lub !s')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            pink_log(ctx, "Utwór pominięty przez użytkownika.")
            await ctx.send("Pominięto aktualnie odtwarzaną piosenkę. 🎶")

    # Komenda zapętlania utworu
    @commands.command(name='loop', help='Zapętlaj aktualnie odtwarzaną piosenkę. Użyj: !loop')
    async def loop(self, ctx):
        global loop_song
        loop_song = not loop_song
        status = "włączone" if loop_song else "wyłączone"
        pink_log(ctx, f"Zapętlanie utworu: {status}")
        await ctx.send(f"Zapętlanie utworu zostało {status}. 🎶")

    # Komenda zapętlania kolejki
    @commands.command(name='loopqueue', aliases=['lq'], help='Zapętlaj kolejkę. Użyj: !loopqueue lub !lq')
    async def loopqueue(self, ctx):
        global loop_queue
        loop_queue = not loop_queue
        status = "włączone" if loop_queue else "wyłączone"
        pink_log(ctx, f"Zapętlanie kolejki: {status}")
        await ctx.send(f"Zapętlanie kolejki zostało {status}. 🎶")

    # Komenda zatrzymywania odtwarzania
    @commands.command(name='stop', aliases=['pause'], help='Wstrzymaj odtwarzanie muzyki. Użyj: !stop')
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            pink_log(ctx, "Odtwarzanie zostało wstrzymane")
            await ctx.send("Wstrzymano odtwarzanie muzyki. 🎶")

    # Komenda wznawiania odtwarzania
    @commands.command(name='resume', help='Wznów odtwarzanie muzyki. Użyj: !resume')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            pink_log(ctx, "Odtwarzanie zostało wznowione.")
            await ctx.send("Wznowiono odtwarzanie muzyki. 🎶")

    # Komenda rozłączenia bota z kanału głosowego
    @commands.command(name='disconnect', aliases=['dc'], help='Rozłącz bota z kanału głosowego. Użyj: !disconnect lub !dc')
    async def disconnect(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            pink_log(ctx, "Bot został rozłączony z kanału głosowego.")
            await ctx.send("Bot został rozłączony z kanału głosowego. 🎶")

    # Komenda wyświetlania kolejki
    @commands.command(name='queue', aliases=['q'], help='Wyświetl listę piosenek w kolejce. Użyj: !queue lub !q')
    async def queue_list(self, ctx):
        if current_song:
            _, title, webpage_url, thumbnail, duration = current_song
            now_playing_str = f"**Aktualnie odtwarzana piosenka**\n[{title}]({webpage_url}) - {duration // 60}:{duration % 60:02d}\n"
            queue_str = "\n".join([f"{idx + 1}. [{title}]({webpage_url}) - {duration // 60}:{duration % 60:02d}" for idx, (_, title, webpage_url, _, duration) in enumerate(queues)])
            embed = discord.Embed(title="Kolejka piosenek", description=now_playing_str + "\n**Kolejne piosenki**\n" + queue_str, color=EMBED_COLOR)
            embed.set_thumbnail(url=thumbnail)
            pink_log(ctx, "Wyświetlenie kolejki piosenek.")
            await ctx.send(embed=embed)
        else:
            await ctx.send("Kolejka jest pusta. 🎶")

# Funkcja setup, która pozwala zarejestrować cogs w bota
async def setup(bot):
    await bot.add_cog(Music(bot))
