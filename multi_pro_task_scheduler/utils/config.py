import configparser
import codecs
from utils.common import Singleton
from confs.settings import setting
from utils.logger import LoggerUtil


logger = LoggerUtil().get_logger()


class Config(Singleton):
    def __init__(self):
        try:
            self.config = configparser.ConfigParser()
            self._set_default_value()
            config_file = setting.CFFile
            self.config.readfp(codecs.open(config_file, "r", "utf-8"))
            # self.config.read_file(config_file)
        except Exception as e:
            logger.exception(e)
        finally:
            logger.debug("Config file is ....")
            logger.debug(self.config)

    def _set_default_value(self):
        add_sec = "pro02"
        self.config.add_section(add_sec)
        self.config.set(add_sec, "uri", "http://127.0.0.1:5000")

    @classmethod
    def get_conf(cls):
        return cls.get_instance().config
