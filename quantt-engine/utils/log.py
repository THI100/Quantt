from loguru import logger
from rich.logging import RichHandler


def setup_logging():
    # 1. Clear default Loguru handler
    logger.remove()

    _ = logger.add(
        RichHandler(rich_tracebacks=True, markup=True),
        format="{message}",  # Rich handles the time/level formatting itself
        level="INFO",
    )

    _ = logger.add(
        "logs/crash_report.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        backtrace=True,
        diagnose=True,
        rotation="00:00",
        retention="1 week",
    )

    # Heavy! 220MB ram and 23MB/s writing, constant usage.

    # # Timeline logging
    # _ = logger.add(
    #     "logs/full_history.log",
    #     level="DEBUG",
    #     rotation="100 MB",
    #     retention="3 days",
    #     compression="zip",
    # )
