import os
import logging
from cloghandler import ConcurrentRotatingFileHandler
import logging.config

CONFIG_DIR = "confs"
LOG_NAME = "process_out_log"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_CONF_PATH = os.path.join(BASE_DIR, CONFIG_DIR, "log.cfg")


class LoggerUtil(object):

    def __init__(self, log_conf_path=LOG_CONF_PATH):
        self.logger = None
        self.last_modify_time = 0
        self.log_conf_path = log_conf_path

    def get_logger(self):
        if self.logger is not None:
            return self.logger

        self.last_modify_time = os.path.getmtime(self.log_conf_path)
        logging.config.fileConfig(self.log_conf_path)
        self.logger = logging.getLogger(LOG_NAME)
        self.logger.propagate = False
        return self.logger

    def re_load_logger(self):
        current_modify_time = os.path.getmtime(self.log_conf_path)
        if self.last_modify_time == current_modify_time:
            return
        self.last_modify_time = os.path.getmtime(self.log_conf_path)
        logging.config.fileConfig(self.log_conf_path)
        self.logger = logging.getLogger(LOG_NAME)
        self.logger.propagate = False
