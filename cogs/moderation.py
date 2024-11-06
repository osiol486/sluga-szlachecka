import discord
from discord.ext import commands
import re
import asyncio
import logging
from colorama import Fore, Style

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format logu z datą, godziną i poziomem logowania
    datefmt='%Y-%m-%d %H:%M:%S'  # Format daty i godziny
)

# Funkcja logująca wiadomości na żółto
def yellow_log(message):
    logging.info(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")

# Kolory dla embedów
EMBED_COLOR_YELLOW = 0xFFEF0A  # żółtawy
EMBED_COLOR_RED = 0xFF0000  # czerwony

class Moderation(commands.Cog):
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

    # Komenda do wyrzucenia użytkownika
    @commands.command(name='kick', help='Wyrzuć użytkownika z serwera. Użyj: !kick [użytkownik]')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        yellow_log(f'Użytkownik {member} został wyrzucony z serwera przez {ctx.author}. Powód: {reason}')
        embed = discord.Embed(title="Użytkownik wyrzucony", description=f"{member.mention} został wyrzucony z serwera przez {ctx.author.mention}.", color=EMBED_COLOR_YELLOW)
        if reason:
            embed.add_field(name="Powód", value=reason, inline=False)
        await ctx.send(embed=embed)

    # Komenda do zbanowania użytkownika
    @commands.command(name='ban', help='Zbanuj użytkownika na określony czas. Użyj: !ban [użytkownik] [czas (np. 1h, 1d)]')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, time: str = None, *, reason=None):
        await member.ban(reason=reason)
        yellow_log(f'Użytkownik {member} został zbanowany przez {ctx.author}. Powód: {reason}')
        embed = discord.Embed(title="Użytkownik zbanowany", description=f"{member.mention} został zbanowany przez {ctx.author.mention}.", color=EMBED_COLOR_RED)
        if reason:
            embed.add_field(name="Powód", value=reason, inline=False)
        await ctx.send(embed=embed)
        if time:
            seconds = self.parse_time(time)
            if seconds:
                await asyncio.sleep(seconds)
                await ctx.guild.unban(member)
                yellow_log(f'Użytkownik {member} został odbanowany po {time}.')
                embed = discord.Embed(title="Użytkownik odbanowany", description=f"{member.mention} został odbanowany po {time}.", color=EMBED_COLOR_YELLOW)
                await ctx.send(embed=embed)

    # Komenda do wyciszenia użytkownika
    @commands.command(name='mute', help='Wycisz użytkownika na określony czas. Użyj: !mute [użytkownik] [czas (np. 1h, 1d)]')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, time: str = None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)
        await member.add_roles(muted_role)
        yellow_log(f'Użytkownik {member} został wyciszony przez {ctx.author}.')
        embed = discord.Embed(title="Użytkownik wyciszony", description=f"{member.mention} został wyciszony przez {ctx.author.mention}.", color=EMBED_COLOR_YELLOW)
        await ctx.send(embed=embed)
        if time:
            seconds = self.parse_time(time)
            if seconds:
                await asyncio.sleep(seconds)
                await member.remove_roles(muted_role)
                yellow_log(f'Użytkownik {member} został odciszony po {time}.')
                embed = discord.Embed(title="Użytkownik odciszony", description=f"{member.mention} został odciszony po {time}.", color=EMBED_COLOR_YELLOW)
                await ctx.send(embed=embed)

    # Komenda do odciszony użytkownika
    @commands.command(name='unmute', help='Odblokuj użytkownika. Użyj: !unmute [użytkownik]')
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            yellow_log(f'Użytkownik {member} został odciszony przez {ctx.author}.')
            embed = discord.Embed(title="Użytkownik odciszony", description=f"{member.mention} został odciszony przez {ctx.author.mention}.", color=EMBED_COLOR_YELLOW)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'Użytkownik {member.mention} nie jest wyciszony. 🔊')


# Funkcja setup, która pozwala zarejestrować cogs w bota
async def setup(bot):
    await bot.add_cog(Moderation(bot))
