import multiprocessing
from multiprocessing import Manager
import signal


class ProcessPool(object):
    def __init__(self, count, max_task):
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.pool = multiprocessing.Pool(
            processes=count, maxtasksperchild=max_task)
        signal.signal(signal.SIGINT, original_sigint_handler)
        self.pm = Manager()
        self.task_dict = self.pm.dict()

    def apply_async(self, func, args):
        self.pool.apply_async(func, args)

    def terminate(self):
        self.pool.terminate()
        self.pool.close()
        self.pool.join()
