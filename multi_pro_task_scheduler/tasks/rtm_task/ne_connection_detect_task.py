import json
from utils.logger import LoggerUtil


class NEConnDetectTasks(object):
    def __init__(self, task_str=None):
        self.logger = LoggerUtil().get_logger()
        self.logger.info("Begin to run the task %s",str(task_str))
        self.task_info = json.loads(task_str)
        self.check_time = self.task_info["Time"]

    def run(self):
        print("ne_conn_task run")
