import json

from loguru import logger
from rich.logging import RichHandler


def setup_logging(stream_callback=None):
    # 1. Clear default Loguru handler
    logger.remove()

    # Console (Rich)
    logger.add(
        RichHandler(rich_tracebacks=True, markup=True),
        format="{message}",
        level="INFO",
    )

    # File (Error logs)
    logger.add(
        "logs/crash_report.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        backtrace=True,
        diagnose=True,
        rotation="00:00",
        retention="1 week",
    )

    if stream_callback:

        def stream_sink(message):
            record = message.record
            payload = json.dumps(
                {
                    "time": record["time"].strftime("%H:%M:%S"),
                    "level": record["level"].name,
                    "message": record["message"],
                }
            )
            # This calls the broadcast function provided by the API
            stream_callback(payload)

        logger.add(stream_sink, level="INFO")
