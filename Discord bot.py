import discord
from discord.ext import commands, tasks
import youtube_dl
import asyncio
import os

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
queues = []

# Muzyka
@bot.command(name='play', help='Odtwórz muzykę z YouTube. Użyj: !play [nazwa utworu / URL]')
async def play(ctx, *url):
    try:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
    except discord.ClientException:
        voice_client = ctx.voice_client
    except AttributeError:
        await ctx.send("Musisz być na kanale głosowym, aby użyć tej komendy.")
        return

    url = ' '.join(url)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=url2))
        queues.append(url2)

@bot.command(name='skip', help='Przewiń do następnej piosenki w kolejce. Użyj: !skip')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Pominięto aktualnie odtwarzaną piosenkę.")
    if queues:
        await play(ctx, queues.pop(0))

@bot.command(name='pause', help='Wstrzymaj aktualnie odtwarzaną piosenkę. Użyj: !pause')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Muzyka została wstrzymana.")

@bot.command(name='resume', help='Wznów odtwarzanie piosenki. Użyj: !resume')
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Muzyka została wznowiona.")

@bot.command(name='stop', help='Zatrzymaj odtwarzanie i wyczyść kolejkę. Użyj: !stop')
async def stop(ctx):
    if ctx.voice_client:
        queues.clear()
        await ctx.voice_client.disconnect()
        await ctx.send("Odtwarzanie zostało zatrzymane, a kolejka wyczyszczona.")

@bot.command(name='rewind', help='Przewiń muzykę o określoną liczbę sekund do tyłu. Użyj: !rewind [sekundy]')
async def rewind(ctx, seconds: int):
    await ctx.send(f"Funkcja przewijania o {seconds} sekund jeszcze nie jest zaimplementowana.")

@bot.command(name='loop', help='Zapętlaj aktualnie odtwarzaną piosenkę. Użyj: !loop')
async def loop(ctx):
    await ctx.send("Funkcja zapętlania jeszcze nie jest zaimplementowana.")

@bot.command(name='queue', help='Dodaj piosenkę do kolejki. Użyj: !queue [nazwa utworu / URL]')
async def queue(ctx, *url):
    url = ' '.join(url)
    queues.append(url)
    await ctx.send(f"Dodano do kolejki: {url}")

@bot.command(name='loopqueue', help='Zapętlaj kolejkę. Użyj: !loopqueue')
async def loopqueue(ctx):
    await ctx.send("Funkcja zapętlania kolejki jeszcze nie jest zaimplementowana.")

# Komendy moderacyjne
@bot.command(name='kick', help='Wyrzuć użytkownika z serwera. Użyj: !kick [użytkownik]')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Użytkownik {member.mention} został wyrzucony.')

@bot.command(name='ban', help='Zbanuj użytkownika. Użyj: !ban [użytkownik]')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Użytkownik {member.mention} został zbanowany.')

@bot.command(name='mute', help='Wycisz użytkownika. Użyj: !mute [użytkownik]')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)
    await member.add_roles(muted_role)
    await ctx.send(f'Użytkownik {member.mention} został wyciszony.')

@bot.command(name='unmute', help='Odblokuj użytkownika. Użyj: !unmute [użytkownik]')
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(muted_role)
    await ctx.send(f'Użytkownik {member.mention} został odblokowany.')

@bot.command(name='warn', help='Ostrzeż użytkownika. Użyj: !warn [użytkownik] [powód]')
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    await ctx.send(f'Użytkownik {member.mention} został ostrzeżony za: {reason}')

@bot.command(name='clear', help='Wyczyść określoną liczbę wiadomości. Użyj: !clear [liczba]')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'Usunięto {amount} wiadomości.', delete_after=5)

# Uruchomienie bota
bot.run('MTMwMzEyMjA0MTMyMjM0MDQ5Ng.GHvZxB.qlLugtI2I5gJo7-uvv-vNNlSHaWokRVu0KNvnU')
