import logging
import os
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from datetime import datetime
from threading import Lock

load_dotenv()
ENABLE_LOGS = os.getenv("ENABLE_LOGS").lower() == "true"
INTERVALO_BACKUP_LOGGER = int(os.getenv("INTERVALO_BACKUP_LOGGER", 7))

path_atual = os.path.dirname(os.path.abspath(__file__))
dois_diretorios_acima = os.path.dirname(os.path.dirname(path_atual))

class SingletonLogger:

    _instance = None
    _lock = Lock()


    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SingletonLogger, cls).__new__(cls, *args, **kwargs)
                cls._instance._initialize()
            return cls._instance


    def _initialize(self):
        self.logger = logging.getLogger("SingletonLogger")
        self.logger.setLevel(logging.DEBUG)
        
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"logs_{current_date}.log"
        log_file = os.path.join(dois_diretorios_acima, "logs", filename)
        path = os.path.dirname(log_file)

        if not os.path.exists(path):
            os.makedirs(path)

        handler = TimedRotatingFileHandler(
            log_file, when="midnight", backupCount=INTERVALO_BACKUP_LOGGER, encoding="utf-8"
        )
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)


    def log(self, mode, message):
        if ENABLE_LOGS:
            log_methods = {
                "info": self.logger.info,
                "error": self.logger.error,
                "warning": self.logger.warning,
                "debug": self.logger.debug
            }

            log_method = log_methods.get(mode, self.logger.info)
            log_method(message)

logger = SingletonLogger()