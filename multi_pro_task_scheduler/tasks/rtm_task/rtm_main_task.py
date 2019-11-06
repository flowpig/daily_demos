from functools import partial
import time
from multiprocessing import Manager
import json

from utils.logger import LoggerUtil
from utils.process.timeout import timeout
from utils.process.task import Task
from confs.settings import setting
from tasks.rtm_task.ne_tasks import NETasks
from tasks.rtm_task.ne_connection_detect_task import NEConnDetectTasks
import datetime
import requests


logger = LoggerUtil().get_logger()
KNOWN_HOST = ["Local"]


# @timeout(360)
def epc_worker(task):
    try:
        print(task)
        logger.info('running epc monitor %s'%task)
        task = NETasks(task)
        task.run()
        logger.info("running epc monitor task %s success"%task)
    except Exception as e:
        logger.exception("running epc task %s"%str(e))

# @timeout(600)
def connection_check(task):
    try:
        logger.info('running Connection check task %s'%task)
        task = NEConnDetectTasks(task)
        task.run()
        logger.info('running Connection check task %s done'%task)
    except Exception as e:
        logger.exception("running Connection check task  %s"%str(e))

def epc_monitor_timeout_fun(func, *args):
    try:
        task_str = args[0]
        func(task_str)
    except Exception as e:
        logger.exception("running task %s :%e"%(task_str, str(e)))
    finally:
        return


class EPCMonTask(Task):
    def __init__(self, pool, **kwargs):
        self.pool = pool
        self.pm = Manager()
        self.pm_dict = self.pm.dict()
        self.conf = kwargs["config"]
        self.ser_uri = self.conf.get("pro01", "server")
        self.ser_user = self.conf.get("pro01", "user")
        self.ser_pass = self.conf.get("pro01", "passwd")
        self.last_tasks = []
        self.last_run_time = None
        self.last_conn_check_time = 0
        self.last_check_time = None

    def assign_task(self):
        now = time.time()

        current_minute = int(now / 60)
        if current_minute > self.last_conn_check_time + 1 and (current_minute % 5) == 0:
            logger.debug("Current time %d  last time %d ,begin to check the connection"% \
                         (current_minute, self.last_conn_check_time))
            self.last_conn_check_time = current_minute
            self._assign_conn_task()

        if self.last_check_time is not None and \
                now <= self.last_check_time + 5 * 60:
            return

        self.last_check_time = time.time()
        get_hosts_url = "https://api.myjson.com/bins/18h52g"
        host_ids = []
        hosts_info = requests.get(url=get_hosts_url).json()
        for host_info in hosts_info:
            if host_info["name"] in KNOWN_HOST:
                continue
            if host_info["status"] != '0':
                continue
            host_ids.append(host_info["hostid"])

        run_hosts = self._will_run_hosts(host_ids)
        self.last_run_time = time.time()
        now_s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(run_hosts)
        for hostid in run_hosts:
            tasks = {
                "hostid": hostid,
                "last_run_time": now_s
                 }
            task_str = json.dumps(tasks)
            logger.info("assign task %s" % str(hostid))
            abortable_func = partial(epc_monitor_timeout_fun, epc_worker)
            self.pool.apply_async(abortable_func, args=[task_str])

    def _assign_conn_task(self):
            tasks = {
                "Time":self.last_conn_check_time
            }
            task_str = json.dumps(tasks)
            abortable_func = partial(epc_monitor_timeout_fun, connection_check)
            self.pool.apply_async(abortable_func,args=[task_str])

    def _will_run_hosts(self, host_ids):
        return host_ids

    def run(self):
        self.assign_task()
