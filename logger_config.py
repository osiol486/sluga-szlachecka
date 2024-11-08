import sys
from loguru import logger

def configure_logger():
    # Usuń poprzednią konfigurację loggera
    logger.remove()

    # Dodaj handler do logowania do pliku bez kolorów
    logger.add(
        "bot.log",
        rotation="30 MB",
        retention="14 days",
        level="INFO",
        format="{time} {level} {message}",
        colorize=False
    )

    # Dodaj handler do logowania w konsoli z kolorami
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
        colorize=True
    )