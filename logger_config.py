import sys
import os
from loguru import logger

def configure_logger():
    # Usuń poprzednią konfigurację loggera
    logger.remove()

    # Tworzenie folderu "logs", jeśli nie istnieje
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Dodaj handler do logowania do pliku debug_bot.log tylko dla poziomu DEBUG
    logger.add(
        "logs/debug_bot.log",
        level="DEBUG",
        filter=lambda record: record["level"].name == "DEBUG",
        format="{time} {level} {message}",
        rotation="5 MB",
        retention="7 days",
        colorize=False
    )

    # Dodaj handler do logowania do pliku info_success.log dla poziomu INFO i SUCCESS
    logger.add(
        "logs/info_success.log",
        level="INFO",
        filter=lambda record: record["level"].name in ["INFO", "SUCCESS"],
        format="{time} {level} {message}",
        rotation="5 MB",
        retention="7 days",
        colorize=False
    )

    # Dodaj handler do logowania do pliku warning_error_critical.log dla poziomu WARNING, ERROR i CRITICAL
    logger.add(
        "logs/warning_error_critical.log",
        level="WARNING",
        filter=lambda record: record["level"].name in ["WARNING", "ERROR", "CRITICAL"],
        format="{time} {level} {message}",
        rotation="5 MB",
        retention="7 days",
        colorize=False
    )

    # Dodaj handler do logowania w konsoli z kolorem dla poziomów INFO, SUCCESS, WARNING, ERROR, CRITICAL
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
        colorize=True
    )


# Funkcja do tworzenia prefiksu logów zawierającego nazwę i ID serwera
def guild_log_prefix(ctx):
    guild_name = ctx.guild.name if ctx.guild else "Brak serwera"
    guild_id = ctx.guild.id if ctx.guild else "Brak ID"
    return f"[{guild_name} ({guild_id})]"
