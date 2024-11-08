import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import openai

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='translate', help='Tłumaczy podane słowo z polskiego na angielski lub odwrotnie przy użyciu diki.pl oraz Merriam-Webster. Użyj: !translate <słowo>')
    async def translate(self, ctx, *, word: str):
        try:
            # Diki.pl - Tłumaczenie słowa oraz przykładowe zdania
            diki_url = f'https://www.diki.pl/slownik-angielskiego?q={word}'
            diki_response = requests.get(diki_url)
            diki_soup = BeautifulSoup(diki_response.text, 'html.parser')

            # Pobieranie tłumaczenia
            translation = diki_soup.find('span', class_='hw')
            translation_text = translation.text if translation else 'Brak tłumaczenia'

            # Pobieranie przykładowych zdań
            example_sentences = diki_soup.find_all('span', class_='exampleSentence')
            examples = []
            for sentence in example_sentences[:2]:
                examples.append(sentence.text.strip())

            diki_translation_info = f'Tłumaczenie dla "{word}": {translation_text}\n'
            if examples:
                diki_translation_info += "\nPrzykłady zdań z diki.pl:\n"
                for example in examples:
                    diki_translation_info += f'- {example}\n'

            # Merriam-Webster - Definicja słowa oraz przykładowe zdania
            mw_url = f'https://www.merriam-webster.com/dictionary/{word}'
            mw_response = requests.get(mw_url)
            mw_soup = BeautifulSoup(mw_response.text, 'html.parser')

            # Pobieranie definicji
            definition = mw_soup.find('span', class_='dtText')
            definition_text = definition.text.strip() if definition else 'Brak definicji'

            # Pobieranie przykładowych zdań
            mw_examples = mw_soup.find_all('span', class_='ex-sent')
            mw_example_sentences = []
            for example in mw_examples[:2]:
                mw_example_sentences.append(example.text.strip())

            mw_translation_info = f'Definicja z Merriam-Webster dla "{word}": {definition_text}\n'
            if mw_example_sentences:
                mw_translation_info += "\nPrzykłady zdań z Merriam-Webster:\n"
                for example in mw_example_sentences:
                    mw_translation_info += f'- {example}\n'

            # Wysyłanie wiadomości z tłumaczeniem, definicją i przykładami
            await ctx.send(f'{diki_translation_info}\n{mw_translation_info}')
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
