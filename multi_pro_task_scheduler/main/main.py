import os
import time
import sys
from concurrent import futures

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from utils.logger import LoggerUtil
from utils.config import Config
from confs.settings import setting
from utils.process.signal_handler import Gracekiller
from tasks.tasks import Tasks

logger = LoggerUtil().get_logger()

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def do_something_regular():
    try:
        LoggerUtil().re_load_logger()
    except Exception as e:
        logger.error("%s", e.args)


if __name__ == '__main__':
    logger.debug("starting ...")
    config = Config.get_conf()
    process_count = int(config.get("pro01", "process_poll_number"))
    task_per_proc = int(config.get("pro01", "task_per_process"))

    # Start event process pool
    killer = Gracekiller()
    logger.debug('Register grace kill function ')
    tasks = Tasks(process_count, task_per_proc)
    tasks.register_task("EPCMonTask", config=config)
    logger.debug('server starting finished...')

    last_time = 0
    interval = 10
    try:
        while True:
            try:
                if killer.kill_now:
                    tasks.terminate()
                    break

                delta = time.time() - last_time - interval
                if delta < 0:
                    time.sleep(0 - delta)
                    continue
                last_time = time.time()
                tasks.run_task()
                do_something_regular()

            except Exception:
                logger.exception("runing with exception")
    except KeyboardInterrupt:
        logger.exception("key board exception")
    except Exception:
        logger.exception("runing with exception")
    finally:
        tasks.terminate()
