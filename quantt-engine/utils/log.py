import sys

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

    # 3. ERROR LOG FILE (The "Black Box")
    # Only records when things break. High detail, long retention.
    _ = logger.add(
        "logs/crash_report.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        backtrace=True,  # Generates the full variable stack
        diagnose=True,  # Shows variable values at time of crash
        rotation="00:00",
        retention="1 week",
    )

    # 4. FULL HISTORY FILE (The "Timeline")
    # Records everything (Info, Debug, Error) but cleans itself up quickly.
    _ = logger.add(
        "logs/full_history.log",
        level="DEBUG",
        rotation="100 MB",
        retention="3 days",
        compression="zip",
    )
