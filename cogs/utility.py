import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import openai

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='translate', help='Tłumaczy podane słowo z polskiego na angielski lub odwrotnie przy użyciu diki.pl. Użyj: !translate <słowo>')
    async def translate(self, ctx, *, word: str):
        try:
            url = f'https://www.diki.pl/slownik-angielskiego?q={word}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Pobieranie pierwszego wyniku tłumaczenia
            translation = soup.find('span', class_='hw').text

            if translation:
                await ctx.send(f'Tłumaczenie dla "{word}": {translation}')
            else:
                await ctx.send(f'Nie znaleziono tłumaczenia dla "{word}" na diki.pl')
        except Exception as e:
            await ctx.send(f'Wystąpił błąd podczas tłumaczenia: {str(e)}')

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
        embed.add_field(name='Utworzono', value=guild.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else '')
        await ctx.send(embed=embed)

    @commands.command(name='userinfo', help='Wyświetla informacje o użytkowniku. Użyj: !userinfo <@użytkownik>')
    async def user_info(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f'Informacje o użytkowniku {member}', color=0x00ff00)
        embed.add_field(name='Nazwa', value=member.name, inline=False)
        embed.add_field(name='ID', value=member.id, inline=False)
        embed.add_field(name='Dołączył do serwera', value=member.joined_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        embed.add_field(name='Konto utworzone', value=member.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)

# Funkcja setup, która pozwala zarejestrować cogs w bota
async def setup(bot):
    await bot.add_cog(Utility(bot))
