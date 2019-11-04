import time
from random import randint
import threading
from utils.logger import LoggerUtil

try:
    import Queue            # Python 2
except ImportError:
    import queue as Queue   # Python 3


HOST_OUTPUT = ["hostid", "name", "status"]
KNOWN_HOST = ["Zabbix server"]


class Host(object):
    def __init__(self, hostid, rtm_api, interval):
        self.hostid = hostid
        self.rtm_api = rtm_api
        self.interval = interval
        self.time = time.time()

    def __cmp__(self, other):
        if self.time < other.time:
            return -1
        elif self.time == other.time:
            return 0
        else:
            return 1

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def handle_coll(self):
        pass


class HostQueue(object):
    def __init__(self, rtm, interval=300, process_number=1, mask=0):
        self.logger = LoggerUtil().get_logger()
        self.host_queue = Queue.PriorityQueue(maxsize=0)
        self.interval = interval
        self.old_host_ids = []
        self.new_host_ids = []
        self.tem_host_ids = []
        self.deleted_host = []
        self.handleing_hosts = {}
        self.lock = threading.Lock()
        self.rtm = rtm
        self.proc_count = process_number
        self.mask = mask

    def create_new_host(self):
        for hostid in self.new_host_ids:
            if hostid not in self.old_host_ids:
                host = self.create_host(hostid)
                # So that the create time can distribute normally
                host.time = host.time - randint(0, self.interval)
                self.logger.info(
                    "Add a new host %s to queue.time:%s", hostid, str(
                        host.time))
                self.host_queue.put((host.time, host))
                self.old_host_ids.append(host.hostid)

    def find_delete_host(self):
        for hostid in self.old_host_ids:
            if hostid not in self.new_host_ids:
                if hostid not in self.deleted_host:
                    self.logger.debug("Add host %s to delete queue", hostid)
                    self.deleted_host.append(hostid)

    def create_host(self, hostid):
        host = Host(hostid, self.rtm, self.interval)
        return host

    def update_host_queue(self):
        get_hosts_url = "https://api.myjson.com/bins/18h52g"
        self.new_host_ids = []
        hosts_info = self.rtm.req.get(url=get_hosts_url).json()
        for host_info in hosts_info:
            if host_info["name"] in KNOWN_HOST:
                continue
            if host_info["status"] != '0':
                continue
            hid = int(host_info["hostid"])
            if self.proc_count > 1:
                if (hid % self.proc_count) != self.mask:
                    continue
            self.new_host_ids.append(host_info["hostid"])

        if self.old_host_ids == self.new_host_ids:
            return
        self.create_new_host()
        self.find_delete_host()

    def put_host_to_queue(self, host):
        if host.hostid not in self.deleted_host:
            self.host_queue.put((host.time, host))
        else:
            self.deleted_host.remove(host.hostid)
        self.del_handling_host(host.hostid)

    def get(self):
        try:
            host = None
            if self.host_queue.qsize() == 0:
                return None
            host = self.host_queue.get(block=False)[1]
            self.add_handling_host(host.hostid)

        except Exception as e:
            self.logger.error("Get host form hostqueue error: %s", str(e))
            host = None
        finally:
            return host

    def del_handling_host(self, hostid):
        try:
            self.lock.acquire()
            self.handleing_hosts.pop(hostid, None)
        except Exception as e:
            self.logger.error("Delete handling host failed %s", e.args)
        finally:
            self.lock.release()

    def add_handling_host(self, hostid):
        try:
            self.lock.acquire()
            self.handleing_hosts.update({hostid: time.time()})
        except Exception:
            self.logger.error("Add handling host %s", hostid)
        finally:
            self.lock.release()

    def check_timeout(self):
        now = time.time()
        for key in self.handleing_hosts.keys():
            if (self.handleing_hosts[key] + self.interval * 2 + 60) < now:
                self.logger.error("Handling host %s time out", key)
                return 1
        return 0

    def release_queue(self):
        self.host_queue = Queue.PriorityQueue(maxsize=0)
        self.old_host_ids = []
        self.new_host_ids = []
        self.tem_host_ids = []
        self.deleted_host = []

    def size(self):
        return self.host_queue.qsize()
