import os
import ConfigParser

from lib.utils.singleton import Singleton
from utils.const import const
from lib.utils.logger import Logger


logger = Logger.get_logger()


class SRServiceConf(Singleton):
    def __init__(self):
        try:
            self.config = ConfigParser.ConfigParser()
            self._set_default_value()
            logger.debug(self.config.sections())
            logger.debug(self.config.defaults())
            parentdir =os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_file = parentdir + const.CFFile
            with open(config_file) as conf_file:
                self.config.readfp(conf_file)
        except Exception as e:
            logger.exception(e)
        finally:
            logger.debug("Config file is ....")
            logger.debug(self.config)

    def _set_default_value(self):
        self.config.add_section(const.CFSR)
        self.config.set(const.CFDE, const.CFSer,
                        "http://127.0.0.1/service_robot")
        self.config.set(const.CFDE, const.CFUser,      "api_access")
        self.config.set(const.CFDE, const.CFPass,      "123api_access!@#")
        self.config.set(const.CFDE, const.TRAPPERIP,   "127.0.0.1")
        self.config.set(const.CFDE, const.TRAPPERPORT, "10051")
        self.config.set(const.CFDE, const.GRPCWORKER,  "100")
        # default ip and port info for the service event handle
        self.config.set(const.CFDE, const.SREVENTSER, '[::]:50052')

        self.config.set(const.CFDE, const.PROCPOLLCOUT, "5")
        self.config.set(const.CFDE, const.TASKPERPROCESS, "10")

        self.config.set(const.CFDE, const.CFBAKETIME, "* 04 * * *")
        self.config.set(const.CFDE, const.CONFFD, const.ConfBakeFolder)
        self.config.set(const.CFDE, const.BAKEMD, "CMD")

    @classmethod
    def get_conf(cls):
        return cls.get_instance().config


