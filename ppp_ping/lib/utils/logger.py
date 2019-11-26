import sys
import os
import logging
import logging.config

CONFIG_DIR ="/conf/"
LOG_NAME = "monitor_out_log"


class Logger(object):
    logger = None
    last_modify_time = 0

    @classmethod
    def get_logger(self):
        if self.logger is not None:
            return self.logger
        parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parentdir = os.path.dirname(parentdir)
        self.last_modify_time = os.path.getmtime(parentdir + CONFIG_DIR + "log.cfg")
        logging.config.fileConfig(parentdir + CONFIG_DIR+"log.cfg")
        self.logger =  logging.getLogger(LOG_NAME)
        self.logger.propagate = False
        return self.logger

    @classmethod
    def re_load_logger(self):
        parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parentdir = os.path.dirname(parentdir)
        current_modify_time = os.path.getmtime(parentdir + CONFIG_DIR + "log.cfg")
        if self.last_modify_time == current_modify_time:
            return
        self.last_modify_time = os.path.getmtime(parentdir + CONFIG_DIR + "log.cfg")
        logging.config.fileConfig(parentdir + CONFIG_DIR+"log.cfg")
        self.logger =  logging.getLogger(LOG_NAME)
        self.logger.propagate = False
        return

    @classmethod
    def set_level(cls,logger,level):
        logger.setLevel(level)
        for i in range(len(logger.handlers)):
            logger.handlers[i].level = level

