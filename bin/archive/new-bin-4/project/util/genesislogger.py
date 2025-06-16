import os
import logging
from logging.handlers import RotatingFileHandler

class GenesisLogger:

    _instance = None;

    @staticmethod
    def get_instance():
        if GenesisLogger._instance == None:
            GenesisLogger._instance == GenesisLogger()
            print("Initializing Logger Class")
        return GenesisLogger._instance


     # MongoManager constructor to initialize
    def __new__(cls,*args, **kwargs):
        """Creates a new instance of MongoClientPool or returns the existing one."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        self.filename = 'genesislog'
        self.directory = 'logs'
        self.logger = logging.getLogger(self.filename)

        # Create the directory if it doesn't exist
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Create a RotatingFileHandler
        log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file = os.path.join(self.directory, f'{self.filename}.log')
        file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=10 * 1024 * 1024, backupCount=10)
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(logging.INFO)

        # Add the file handler to the logger
        self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def debug(self, message):
        self.logger.debug(message)

