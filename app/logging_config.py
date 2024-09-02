from loguru import logger

logger.remove()

logger.add(
    "instance/error.log",
    format="{time} {level} {message}",
    level="ERROR",
    filter=lambda record: record["level"].name == "ERROR",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
)

logger.add(
    "instance/toolkit.log",
    format="{time} {level} {message}",
    filter=lambda record: record["level"].name == "INFO",
    level="INFO",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
)

loguru_logger = logger
