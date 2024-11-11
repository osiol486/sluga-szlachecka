import os
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import json
from colorama import Fore, Style
from loguru import logger
from utils.utils import parse_time, parse_minutes_seconds
import time
from utils.constants import EMBED_COLOR_GREEN

from logger_config import configure_logger
configure_logger()


def pink_log(ctx, message):
    if ctx:
        guild_info = f"[{ctx.guild.name} ({ctx.guild.id})]"
        logger.debug(f"{guild_info} {message}")
    else:
        logger.debug(f"[Nieznany kontekst] {message}")

# Folder do przechowywania cache'u
CACHE_FOLDER = "cache"
CACHE_FILE_PATH = os.path.join(CACHE_FOLDER, "music_cache.json")
MAX_CACHE_SIZE_MB = 25

# Sprawdź, czy folder cache istnieje, jeśli nie - utwórz go
if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)

async def get_video_info(url, ydl_opts):
    # Przenieś blokującą operację do osobnego wątku
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return await asyncio.to_thread(ydl.extract_info, url, download=False)

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
        self.queue = {}  # Kolejka odtwarzania
        self.loop_song = False
        self.loop_queue = False
        self.voice_client = None
        self.current_song = None
        self.start_time = None
        self.history = []

    # Funkcja do odtwarzania muzyki w tle
    def play_music(self, voice_client, source, after_callback):
        voice_client.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=source, **FFMPEG_OPTIONS), after=after_callback)

    async def play_song(self, ctx, url, start_time=0):
        FFMPEG_OPTIONS = {
            'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {start_time}',
            'options': '-vn'
        }
        source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
        self.voice_client.play(source, after=lambda e: logger.error(f'Błąd podczas odtwarzania: {e}') if e else None)
        self.start_time = time.time() - start_time  # Ustawienie czasu rozpoczęcia odtwarzania

    @commands.command(name='play', aliases=['p'], help='Odtwórz muzykę z YouTube. Użyj: !play [nazwa utworu / URL]')
    async def play(self, ctx, *url):
        global disconnect_task

        # Upewnij się, że użytkownik jest na kanale głosowym
        try:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                # Połącz się z kanałem, jeśli bot jeszcze nie jest połączony
                self.voice_client = await channel.connect()
            else:
                # Sprawdź, czy bot jest na kanale użytkownika
                if ctx.voice_client.channel != channel:
                    await ctx.send("Bot jest już połączony na innym kanale głosowym. 🎶")
                    return
                self.voice_client = ctx.voice_client
        except AttributeError:
            await ctx.send("Musisz być na kanale głosowym, aby użyć tej komendy. 🎶")
            return

        # Anuluj rozłączenie, jeśli jest w toku
        if disconnect_task:
            disconnect_task.cancel()
            disconnect_task = None

        # Łączenie URL, jeśli użytkownik podał frazę zamiast linku
        url = ' '.join(url).strip()

        # Identyfikator serwera
        guild_id = ctx.guild.id
        # Utwórz nową kolejkę dla tego serwera, jeśli nie istnieje
        if guild_id not in self.queue:
            self.queue[guild_id] = []

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
            'quiet': True  # Ogranicz logi yt_dlp
        }

        # Sprawdź, czy utwór jest w cache
        cached_url = None
        if url in song_cache:
            info = song_cache[url]
            logger.info(f'Użycie cache dla utworu: {info.get("title", "Nieznany tytuł")}')
            cached_url = url
        else:
            try:
                # Pobierz informacje o utworze asynchronicznie
                info = await get_video_info(url, ydl_opts)

                # Jeśli to wyszukiwanie, sprawdzamy, czy są wyniki
                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]
                    url = info['webpage_url']
                elif 'entries' in info:
                    await ctx.send("Nie znaleziono żadnych wyników. Spróbuj użyć innej frazy. 🎶")
                    return

                # Dodaj do cache
                if url not in song_cache:
                    song_cache[url] = info
                    logger.debug(f'Dodano do cache utwór: {info.get("title", "Nieznany tytuł")}')
                    save_cache()

            except youtube_dl.utils.DownloadError:
                await ctx.send("Nie udało się znaleźć lub odtworzyć tej piosenki. Spróbuj jeszcze raz. 🎶")
                return

        # Przygotowanie danych o piosence
        url2 = info['url']
        title = info.get('title', 'Nieznany tytuł')
        webpage_url = info.get('webpage_url', '')
        thumbnail = info.get('thumbnail', '')
        duration = info.get('duration', 0)

        song_info = {
            'url': url2,
            'title': title,
            'webpage_url': webpage_url,
            'thumbnail': thumbnail,
            'duration': duration
        }

        # Sprawdź, czy coś jest aktualnie odtwarzane lub jest wstrzymane
        if self.voice_client.is_playing() or self.voice_client.is_paused():
            # Dodanie utworu do kolejki
            self.queue[guild_id].append(song_info)
            embed = discord.Embed(title="Dodano do kolejki", description=f"[{title}]({webpage_url})", color=EMBED_COLOR_GREEN)
            embed.set_thumbnail(url=thumbnail)
            embed.add_field(name="Czas trwania", value=f"{duration // 60}:{duration % 60:02d}", inline=True)
            await ctx.send(embed=embed)
        else:
            # Rozpoczęcie odtwarzania, jeśli nic nie jest odtwarzane
            self.current_song = song_info
            await self.start_playing(ctx, song_info)


    #### Poprawiona Funkcja `start_playing()`

    async def start_playing(self, ctx, song_info):
    # Użyj funkcji asynchronicznej jako after callback
        async def after_song(self, ctx, err):
            if err:
                logger.error(f'Błąd podczas odtwarzania utworu: {err}')
            
            # Sprawdź, czy zapętlanie jest włączone
            if self.loop_song:
                await self.start_playing(ctx, self.current_song)
            elif self.queue[ctx.guild.id]:
                next_song = self.queue[ctx.guild.id].pop(0)
                if self.loop_queue:
                    self.queue[ctx.guild.id].append(next_song)
                await self.start_playing(ctx, next_song)
            else:
                global disconnect_task
                disconnect_task = ctx.bot.loop.create_task(self.disconnect_after_delay(ctx))

        # Ustawienie aktualnie odtwarzanego utworu
        self.current_song = song_info
        self.start_time = time.time()  # Aktualizacja start_time

        # Przygotowanie embedu z informacjami o utworze
        embed = discord.Embed(title="Odtwarzanie muzyki", description=f"[{song_info['title']}]({song_info['webpage_url']})", color=EMBED_COLOR_GREEN)
        embed.set_thumbnail(url=song_info['thumbnail'])
        embed.add_field(name="Czas trwania", value=f"{song_info['duration'] // 60}:{song_info['duration'] % 60:02d}", inline=True)
        await ctx.send(embed=embed)

        # Odtwarzanie utworu
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        
        # Użycie `lambda` do wywołania funkcji asynchronicznej w pętli eventowej
        self.voice_client.play(discord.FFmpegPCMAudio(self.current_song['url'], **FFMPEG_OPTIONS), after=lambda e: ctx.bot.loop.create_task(self.after_song(ctx, e)))



    # Funkcja rozłączenia po opóźnieniu
    async def disconnect_after_delay(self, ctx):
        await asyncio.sleep(300)  # 5 minut
        if not ctx.voice_client.is_playing():
            await ctx.voice_client.disconnect()
            logger.info("Bot został rozłączony z powodu braku aktywności.")
            await ctx.send("Bot został rozłączony z powodu braku aktywności. 🎶")

    @commands.command(name='skip', aliases=['s'], help='Przewiń do następnej piosenki w kolejce. Użyj: !skip lub !s')
    async def skip(self, ctx):
        guild_id = ctx.guild.id
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            logger.debug("Utwór pominięty przez użytkownika.")

            # Sprawdzenie kolejki serwera
            if guild_id in self.queue and self.queue[guild_id]:
                next_song = self.queue[guild_id].pop(0)
                await self.start_playing(ctx, next_song)
            else:
                await ctx.send("Kolejka jest pusta. 🎶")

    # Komenda zapętlania utworu
    @commands.command(name='loop', help='Zapętlaj aktualnie odtwarzaną piosenkę. Użyj: !loop')
    async def loop(self, ctx):
        self.loop_song = not self.loop_song
        status = "włączone" if self.loop_song else "wyłączone"
        await ctx.send(f"Zapętlanie utworu zostało {status}. 🎶")

    # Komenda zapętlania kolejki
    @commands.command(name='loopqueue', aliases=['lq'], help='Zapętlaj kolejkę. Użyj: !loopqueue lub !lq')
    async def loopqueue(self, ctx):
        self.loop_queue = not self.loop_queue
        status = "włączone" if self.loop_queue else "wyłączone"
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
        guild_id = ctx.guild.id
        if guild_id not in self.queue or not self.queue[guild_id]:
            if self.current_song:
                embed = discord.Embed(title="Kolejka piosenek", description="**🎶 Aktualnie odtwarzana piosenka**\n"
                                                                            f"[{self.current_song['title']}]({self.current_song['webpage_url']}) - {self.current_song['duration'] // 60}:{self.current_song['duration'] % 60:02d}\n",
                                    color=EMBED_COLOR_GREEN)
                embed.set_thumbnail(url=self.current_song['thumbnail'])
                msg = await ctx.send(embed=embed)

                if len(self.queue[guild_id]) > 0:
                    await msg.add_reaction('⏮️')
                    await msg.add_reaction('⏭️')
            else:
                await ctx.send("Kolejka jest pusta. 🎶")
            return

        queue_str = ""
        if self.current_song:
            title = self.current_song['title']
            webpage_url = self.current_song['webpage_url']
            duration = self.current_song['duration']
            queue_str += f"**🎶 Aktualnie odtwarzana piosenka**\n[{title}]({webpage_url}) - {duration // 60}:{duration % 60:02d}\n\n"

        # Ustawienie liczby elementów na stronę na 10
        items_per_page = 10
        total_pages = (len(self.queue[guild_id]) + items_per_page - 1) // items_per_page
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page

        # Wyświetl piosenki na bieżącej stronie
        queue_page = self.queue[guild_id][start_idx:end_idx]
        if queue_page:
            queue_str += "**📜 Kolejne piosenki w kolejce**\n"
            for idx, song in enumerate(queue_page):
                title = song['title']
                webpage_url = song['webpage_url']
                duration = song['duration']
                queue_str += f"{start_idx + idx + 1}. [{title}]({webpage_url}) - {duration // 60}:{duration % 60:02d}\n"

        embed = discord.Embed(title=f"Kolejka piosenek - Strona {page}/{total_pages}", description=queue_str, color=EMBED_COLOR_GREEN)
        if self.current_song:
            embed.set_thumbnail(url=self.current_song['thumbnail'])
        msg = await ctx.send(embed=embed)

        if total_pages > 1:
            await msg.add_reaction('⏮️')
            await msg.add_reaction('⏭️')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⏮️', '⏭️'] and reaction.message.id == msg.id

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                if str(reaction.emoji) == '⏮️':
                    page = max(1, page - 1)
                elif str(reaction.emoji) == '⏭️':
                    page = min(total_pages, page + 1)

                await msg.remove_reaction(reaction.emoji, user)

                queue_str = ""
                if self.current_song:
                    title = self.current_song['title']
                    webpage_url = self.current_song['webpage_url']
                    duration = self.current_song['duration']
                    queue_str += f"**🎶 Aktualnie odtwarzana piosenka**\n[{title}]({webpage_url}) - {duration // 60}:{duration % 60:02d}\n\n"

                start_idx = (page - 1) * items_per_page
                end_idx = start_idx + items_per_page
                queue_page = self.queue[guild_id][start_idx:end_idx]

                if queue_page:
                    queue_str += "**📜 Kolejne piosenki w kolejce**\n"
                    for idx, song in enumerate(queue_page):
                        title = song['title']
                        webpage_url = song['webpage_url']
                        duration = song['duration']
                        queue_str += f"{start_idx + idx + 1}. [{title}]({webpage_url}) - {duration // 60}:{duration % 60:02d}\n"

                embed = discord.Embed(title=f"Kolejka piosenek - Strona {page}/{total_pages}", description=queue_str, color=EMBED_COLOR_GREEN)
                if self.current_song:
                    embed.set_thumbnail(url=self.current_song['thumbnail'])
                await msg.edit(embed=embed)

            except asyncio.TimeoutError:
                break



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
        
        # Pobranie informacji o utworze z YouTube
        with youtube_dl.YoutubeDL({'format': 'bestaudio'}) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
            title = info.get('title', 'Nieznany tytuł')
            webpage_url = info.get('webpage_url', url)
            thumbnail = info.get('thumbnail', '')
            duration = info.get('duration', 0)

        # Stworzenie źródła audio
        source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)

        # Połączenie z kanałem głosowym
        if ctx.voice_client is None:
            channel = ctx.author.voice.channel
            self.voice_client = await channel.connect()
        else:
            self.voice_client = ctx.voice_client

        # Odtwarzanie utworu
        self.voice_client.play(source, after=lambda e: self.after_song(ctx, e))

        # Ustawienie czasu rozpoczęcia odtwarzania
        self.start_time = time.time() - start_time

        # Aktualizacja historii utworów, jeśli jest coś aktualnie odtwarzane
        if self.current_song:
            self.history.append(self.current_song)

        # Aktualizacja informacji o aktualnie odtwarzanym utworze
        self.current_song = {
            'url': url,
            'title': title,
            'webpage_url': webpage_url,
            'thumbnail': thumbnail,
            'duration': duration,
            'seek_position': start_time
        }

    @commands.command(name='forward', aliases=['fwd'], help='Przewiń aktualnie odtwarzaną piosenkę o określoną liczbę sekund. Użyj: !forward [sekundy]')
    async def forward(self, ctx, seconds: int):
        if ctx.voice_client and ctx.voice_client.is_playing():
            if not self.current_song:
                await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")
                return

            # Oblicz nową pozycję, upewniając się, że nie przekraczamy długości utworu
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            new_position = min(elapsed_time + seconds, self.current_song['duration'])

            # Rozpoczęcie odtwarzania od nowej pozycji za pomocą `FFmpeg` z `-ss`
            FFMPEG_OPTIONS = {
                'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {new_position}',
                'options': '-vn'
            }
            
            # Stopowanie aktualnego klienta i ponowne odtwarzanie od nowej pozycji
            self.voice_client.stop()
            self.voice_client.play(discord.FFmpegPCMAudio(self.current_song['url'], **FFMPEG_OPTIONS), after=lambda e: ctx.bot.loop.create_task(self.after_song(ctx, e)))

            # Ustawienie start_time na nową wartość
            self.start_time = time.time() - new_position

            # Aktualizacja embedu z informacjami o nowym czasie
            await self.send_now_playing_embed(ctx)

            await ctx.send(f"Przewinięto utwór do przodu o {seconds} sekund. ⏩")
        else:
            await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")

    @commands.command(name='rewind', aliases=['rwd'], help='Cofnij aktualnie odtwarzaną piosenkę o określoną liczbę sekund. Użyj: !rewind [sekundy]')
    async def rewind(self, ctx, seconds: int):
        if ctx.voice_client and ctx.voice_client.is_playing():
            if not self.current_song:
                await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")
                return

            # Oblicz nową pozycję, upewniając się, że nie spada poniżej 0
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            new_position = max(elapsed_time - seconds, 0)

            # Rozpoczęcie odtwarzania od nowej pozycji za pomocą `FFmpeg` z `-ss`
            FFMPEG_OPTIONS = {
                'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {new_position}',
                'options': '-vn'
            }
            
            # Stopowanie aktualnego klienta i ponowne odtwarzanie od nowej pozycji
            self.voice_client.stop()
            self.voice_client.play(discord.FFmpegPCMAudio(self.current_song['url'], **FFMPEG_OPTIONS), after=lambda e: ctx.bot.loop.create_task(self.after_song(ctx, e)))

            # Ustawienie start_time na nową wartość
            self.start_time = time.time() - new_position

            # Aktualizacja embedu z informacjami o nowym czasie
            await self.send_now_playing_embed(ctx)

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
            # Zatrzymanie obecnie odtwarzanego utworu
            ctx.voice_client.stop()
            # Rozpoczęcie odtwarzania od określonego czasu
            await self.play_song(ctx, url, start_time=seconds)

            # Aktualizacja `start_time` i `current_song`
            self.start_time = time.time() - seconds
            self.current_song['seek_position'] = seconds

            logger.debug(f"Przewinięto utwór do pozycji {seconds} sekund.")
            await ctx.send(f"Przewinięto utwór do pozycji {seconds} sekund. ⏩")
        else:
            await ctx.send("Nie odtwarzam teraz żadnej muzyki. 🎶")

    @commands.command(name='remove', help='Usuń utwór z kolejki na podstawie jego numeru. Użyj: !remove [numer]')
    async def remove(self, ctx, position: int):
        if position < 1 or position > len(self.queue[ctx.guild.id]):
            await ctx.send("Nieprawidłowy numer utworu. 🎶")
            return

        removed_song = self.queue[ctx.guild.id].pop(position - 1)
        await ctx.send(f"Usunięto utwór: {removed_song[1]} z kolejki. ❌")

    @commands.command(name='clearqueue', aliases=['cq'], help='Wyczyść kolejkę. Użyj: !clearqueue')
    async def clearqueue(self, ctx):
        self.queue[ctx.guild.id].clear()
        await ctx.send("Kolejka została wyczyszczona. 🧹")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Sprawdzamy, czy bot jest na kanale, który jest aktualnie pusty
        for vc in self.bot.voice_clients:
            if vc.channel and len(vc.channel.members) == 1 and vc.channel.members[0] == self.bot.user:
                await asyncio.sleep(5)  # Dajemy chwilę na ewentualny powrót użytkownika
                if len(vc.channel.members) == 1 and vc.channel.members[0] == self.bot.user:
                    await vc.disconnect()
                    logger.info(f"Bot został rozłączony z kanału głosowego ({vc.channel.id}), ponieważ kanał jest pusty.")


# Funkcja setup, która pozwala zarejestrować cogs w bota
async def setup(bot):
    await bot.add_cog(Music(bot))
