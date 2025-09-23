import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Create and configure a stream logger for console output.

    Args:
        name (str): Name for the logger.

    Returns:
        logging.Logger: Configured logger instance with StreamHandler.
    """
    # Logger configuration
    logger = logging.getLogger(name=name)

    # Sets log level to INFO
    logger.setLevel(level=logging.INFO)

    # Clears existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Disable propagation to prevent double logging
    logger.propagate = False
    
    # Custom formatter
    formatter = logging.Formatter(fmt="%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # Stream handler for console output
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(level=logging.INFO)
    handler.setFormatter(fmt=formatter)
    logger.addHandler(hdlr=handler)

    # Suppress py4j logger to reduce noise
    logging.getLogger(name="py4j").setLevel(level=logging.WARNING)

    return logger
