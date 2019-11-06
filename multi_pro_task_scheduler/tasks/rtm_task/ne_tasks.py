import json
from utils.logger import LoggerUtil


class NETasks(object):
    def __init__(self, task_str=None):
        self.logger = LoggerUtil().get_logger()
        self.logger.info("Begin to run the task %s",str(task_str))
        self.task_info = json.loads(task_str)
        self.host_id = self.task_info["hostid"]
        self.run_time = self.task_info["last_run_time"]
        self._init_tasks()

    def _init_tasks(self):
        # prepare
        pass

    def run(self):
        print("this is handle for: %s", self.host_id)
        numbers = [1000000 + x for x in range(20)]
        for number in numbers:
            temp = sum(i * i for i in range(number))
        print(temp)
        print("{} host end".format(self.host_id))
        self.logger.info("Excute the task %s"%self.task_info)
        self.upload_result()

    def upload_result(self):
        print("handle result for {} host".format(self.host_id))
        self.logger.info("upload result finished")
