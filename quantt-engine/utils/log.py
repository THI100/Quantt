import sys

from loguru import logger


def setup_logging():
    logger.remove()

    logger.add(sys.stderr, level="INFO")

    # Create a specific log file for Errors/Critical issues only
    logger.add(
        "error_logs/crash_report.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="10 MB",
        retention="10 days",
        compression="zip",
    )


if __name__ == "__main__":
    setup_logging()
