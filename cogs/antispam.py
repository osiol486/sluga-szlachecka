import time
from collections import defaultdict
from discord.ext import commands

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_usage = defaultdict(list)  # Śledzenie użycia komend przez użytkowników
        self.spam_timeout = defaultdict(lambda: 0)  # Czas blokady użytkowników po spamowaniu

    def is_spamming(self, user_id):
        now = time.time()
        # Usuwanie starych wpisów (starszych niż 10 sekund)
        self.command_usage[user_id] = [timestamp for timestamp in self.command_usage[user_id] if now - timestamp < 10]
        return len(self.command_usage[user_id]) > 5  # Limit: więcej niż 5 komend w ciągu 10 sekund

    @commands.Cog.listener()
    async def on_command(self, ctx):
        user_id = ctx.author.id
        now = time.time()
        # Sprawdź, czy użytkownik jest obecnie w stanie blokady
        if now < self.spam_timeout[user_id]:
            await ctx.send(f"{ctx.author.mention}, jesteś obecnie zablokowany za spamowanie komendami. Poczekaj kilka sekund. 🛑")
            return
        
        self.command_usage[user_id].append(now)
        if self.is_spamming(user_id):
            await ctx.send(f"{ctx.author.mention}, proszę przestań spamować komendami. Zostałeś zablokowany na 10 sekund. 🛑")
            # Zablokuj użytkownika na 10 sekund
            self.spam_timeout[user_id] = now + 10

    
async def setup(bot):
    await bot.add_cog(AntiSpam(bot))