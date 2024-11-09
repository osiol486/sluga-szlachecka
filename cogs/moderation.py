import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import asyncio
from loguru import logger
from colorama import Fore, Style
from utils.utils import parse_time, parse_minutes_seconds
from utils.constants import ERROR_NO_PERMISSION_USER, ERROR_NO_PERMISSION_BOT, EMBED_COLOR_RED, EMBED_COLOR_YELLOW

# Funkcja logująca wiadomości na żółto z informacją o serwerze
def yellow_log(ctx, message, level="INFO"):
    guild_info = f"[{ctx.guild.name} ({ctx.guild.id})]" if ctx.guild else "[Brak serwera]"
    log_message = f"{guild_info} {message}"  # Nie dodawaj kolorów, które mogą być problematyczne w logach plikowych

    if level == "DEBUG":
        logger.debug(log_message)
    else:
        logger.info(log_message)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Komenda do zbanowania użytkownika
    @commands.command(name='ban', help='Zbanuj użytkownika na określony czas. Użyj: !ban [użytkownik] [czas (np. 1h, 1d)]')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, time: str = None, *, reason=None):
        # Sprawdź, czy użytkownik wykonujący komendę ma uprawnienia do banowania
        if not ctx.author.guild_permissions.ban_members:
            await ctx.send(ERROR_NO_PERMISSION_USER)
            return
        # Sprawdź, czy podano użytkownika do zbanowania
        if not member:
            await ctx.send(f"{ctx.author.mention}, musisz podać użytkownika, którego chcesz zbanować.")
            return
        # Sprawdź, czy użytkownik próbujący zbanować siebie samego
        if member == ctx.author:
            await ctx.send(f"{ctx.author.mention}, nie możesz zbanować samego siebie.")
            return
        # Sprawdź, czy użytkownik próbujący zbanować bota
        if member == ctx.guild.me:
            await ctx.send(f"{ctx.author.mention}, nie możesz zbanować bota.")
            return
        # Spróbuj zbanować użytkownika
        try:
            await member.ban(reason=reason)
            yellow_log(ctx, f'[{ctx.guild.name} ({ctx.guild.id})] Użytkownik {member} został zbanowany przez {ctx.author}. Powód: {reason}')
            
            embed = discord.Embed(
                title="Użytkownik zbanowany",
                description=f"{member.mention} został zbanowany przez {ctx.author.mention}.",
                color=EMBED_COLOR_RED
            )
            if reason:
                embed.add_field(name="Powód", value=reason, inline=False)
            await ctx.send(embed=embed)
            # Obsługa czasowego bana
            if time:
                seconds = parse_time(time)
                if seconds:
                    await asyncio.sleep(seconds)
                    await ctx.guild.unban(member)
                    yellow_log(ctx, f'Użytkownik {member} został odbanowany po {time}.')
                    
                    embed = discord.Embed(
                        title="Użytkownik odbanowany",
                        description=f"{member.mention} został odbanowany po {time}.",
                        color=EMBED_COLOR_YELLOW
                    )
                    await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(ERROR_NO_PERMISSION_BOT)
        except discord.HTTPException as e:
            await ctx.send(f"Wystąpił błąd podczas próby banowania: {str(e)}")

    # Komenda do wyrzucenia użytkownika
    @commands.command(name='kick', help='Wyrzuć użytkownika z serwera. Użyj: !kick [użytkownik]')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        yellow_log(ctx, f'[{ctx.guild.name} ({ctx.guild.id})] Użytkownik {member} został wyrzucony z serwera przez {ctx.author}. Powód: {reason}')
        embed = discord.Embed(title="Użytkownik wyrzucony", description=f"{member.mention} został wyrzucony z serwera przez {ctx.author.mention}.", color=EMBED_COLOR_YELLOW)
        if reason:
            embed.add_field(name="Powód", value=reason, inline=False)
        await ctx.send(embed=embed)

    # Komenda do mutowania
    @commands.command(name='mute', help='Wycisz użytkownika na określony czas. Użyj: !mute [użytkownik] [czas (np. 1h, 1d)]')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, time: str = None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)
        
        await member.add_roles(muted_role)
        if time:
            seconds = parse_time(time)
            if seconds:
                yellow_log(ctx, f'Użytkownik {member} został wyciszony przez {ctx.author} na {time}.')
                embed = discord.Embed(
                    title="Użytkownik wyciszony", 
                    description=f"{member.mention} został wyciszony przez {ctx.author.mention} na {time}.", 
                    color=EMBED_COLOR_YELLOW
                )
                # Stwórz niezależne zadanie, aby rozmutować użytkownika po określonym czasie
                async def unmute_after():
                    await asyncio.sleep(seconds)
                    if muted_role in member.roles:
                        await member.remove_roles(muted_role)
                        yellow_log(ctx, f'Użytkownik {member} został odciszony po {time}.')
                        embed_unmute = discord.Embed(
                            title="Użytkownik odciszony", 
                            description=f"{member.mention} został odciszony po {time}.", 
                            color=EMBED_COLOR_YELLOW
                        )
                        await ctx.send(embed=embed_unmute)

                # Tworzymy zadanie w pętli zdarzeń bota, które wykona się po określonym czasie
                ctx.bot.loop.create_task(unmute_after())
            else:
                # Jeśli nie udało się przetworzyć czasu
                yellow_log(ctx, f'Użytkownik {member} został wyciszony przez {ctx.author}, ale podano nieprawidłowy czas.')
                embed = discord.Embed(
                    title="Użytkownik wyciszony", 
                    description=f"{member.mention} został wyciszony przez {ctx.author.mention}.", 
                    color=EMBED_COLOR_YELLOW
                )
        else:
            # Brak określonego czasu
            yellow_log(ctx, f'Użytkownik {member} został wyciszony przez {ctx.author}.')
            embed = discord.Embed(
                title="Użytkownik wyciszony", 
                description=f"{member.mention} został wyciszony przez {ctx.author.mention}.", 
                color=EMBED_COLOR_YELLOW
            )
        
        await ctx.send(embed=embed)

    # Komenda do odciszenia użytkownika
    @commands.command(name='unmute', help='Odblokuj użytkownika. Użyj: !unmute [użytkownik]')
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            yellow_log(ctx, f'Użytkownik {member} został odciszony przez {ctx.author}.')
            embed = discord.Embed(title="Użytkownik odciszony", description=f"{member.mention} został odciszony przez {ctx.author.mention}.", color=EMBED_COLOR_YELLOW)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'Użytkownik {member.mention} nie jest wyciszony. 🔊')

    # Komenda do usuwania wiadomości
    @commands.command(name='purge', help='Usuń wiadomości. Możesz użyć filtrów, takich jak -images, -bots, etc.')
    @has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int, *filters):
        def check(message):
            result = True
            if '-bots' in filters:
                result = result and message.author.bot
            if '-users' in filters:
                result = result and not message.author.bot
            if '-links' in filters:
                result = result and any(substring in message.content for substring in ['http://', 'https://'])
            if '-invites' in filters:
                result = result and 'discord.gg' in message.content
            if '-embeds' in filters:
                result = result and bool(message.embeds)
            if '-images' in filters:
                result = result and any(attachment.filename.lower().endswith(('jpg', 'jpeg', 'png', 'gif')) for attachment in message.attachments)
            if '-files' in filters:
                result = result and any(not attachment.filename.lower().endswith(('jpg', 'jpeg', 'png', 'gif')) for attachment in message.attachments)
            if '-mentions' in filters:
                result = result and bool(message.mentions)
            if '-pins' not in filters:
                result = result and not message.pinned
            return result

        deleted = await ctx.channel.purge(limit=limit, check=check)
        if '-silent' not in filters:
            await ctx.send(f'Usunięto **{len(deleted)}** wiadomości. 🧹', delete_after=5)

        # Logowanie informacji o użyciu komendy purge
        yellow_log(ctx, f'Komenda "purge" została użyta przez {ctx.author} w kanale #{ctx.channel}. Usunięto {len(deleted)} wiadomości.')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(ERROR_NO_PERMISSION_USER)


# Funkcja setup, która pozwala zarejestrować cogs w bota
async def setup(bot):
    await bot.add_cog(Moderation(bot))
