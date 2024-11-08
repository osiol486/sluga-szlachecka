# role_management/bot_roles.py
import discord
from discord.ext import commands

async def check_and_assign_role(bot: commands.Bot, guild: discord.Guild):
    # Sprawdź, czy bot ma już określoną rolę
    bot_role_name = "Bot Helper"
    existing_role = discord.utils.get(guild.roles, name=bot_role_name)

    # Jeśli nie ma roli, utwórz ją
    if existing_role is None:
        try:
            new_role = await guild.create_role(name=bot_role_name, permissions=discord.Permissions.general(), color=discord.Color.blue())
            await bot.user.add_roles(new_role)
            print(f"Stworzono nową rolę i przypisano ją botowi: {new_role.name}")
        except discord.Forbidden:
            print("Brak uprawnień do tworzenia nowych ról.")
        except discord.HTTPException as e:
            print(f"Wystąpił błąd podczas tworzenia roli: {e}")
    else:
        print(f"Rola {bot_role_name} już istnieje.")