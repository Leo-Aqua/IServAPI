from .auth import AuthClient
import logging
from logging.handlers import RotatingFileHandler


class Core:
    def __init__(self, username, password, iserv_url):
        """
        Initializes the credentials and URLs needed for accessing the IServ system.

        :param username: str - The username for the IServ system.
        :param password: str - The password for the IServ system.
        :param iserv_url: str - The URL of the IServ system.
        :return: None
        """
        self.username = username
        self._password = password
        self.iserv_url = iserv_url

        # Log in to IServ

        self.auth = AuthClient(self.username, self._password, self.iserv_url)

        self._session = self.auth._session
        self._IServSAT = self.auth._IServSAT
        self._IServSATId = self.auth._IServSATId
        self._IServSession = self.auth._IServSession
        self.__DAVclient = None

    @staticmethod
    def setup_logging(log_file="app.log"):
        """
        Set up a logger with a rotating file handler.

        This function initializes a logger that writes logs to a specified file. It uses
        a rotating file handler to limit the size of each log file to 1 MB and retains
        up to 5 backup copies of the log files.

        Args:
            log_file (str): The path to the log file.
        """

        # Initialize the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Define the format for log messages
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Set up rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,
            backupCount=5,  # Set file size to 1MB and keep 5 backups
        )
        file_handler.setLevel(logging.DEBUG)  # Log all DEBUG and higher level messages
        file_handler.setFormatter(formatter)  # Apply the formatter to the file handler

        # Attach the file handler to the logger
        logger.addHandler(file_handler)

        # Log a message indicating that logging was set up successfully
        logging.info("Logging setup successful!")
