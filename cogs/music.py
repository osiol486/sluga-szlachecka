import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import re
import threading
import logging
from colorama import Fore, Style
from datetime import timedelta, datetime

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Funkcja logująca wiadomości na różowo
def pink_log(message):
    logging.info(f"{Fore.MAGENTA}{message}{Style.RESET_ALL}")

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

    # Funkcja do parsowania czasu
    def parse_time(self, time_str):
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

    # Funkcja do parsowania czasu w formacie MM:SS
    def parse_minutes_seconds(self, time_str):
        match = re.match(r"(\d+):(\d+)", time_str)
        if match:
            minutes, seconds = match.groups()
            return int(minutes) * 60 + int(seconds)
        return None

    # Funkcja do odtwarzania muzyki w tle
    def play_music(self, voice_client, source, after_callback):
        pink_log("Odtwarzanie muzyki w tle")
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

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': 'ytsearch',  # Domyślne wyszukiwanie na YouTube
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)

                # Jeśli to wyszukiwanie, bierzemy pierwszy wynik
                if 'entries' in info:
                    info = info['entries'][0]

                url2 = info['url']
                title = info.get('title', 'Nieznany tytuł')
                webpage_url = info.get('webpage_url', '')
                thumbnail = info.get('thumbnail', '')
                duration = info.get('duration', 0)

                # Przygotowanie embedu z informacjami o utworze
                embed = discord.Embed(title="Odtwarzanie muzyki", description=f"[{title}]({webpage_url})", color=EMBED_COLOR)
                embed.set_thumbnail(url=thumbnail)
                embed.add_field(name="Czas trwania", value=f"{duration // 60}:{duration % 60:02d}", inline=True)

                # Dodanie do kolejki, jeśli coś już jest odtwarzane
                if voice_client.is_playing() or voice_client.is_paused():
                    queues.append((url, title, webpage_url, thumbnail, duration))
                    embed = discord.Embed(title="Dodano do kolejki", description=f"[{title}]({webpage_url})", color=EMBED_COLOR)
                    embed.set_thumbnail(url=thumbnail)
                    embed.add_field(name="Czas trwania", value=f"{duration // 60}:{duration % 60:02d}", inline=True)
                    await ctx.send(embed=embed)
                else:
                    # Odtwarzanie muzyki
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
                    await ctx.send(embed=embed)

            except youtube_dl.utils.DownloadError:
                await ctx.send("Nie udało się znaleźć lub odtworzyć tej piosenki. Spróbuj jeszcze raz. 🎶")

    # Funkcja rozłączenia po opóźnieniu
    async def disconnect_after_delay(self, ctx):
        await asyncio.sleep(300)  # 5 minut
        if not ctx.voice_client.is_playing():
            await ctx.voice_client.disconnect()
            pink_log("Bot został rozłączony z powodu braku aktywności.")
            await ctx.send("Bot został rozłączony z powodu braku aktywności. 🎶")

    # Komenda pomijania utworu
    @commands.command(name='skip', aliases=['s'], help='Przewiń do następnej piosenki w kolejce. Użyj: !skip lub !s')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            pink_log("Utwór pominięty przez użytkownika.")
            await ctx.send("Pominięto aktualnie odtwarzaną piosenkę. 🎶")

    # Komenda zapętlania utworu
    @commands.command(name='loop', help='Zapętlaj aktualnie odtwarzaną piosenkę. Użyj: !loop')
    async def loop(self, ctx):
        global loop_song
        loop_song = not loop_song
        status = "włączone" if loop_song else "wyłączone"
        pink_log(f"Zapętlanie utworu: {status}")
        await ctx.send(f"Zapętlanie utworu zostało {status}. 🎶")

    # Komenda zapętlania kolejki
    @commands.command(name='loopqueue', aliases=['lq'], help='Zapętlaj kolejkę. Użyj: !loopqueue lub !lq')
    async def loopqueue(self, ctx):
        global loop_queue
        loop_queue = not loop_queue
        status = "włączone" if loop_queue else "wyłączone"
        pink_log(f"Zapętlanie kolejki: {status}")
        await ctx.send(f"Zapętlanie kolejki zostało {status}. 🎶")

    # Komenda zatrzymywania odtwarzania
    @commands.command(name='stop', aliases=['pause'], help='Wstrzymaj odtwarzanie muzyki. Użyj: !stop')
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            pink_log("Odtwarzanie zostało wstrzymane")
            await ctx.send("Wstrzymano odtwarzanie muzyki. 🎶")

    # Komenda wznawiania odtwarzania
    @commands.command(name='resume', help='Wznów odtwarzanie muzyki. Użyj: !resume')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            pink_log("Odtwarzanie zostało wznowione.")
            await ctx.send("Wznowiono odtwarzanie muzyki. 🎶")

    # Komenda rozłączenia bota z kanału głosowego
    @commands.command(name='disconnect', aliases=['dc'], help='Rozłącz bota z kanału głosowego. Użyj: !disconnect lub !dc')
    async def disconnect(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            pink_log("Bot został rozłączony z kanału głosowego.")
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
            pink_log("Wyświetlenie kolejki piosenek.")
            await ctx.send(embed=embed)
        else:
            await ctx.send("Kolejka jest pusta. 🎶")

# Funkcja setup, która pozwala zarejestrować cogs w bota
async def setup(bot):
    await bot.add_cog(Music(bot))
