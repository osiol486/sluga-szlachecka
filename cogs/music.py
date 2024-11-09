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
import time
from utils.constants import EMBED_COLOR_GREEN


# Funkcja logująca wiadomości na poziomie DEBUG z kolorem magenta
def pink_log(ctx, message):
    guild_info = f"[{ctx.guild.name} ({ctx.guild.id})]" if ctx.guild else "[Brak serwera]"
    logger.debug(f"{guild_info} {message}")

# Folder do przechowywania cache'u
CACHE_FOLDER = "cache"
CACHE_FILE_PATH = os.path.join(CACHE_FOLDER, "music_cache.json")
MAX_CACHE_SIZE_MB = 25

# Sprawdź, czy folder cache istnieje, jeśli nie - utwórz go
if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)

# Inicjalizacja cache'u dla utworów
try:
    # Odczytaj cache z pliku, jeśli istnieje
    if os.path.exists(CACHE_FILE_PATH):
        if os.path.getsize(CACHE_FILE_PATH) > MAX_CACHE_SIZE_MB * 1024 * 1024:
            os.remove(CACHE_FILE_PATH)
            logger.debug(f'Plik cache osiągnął maksymalny rozmiar {MAX_CACHE_SIZE_MB} MB i został usunięty.')
            song_cache = {}
        else:
            with open(CACHE_FILE_PATH, 'r', encoding='utf-8') as f:
                song_cache = json.load(f)
            logger.debug('Załadowano cache utworów.')
    else:
        song_cache = {}
        logger.debug('Cache utworów jest pusty.')
except (FileNotFoundError, json.JSONDecodeError) as e:
    song_cache = {}
    logger.error(f'Nie znaleziono pliku cache lub plik jest uszkodzony ({e}), zaczynamy od pustego cache.')

