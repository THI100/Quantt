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


# ------------------------ Special for Uvicorn on Production ------------------------ #

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelprefix)s %(message)s",
            "()": "uvicorn.logging.DefaultFormatter",
            "use_colors": False,
        },
        "access": {
            "format": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            "()": "uvicorn.logging.AccessFormatter",
            "use_colors": False,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
