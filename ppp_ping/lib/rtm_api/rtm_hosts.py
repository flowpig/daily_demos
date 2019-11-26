from lib.utils.logger import Logger
from rtm_api import RtmAPI
logger = Logger.get_logger();
KNOWN_HOST = ["Zabbix server"]
HOST_OUTPUT = ["hostid","name","status"]

class RTMHosts(object):
    
    def __init__(self,**kwargs):
        self.hosts = []
        self.logger = Logger.get_logger()
        self.rtm_api = None
        self._create_rtm_api(**kwargs)
        self.host_ids = []
        return

    def _create_rtm_api(self,**kwargs):
        try:
            rtm = RtmAPI(**kwargs)
            self.rtm_api = rtm
        except Exception as e:
            logger.exception(e)
        return 


    def get_host_ids(self):
        self.host_ids = []
        hosts_info = self.rtm_api.host.get(filter={"status":"0"},output=HOST_OUTPUT)
        for host_info in hosts_info:
            if host_info["name"] in KNOWN_HOST:
                continue
            if host_info["status"] != '0':
                continue
            self.host_ids.append(host_info["hostid"])
        return self.host_ids




