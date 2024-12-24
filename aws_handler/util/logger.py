from logging.handlers import RotatingFileHandler
import logging


# Define color codes for different log levels
LOG_COLORS = {
    # Green
    "DEBUG": "\033[32m",
    # Blue
    "INFO": "\033[34m",
    # Yellow
    "WARNING": "\033[33m",
    # Red
    "ERROR": "\033[31m",
    # Magenta
    "CRITICAL": "\033[35m",
}

# Define color reset code
LOG_COLOR_RESET = "\033[0m"


def setup_logger(name, info_only=True):
    if info_only:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # Custom log formatting based on log level
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                levelname = record.levelname
                record.levelname = (
                    f"{LOG_COLORS.get(levelname, '')}{levelname}"
                    f"{LOG_COLOR_RESET}"
                )
                return super().format(record)

        colored_formatter = ColoredFormatter(
            fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
        )
        stream_handler.setFormatter(colored_formatter)

        logger.addHandler(stream_handler)
    else:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
        )

        loghdl = RotatingFileHandler(name + ".log")
        loghdl.setLevel(logging.DEBUG)
        loghdl.setFormatter(formatter)
        logger.addHandler(loghdl)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # Custom log formatting based on log level
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                levelname = record.levelname
                record.levelname = (
                    f"{LOG_COLORS.get(levelname, '')}{levelname}"
                    f"{LOG_COLOR_RESET}"
                )
                return super().format(record)

        colored_formatter = ColoredFormatter(
            fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
        )
        stream_handler.setFormatter(colored_formatter)

        logger.addHandler(stream_handler)

    return logger


# Set up the logger only once
log = logging.getLogger("aws-handler")
if not log.handlers:
    setup_logger(name="aws-handler")