# Funkcja zapisywania cache
def save_cache():
    try:
        with open(CACHE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(song_cache, f, ensure_ascii=False, indent=4)
        logger.debug('Cache został zapisany poprawnie.')
    except Exception as e:
        logger.error(f'Błąd podczas zapisywania cache: {e}')
        
# Ustawienie ścieżki do ffmpeg.exe
FFMPEG_PATH = os.path.join(os.path.dirname(__file__), "..", "ffmpeg", "bin", "ffmpeg.exe")

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

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []  # Kolejka odtwarzania
        self.loop_song = False
        self.loop_queue = False
        self.voice_client = None
        self.current_song = None
        self.start_time = None
        self.history = []

    # Funkcja do odtwarzania muzyki w tle
    def play_music(self, voice_client, source, after_callback):
        voice_client.play(discord.FFmpegPCMAudio(executable="FFMPEG_PATH", source=source, **FFMPEG_OPTIONS), after=after_callback)

    async def play_song(self, ctx, url, start_time=0):
        FFMPEG_OPTIONS = {
            'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {start_time}',
            'options': '-vn'
        }
        source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
        self.voice_client.play(source, after=lambda e: logger.error(f'Błąd podczas odtwarzania: {e}') if e else None)
        self.start_time = time.time() - start_time  # Ustawienie czasu rozpoczęcia odtwarzania

    # Komenda odtwarzania muzyki
    @commands.command(name='play', aliases=['p'], help='Odtwórz muzykę z YouTube. Użyj: !play [nazwa utworu / URL]')
    async def play(self, ctx, *url):
        global disconnect_task
        try:
            # Przechodzimy na kanał głosowy użytkownika
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                voice_client = await channel.connect()
                self.voice_client = voice_client
            else:
                self.voice_client = ctx.voice_client
                # Jeśli bot gra na innym kanale, blokujemy
                if self.voice_client.channel != channel:
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

        # Opcje dla youtube_dl
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

        # Sprawdź, czy utwór jest już w cache
        if url in song_cache:
            info = song_cache[url]
            logger.debug(f'Użycie cache dla utworu: {info.get("title", "Nieznany tytuł")}')
        else:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)

                    # Jeśli to wyszukiwanie, sprawdzamy, czy są wyniki
                    if 'entries' in info and len(info['entries']) > 0:
                        info = info['entries'][0]
                    elif 'entries' in info:
                        await ctx.send("Nie znaleziono żadnych wyników. Spróbuj użyć innej frazy. 🎶")
                        return

                    # Zapisz informacje o utworze w cache'u
                    song_cache[url] = info
                    logger.debug(f'Dodano do cache utwór: {info.get("title", "Nieznany tytuł")}')
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

        # Ustawienie aktualnie odtwarzanego utworu
        self.current_song = {
            'url': url2,
            'title': title,
            'webpage_url': webpage_url,
            'thumbnail': thumbnail,
            'duration': duration
        }

        # Ustawienie start_time
        self.start_time = time.time()

        # Przygotowanie embedu z informacjami o utworze
        embed = discord.Embed(title="Odtwarzanie muzyki", description=f"[{title}]({webpage_url})", color=EMBED_COLOR_GREEN)
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name="Czas trwania", value=f"{duration // 60}:{duration % 60:02d}", inline=True)

        if self.voice_client.is_playing() or self.voice_client.is_paused():
            self.queue.append((url, title, webpage_url, thumbnail, duration))
            embed = discord.Embed(title="Dodano do kolejki", description=f"[{title}]({webpage_url})", color=EMBED_COLOR_GREEN)
            embed.set_thumbnail(url=thumbnail)
            embed.add_field(name="Czas trwania", value=f"{duration // 60}:{duration % 60:02d}", inline=True)
            await ctx.send(embed=embed)
        else:
            def after_song(err):
                if err:
                    logger.error(f'Błąd podczas odtwarzania utworu: {err}')
                if self.loop_song:
                    self.play_music(self.voice_client, url2, after_song)
                elif self.queue:
                    next_song = self.queue.pop(0)
                    if self.loop_queue:
                        self.queue.append(next_song)  # Dodaj na koniec, jeśli loop_queue jest włączone
                    ctx.bot.loop.create_task(self.play(ctx, next_song[0]))
                else:
                    disconnect_task = ctx.bot.loop.create_task(self.disconnect_after_delay(ctx))

            self.play_music(self.voice_client, url2, after_song)
            global current_song
            current_song = (url, title, webpage_url, thumbnail, duration)
            logger.debug(f"Odtwarzanie muzyki: {title}")
            await ctx.send(embed=embed)

    # Funkcja rozłączenia po opóźnieniu
    async def disconnect_after_delay(self, ctx):
        await asyncio.sleep(300)  # 5 minut
        if not ctx.voice_client.is_playing():
            await ctx.voice_client.disconnect()
            logger.info("Bot został rozłączony z powodu braku aktywności.")
            await ctx.send("Bot został rozłączony z powodu braku aktywności. 🎶")

    # Komenda pomijania utworu
    @commands.command(name='skip', aliases=['s'], help='Przewiń do następnej piosenki w kolejce. Użyj: !skip lub !s')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            logger.debug("Utwór pominięty przez użytkownika.")
            await ctx.send("Pominięto aktualnie odtwarzaną piosenkę. 🎶")

    # Komenda zapętlania utworu
    @commands.command(name='loop', help='Zapętlaj aktualnie odtwarzaną piosenkę. Użyj: !loop')
    async def loop(self, ctx):
        self.loop_song = not self.loop_song
        status = "włączone" if self.loop_song else "wyłączone"
        logger.debug(f"Zapętlanie utworu: {status}")
        await ctx.send(f"Zapętlanie utworu zostało {status}. 🎶")

    # Komenda zapętlania kolejki
    @commands.command(name='loopqueue', aliases=['lq'], help='Zapętlaj kolejkę. Użyj: !loopqueue lub !lq')
    async def loopqueue(self, ctx):
        self.loop_queue = not self.loop_queue
        status = "włączone" if self.loop_queue else "wyłączone"
        logger.debug(f"Zapętlanie kolejki: {status}")
        await ctx.send(f"Zapętlanie kolejki zostało {status}. 🎶")

    # Komenda zatrzymywania odtwarzania
    @commands.command(name='stop', aliases=['pause'], help='Wstrzymaj odtwarzanie muzyki. Użyj: !stop')
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            logger.debug("Odtwarzanie zostało wstrzymane")
            await ctx.send("Wstrzymano odtwarzanie muzyki. 🎶")

    # Komenda wznawiania odtwarzania
    @commands.command(name='resume', help='Wznów odtwarzanie muzyki. Użyj: !resume')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            logger.debug("Odtwarzanie zostało wznowione.")
            await ctx.send("Wznowiono odtwarzanie muzyki. 🎶")

    # Komenda rozłączenia bota z kanału głosowego
    @commands.command(name='disconnect', aliases=['dc'], help='Rozłącz bota z kanału głosowego. Użyj: !disconnect lub !dc')
    async def disconnect(self, ctx):
        if ctx.voice_client:
            if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel:
                await ctx.voice_client.disconnect()
                logger.info("Bot został rozłączony z kanału głosowego.")
                await ctx.send("Bot został rozłączony z kanału głosowego. 🎶")
            else:
                await ctx.send("Musisz być na tym samym kanale głosowym, aby rozłączyć bota. 🎶")

    @commands.command(name='queue', aliases=['q'], help='Wyświetl listę piosenek w kolejce. Użyj: !queue lub !q')
    async def queue_list(self, ctx, page: int = 1):
        if not self.queue and not self.current_song:
            await ctx.send("Kolejka jest pusta. 🎶")
            return

        # Wyświetl aktualnie odtwarzany utwór
        queue_str = ""
        if self.current_song:
            title = self.current_song['title']
            webpage_url = self.current_song['webpage_url']
            duration = self.current_song['duration']
            queue_str += f"**Aktualnie odtwarzana piosenka**\n[{title}]({webpage_url}) - {duration // 60}:{duration % 60:02d}\n\n"

        # Tworzenie stron
        items_per_page = 10
        total_pages = (len(self.queue) + items_per_page - 1) // items_per_page
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page

        # Wyświetl piosenki na bieżącej stronie
        queue_page = self.queue[start_idx:end_idx]
        queue_str += "**Kolejne piosenki**\n"
        queue_str += "\n".join([f"{start_idx + idx + 1}. [{song[1]}]({song[2]}) - {song[4] // 60}:{song[4] % 60:02d}"
                                  for idx, song in enumerate(queue_page)])

        embed = discord.Embed(title=f"Kolejka piosenek - Strona {page}/{total_pages}", description=queue_str, color=0xA8E6CF)
        if self.current_song:
            embed.set_thumbnail(url=self.current_song['thumbnail'])
        await ctx.send(embed=embed)

    @commands.command(name='queue_page', help='Przejdź do określonej strony kolejki. Użyj: !queue_page [numer strony]')
    async def queue_page(self, ctx, page: int = None):
        if page is None:
            await ctx.send("Proszę podać numer strony, do której chcesz przejść. 📄")
        else:
            await self.queue_list(ctx, page)

    @commands.command(name='now_playing', aliases=['np'], help='Sprawdź, na jakiej minucie odtwarzania jesteś. Użyj: !now_playing lub !np')
    async def now_playing(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            if not self.current_song:
                await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")
                return

            elapsed_time = time.time() - self.start_time if self.start_time else 0
            elapsed_minutes = int(elapsed_time // 60)
            elapsed_seconds = int(elapsed_time % 60)

            total_duration = self.current_song['duration']
            total_minutes = int(total_duration // 60)
            total_seconds = int(total_duration % 60)

            progress_bar_length = 20
            progress = int((elapsed_time / total_duration) * progress_bar_length) if total_duration > 0 else 0
            progress_bar = "▬" * progress + "🔘" + "▬" * (progress_bar_length - progress - 1)

            embed = discord.Embed(title="Teraz odtwarzane", description=f"[{self.current_song['title']}]({self.current_song['webpage_url']})", color=0x00ff00)
            embed.set_thumbnail(url=self.current_song['thumbnail'])
            embed.add_field(name="Czas", value=f"{elapsed_minutes}:{elapsed_seconds:02d} / {total_minutes}:{total_seconds:02d}", inline=False)
            embed.add_field(name="Postęp", value=progress_bar, inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")

    async def play_song(self, ctx, url, start_time=0):
        FFMPEG_OPTIONS = {
            'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {start_time}',
            'options': '-vn'
        }
        with youtube_dl.YoutubeDL({'format': 'bestaudio'}) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
            title = info.get('title', 'Nieznany tytuł')
            webpage_url = info.get('webpage_url', url)
            thumbnail = info.get('thumbnail', '')
            duration = info.get('duration', 0)

        source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
        if ctx.voice_client is None:
            channel = ctx.author.voice.channel
            self.voice_client = await channel.connect()
        else:
            self.voice_client = ctx.voice_client

        self.voice_client.play(source, after=lambda e: logger.error(f'Błąd podczas odtwarzania: {e}') if e else None)
        self.start_time = time.time() - start_time  # Ustawienie czasu rozpoczęcia odtwarzania

        # Aktualizacja historii utworów
        if self.current_song:
            self.history.append(self.current_song)
        self.current_song = {
            'url': url,
            'title': title,
            'webpage_url': webpage_url,
            'thumbnail': thumbnail,
            'duration': duration
        }

    @commands.command(name='forward', aliases=['fwd'], help='Przewiń aktualnie odtwarzaną piosenkę o określoną liczbę sekund. Użyj: !forward [sekundy]')
    async def forward(self, ctx, seconds: int):
        if ctx.voice_client and ctx.voice_client.is_playing():
            if not self.current_song:
                await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")
                return

            url = self.current_song['url']
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            new_position = elapsed_time + seconds

            ctx.voice_client.stop()
            await self.play_song(ctx, url, start_time=new_position)

            logger.debug(f"Przewinięto utwór do przodu o {seconds} sekund.")
            await ctx.send(f"Przewinięto utwór do przodu o {seconds} sekund. ⏩")
        else:
            await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")

    @commands.command(name='rewind', aliases=['rwd'], help='Cofnij aktualnie odtwarzaną piosenkę o określoną liczbę sekund. Użyj: !rewind [sekundy]')
    async def rewind(self, ctx, seconds: int):
        if ctx.voice_client and ctx.voice_client.is_playing():
            if not self.current_song:
                await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")
                return

            url = self.current_song['url']
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            new_position = max(elapsed_time - seconds, 0)

            ctx.voice_client.stop()
            await self.play_song(ctx, url, start_time=new_position)

            logger.debug(f"Cofnięto utwór o {seconds} sekund.")
            await ctx.send(f"Cofnięto utwór o {seconds} sekund. ⏪")
        else:
            await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")

    @commands.command(name='seek', help='Przewiń aktualnie odtwarzaną piosenkę do określonego czasu. Użyj: !seek [sekundy lub mm:ss]')
    async def seek(self, ctx, *, time_str: str):
        try:
            seconds = parse_minutes_seconds(time_str) if ':' in time_str else parse_time(time_str)
        except ValueError:
            await ctx.send("Nieprawidłowy format czasu. Użyj formatu sekund (np. 90) lub mm:ss (np. 01:30). ⏱️")
            return

        if ctx.voice_client and ctx.voice_client.is_playing():
            if not self.current_song:
                await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")
                return

            url = self.current_song['url']
            ctx.voice_client.stop()
            await self.play_song(ctx, url, start_time=seconds)

            logger.debug(f"Przewinięto utwór do pozycji {seconds} sekund.")
            await ctx.send(f"Przewinięto utwór do pozycji {seconds} sekund. ⏩")
        else:
            await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")
    
    @commands.command(name='remove', help='Usuń utwór z kolejki na podstawie jego numeru. Użyj: !remove [numer]')
    async def remove(self, ctx, position: int):
        if position < 1 or position > len(self.queue):
            await ctx.send("Nieprawidłowy numer utworu. 🎶")
            return

        removed_song = self.queue.pop(position - 1)
        await ctx.send(f"Usunięto utwór: {removed_song[1]} z kolejki. ❌")

    @commands.command(name='clearqueue', aliases=['cq'], help='Wyczyść kolejkę. Użyj: !clearqueue')
    async def clearqueue(self, ctx):
        self.queue.clear()
        await ctx.send("Kolejka została wyczyszczona. 🧹")

# Funkcja setup, która pozwala zarejestrować cogs w bota
async def setup(bot):
    await bot.add_cog(Music(bot))
