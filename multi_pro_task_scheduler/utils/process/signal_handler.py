from utils.logger import LoggerUtil


class Gracekiller(object):
    logger = LoggerUtil().get_logger()
    kill_now = False

    def __init__(self):
        pass

    def exit_gracefully(self, signum, frame):
        self.kill_now = True
        self.logger.error('Get a singal process [%d] will exit ' % signum)
