import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
from utils import format_datetime

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='avatar', help='Wyświetla avatar użytkownika. Użyj: !avatar <@użytkownik>')
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f'Avatar użytkownika {member}', color=0x00ff00)
        embed.set_image(url=member.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name='serverinfo', help='Wyświetla informacje o serwerze. Użyj: !serverinfo')
    async def server_info(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f'Informacje o serwerze {guild.name}', color=0x00ff00)
        embed.add_field(name='Nazwa serwera', value=guild.name, inline=False)
        embed.add_field(name='ID serwera', value=guild.id, inline=False)
        embed.add_field(name='Właściciel', value=guild.owner, inline=False)
        embed.add_field(name='Liczba użytkowników', value=guild.member_count, inline=False)
        embed.add_field(name='Utworzono', value=format_datetime(guild.created_at), inline=False)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else '')
        await ctx.send(embed=embed)

    @commands.command(name='userinfo', help='Wyświetla informacje o użytkowniku. Użyj: !userinfo <@użytkownik>')
    async def user_info(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f'Informacje o użytkowniku {member}', color=0x00ff00)
        embed.add_field(name='Nazwa', value=member.name, inline=False)
        embed.add_field(name='ID', value=member.id, inline=False)
        embed.add_field(name='Dołączył do serwera', value=format_datetime(member.joined_at), inline=False)
        embed.add_field(name='Konto utworzone', value=format_datetime(member.created_at), inline=False)
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)

# Funkcja setup, która pozwala zarejestrować cogs w bota
async def setup(bot):
    await bot.add_cog(Utility(bot))
