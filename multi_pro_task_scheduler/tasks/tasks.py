from utils.logger import LoggerUtil
from utils.process.pool import ProcessPool
from tasks.rtm_task.rtm_main_task import EPCMonTask

"""
if you want tou use concurrent.futures:

import use concurrent.futures
self.pool = concurrent.futures.ProcessPoolExecutor(count)

submit task like this: self.pool.submit(abortable_func, task_str)
"""


class Tasks(object):
    def __init__(self, count, max_task):
        self.logger = LoggerUtil().get_logger()
        self.pool = ProcessPool(count, max_task)
        self.tasks = []

    def register_task(self, task_name, **kwargs):
        if task_name not in globals().keys():
            self.logger.error("Register task failed %s " % task_name)
            return
        m_task = globals()[task_name]
        task = m_task(self.pool, **kwargs)
        if task is None:
            return
        else:
            self.tasks.append(task)

    def run_task(self):
        for task in self.tasks:
            task.run()

    def terminate(self):
        self.pool.terminate()
