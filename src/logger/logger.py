import logging
import sys
import os

# ANSI escape codes for colors
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BOLD = "\033[1m"

class ColorFormatter(logging.Formatter):
    """A custom formatter to add color to log messages based on level."""

    FORMAT = {
        logging.DEBUG: CYAN + "%(levelname)s: %(name)s - %(message)s" + RESET,
        logging.INFO: GREEN + "%(levelname)s: %(name)s - %(message)s" + RESET,
        logging.WARNING: YELLOW + "%(levelname)s: %(name)s - %(message)s" + RESET,
        logging.ERROR: RED + "%(levelname)s: %(name)s - %(message)s" + RESET,
        logging.CRITICAL: BOLD + RED + "%(levelname)s: %(name)s - %(message)s" + RESET,
    }

    def format(self, record):
        log_fmt = self.FORMAT.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logger(name, log_file=None, level=logging.DEBUG):
    """
    Sets up a logger with colorized output and optional file logging.

    Args:
        name (str): The name of the logger.  Use __name__ for module-specific logging.
        log_file (str, optional): Path to a log file. If None, logs only to the console. Defaults to None.
        level (int, optional): The logging level (e.g., logging.DEBUG, logging.INFO). Defaults to logging.DEBUG.

    Returns:
        logging.Logger: The configured logger instance.
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create handlers
    stream_handler = logging.StreamHandler(sys.stdout) # or sys.stderr
    stream_handler.setFormatter(ColorFormatter())
    logger.addHandler(stream_handler)

    if log_file:
        # Create the directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        # Keep a standard formatter for files.  Less distracting when reading logs.
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Disable propagation to the root logger (optional but often desired)
    logger.propagate = False

    return logger

if __name__ == '__main__':
    # Example Usage
    # Create a logger for the 'my_module' module (or any name you want)
    my_logger = setup_logger(__name__, log_file="my_app.log", level=logging.DEBUG)

    # Log some messages
    my_logger.debug("This is a debug message.")
    my_logger.info("This is an info message.")
    my_logger.warning("This is a warning message.")
    my_logger.error("This is an error message.")
    my_logger.critical("This is a critical message.")

    # Another example, showcasing different parts of the code logging.
    try:
        x = 1 / 0
    except ZeroDivisionError as e:
        my_logger.exception("An exception occurred:") # Logs the exception message *and* the traceback
        # Alternative, if you need to do something else with the exception:
        # my_logger.error("Division by zero occurred.", exc_info=True)
    finally:
        my_logger.info("Finished the example.")