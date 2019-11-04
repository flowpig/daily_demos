#!/usr/bin/env python2.7
import os
import time
import sys
from configparser import RawConfigParser
from utils.logger import LoggerUtil
from utils.threadpool import ThreadPool, makeRequests, NoResultsPending
from utils.rtm_api import RtmAPI
from rtm_lib.host_queue import HostQueue


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RTM_CONF = os.path.join(BASE_DIR, "confs", "rtm.cfg")

COLLECT_INTERVAL = 5 * 60
Host_Queue = None
logger = LoggerUtil().get_logger()


def get_host_queue():
    global Host_Queue
    return Host_Queue


def load_host():
    host_queue = get_host_queue()
    host_queue.update_host_queue()


def handle(host):
    try:
        print("this is handle for: %s", host.hostid)
        host.handle_coll()
        logger.debug("Handle host %s host id %s", host.time, host.hostid)
        host_queue = get_host_queue()
        host_summary = "{} summary".format(host.hostid)
    except Exception as e:
        logger.error("Get host %s data failed %s", host.hostid, e.args)
    finally:
        logger.info(
            "Handle host %s result [%s]",
            host.hostid,
            str(host_summary))
        host_queue.put_host_to_queue(host)
        return None


def result_handle(req, result):
    logger.debug("Request task result handle run... ")
    logger.debug("Handle result {}".format(result))


def load_env(rtm_config, process_number, mask):
    global Host_Queue
    rtm_serv = rtm_config.get("rtm_server", "server")
    rtm_user = rtm_config.get("rtm_server", "user")
    rtm_pass = rtm_config.get("rtm_server", "passwd")

    rtm_url = rtm_serv
    connected = False
    count = 20
    while connected == False:
        try:
            rtm = RtmAPI(rtm_url, user=rtm_user, password=rtm_pass)
            connected = True
        except Exception as e:
            if count >= 0:
                logger.exception(e)
                logger.info("Connect RTM server failed %d.Detail: \n%s", count, e.args)
                count = count - 1
                time.sleep(2)
            else:
                raise e
    interval = int(rtm_config.get("collector", "interval"))
    if interval is None or interval < 10:
        interval = 300
    Host_Queue = HostQueue(rtm, interval, process_number, mask)
    load_host()


def do_something_regular():
    try:
        LoggerUtil().re_load_logger()
    except Exception as e:
        logger.error("%s", e.args)


def main_loop(rtm_config, process_number, mask):
    global Host_Queue
    load_env(rtm_config, process_number, mask)

    logger.info("Data Collector started success")
    interval = int(rtm_config.get("collector", "interval"))
    worker_number = rtm_config.get("collector", "max_thread_number")
    thre_poll = ThreadPool(int(worker_number))
    if interval <= 0:
        interval = 5

    load_time = int(time.time())
    while True:
        sleep_time = 0
        count = 0
        hosts = []

        while True:
            host = Host_Queue.get()
            if host is None:
                break
            current_time = int(time.time())
            sleep_time = host.time + int(interval) - current_time
            if (sleep_time > 0):
                Host_Queue.put_host_to_queue(host)
                break
            host.time = host.time + int(interval)
            hosts.append(host)

        try:
            reqs = makeRequests(handle, hosts, result_handle)
            for req in reqs:
                logger.debug("Add request %s ", str(req))
                thre_poll.putRequest(req)

            do_something_regular()
            time.sleep(0.5)
            if (load_time + COLLECT_INTERVAL) < int(time.time()):
                load_host()
                load_time = int(time.time())
                if Host_Queue.check_timeout():
                    logger.error("Main process will exit .....")
                    '''
                    Fast handler.If more clean task needed can add an single to cover it.
                    '''
                    os._exit(1)
            thre_poll.poll()
        except KeyboardInterrupt:
            break
        except NoResultsPending:
            logger.info("Waiting to collect data for new host ...")
            continue
        except Exception as e:
            logger.error("Create request failed %s ", e.args)
            continue

    if thre_poll.dismissedWorkers:
        thre_poll.joinAllDismissedWorkers()


def load_config():
    config = RawConfigParser(allow_no_value=True)
    config.read(RTM_CONF)
    logger.debug("configue item is %s", config.items("rtm_server"))
    return config


if __name__ == '__main__':
    process_number = 1
    mask = 0

    if len(sys.argv) == 3:
        process_number = int(sys.argv[1])
        mask = int(sys.argv[2])
        if process_number <= mask:
            logger.error("input parameter invalid !")
            sys.exit(1)
    config = load_config()

    main_loop(config, process_number, mask)
