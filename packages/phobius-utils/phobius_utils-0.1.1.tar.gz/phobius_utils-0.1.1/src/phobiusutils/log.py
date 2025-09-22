import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class Log:
    INTERVAL = 1  # 1 day
    FORMATTER = logging.Formatter(
        "%(asctime)s [%(levelname)-8s]> %(message)s", datefmt="%H:%M:%S"
    )

    def __init__(self, name: str):
        """
        Initializes the logger instance.

        Args:
            name (str): Name used for the log file. The log will be saved as <name>.log.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.configureLogging()

    def configureLogging(self, log_dir: str = "", backup_count: int = 1):
        """
        Updates the log directory and configures log rotation.

        Args:
            log_dir (str): Path to the folder where logs will be saved.
                If empty (""), logs will be stored in the current working directory.
                Example: "logs/" or "path/to/log_folder".
            backup_count (int): Number of old log files to retain during log rotation (n>0).
                Default is 1.

        Returns:
            None
        """

        try:
            delay = True if log_dir == "" else False
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / f"{self.logger.name}.log"
            # create handler
            log_handler = TimedRotatingFileHandler(
                log_path,
                delay=delay,
                when="midnight",
                interval=self.INTERVAL,
                backupCount=backup_count,
                encoding="utf-8",
                utc=False,
            )
            # if has old files using rollver to delete and rolling log
            if log_handler.getFilesToDelete():
                log_handler.doRollover()
            log_handler.setFormatter(self.FORMATTER)
            # remove old handler
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
            self.logger.addHandler(log_handler)
        except Exception as e:
            self.critical(f"Log.configureLogging> !{type(e).__name__}! {e}")

    def setLevel(self, level: str):
        """
        Sets the logging level.

        Args:
            level (str): Logging level as a string.
                Accepted values are: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".

        Raises:
            ValueError: If the provided level is not a valid logging level.
        """
        try:
            self.logger.setLevel(level)
        except Exception as e:
            self.critical(f"Log.setLevel> !{type(e).__name__}! {e}")

    def info(self, message: str):
        """
        Logs an informational message with a custom format.

        The format should follow: "ClassNameOrFileName.function_name > message"

        Args:
            message (str): The message to log, typically prefixed with context such as class or function name.
        """
        self.logger.info(message)

    def error(self, message: str):
        """
        Logs an informational message with a custom format.

        The format should follow: "ClassNameOrFileName.function_name > message"

        Args:
            message (str): The message to log, typically prefixed with context such as class or function name.
        """
        self.logger.error(message)

    def debug(self, message: str):
        """
        Logs an informational message with a custom format.

        The format should follow: "ClassNameOrFileName.function_name > message"

        Args:
            message (str): The message to log, typically prefixed with context such as class or function name.
        """
        self.logger.debug(message)

    def warning(self, message: str):
        """
        Logs an informational message with a custom format.

        The format should follow: "ClassNameOrFileName.function_name > message"

        Args:
            message (str): The message to log, typically prefixed with context such as class or function name.
        """
        self.logger.warning(message)

    def critical(self, message: str):
        """
        Logs an informational message with a custom format.

        The format should follow: "ClassNameOrFileName.function_name > message"

        Args:
            message (str): The message to log, typically prefixed with context such as class or function name.
        """
        self.logger.critical(message)


if __name__ == "__main__":
    pass
