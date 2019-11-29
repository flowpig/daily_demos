#!/usr/bin/python
# -*- coding: utf-8 -*-


#import sys
#sys.path.append("../..")
import subprocess
import datetime
import re
from collections import defaultdict
import pymysql
import json

try:
    import Queue  # Python 2
except ImportError:
    import queue as Queue  # Python 3

from lib.rtm_api.rtm_api import RTMAPI
from lib.utils.logger import Logger
import time
from lib.utils.threadpool import makeRequests, ThreadPool, NoResultsPending
from threading import Thread
from device.device import Device


MYSQL_USER = "rtm"
MYSQL_PWD = "rtmPassword123"
MYSQL_DB = "rtm"
MYSQL_PORT = 3306
MYSQL_HOST = "127.0.0.1"
MATCH_IP_CMD = 'show service id {0} ppp session | match  expression "sap|local" max-count {1}'
PING_MAPPER = {
    1: "fping -q -c 4 -i 1 {0}",
    2: "fping -q -c 4 {0}"
}

MACRO_MAPPER = {
    "ppp_service_id": "{$PPP_SERVICE_ID}",
    "login_info": "{$PROTOCOL}"
}

logger = Logger.get_logger()


def ppp_run(schema, users, hostids):
    with PingProcess(schema, users, hostids) as run:
        run()


class DBConnectionManager:
    def __init__(self, host, port, user, pwd, db):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db
        self.connection = None
        self.cur = None

    def __enter__(self):
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.pwd,
            db=self.db)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        self.connection.close()


class PingProcess(object):
    def __init__(self, schema, users, hostids):
        self.schema = schema
        self.users = users
        self.hostids = hostids
        self.logger = logger
        self.result_data = {}
        self.rtm_api = RTMAPI.get_api()
        self.host_ip_q = Queue.Queue()
        self.time_str = str(datetime.datetime.now()).split('.')[0]
        self.err_hosts = []
        self.Count = 0

    def _get_ips(self, hostid):
        try:
            macro_res = self._get_host_macros(hostid)
            login_info = macro_res[MACRO_MAPPER["login_info"]]
            ppp_service_id = macro_res[MACRO_MAPPER["ppp_service_id"]]
            device = Device(login_info)
            match_ip_cmd = MATCH_IP_CMD.format(
                ppp_service_id, self.users * 2 + 200)
            match_ip_cmd = "show ppp session"
            result = device.run_cmd(match_ip_cmd)
            ip_vlan_map = self._parse_ppp_ip(result, self.users)
            self.host_ip_q.put((hostid, ip_vlan_map))
        except Exception as e:
            self.err_hosts.append(hostid)
            self.logger.error("**** Exception occured for hostid #%s: %s" %
                          (hostid, str(e)))

    def _parse_ppp_ip(self, result, users):
        res = re.findall(r"(s.*?)mac.*?(\d+\.\d+\.\d+\.\d+)", result, re.S)
        lag_set = set(list(map(lambda x: x[0].split(':')[2][1:], res)))
        count_dic = defaultdict(int)
        res_dic = {x[1].strip(): x[0].strip() for x in res}
        ips = []
        per, rest = divmod(users, len(lag_set))
        per_all = users - rest
        if rest == users:
            per_all = users
            rest = 0
        for ip, ser in res_dic.items():
            if per_all == 0 and rest == 0:
                break
            lag = ser.split(':')[2][1:]
            if count_dic[lag] <= per:
                ips.append(ip)
                count_dic[lag] += 1
                per_all -= 1
            elif rest > 0:
                ips.append(ip)
                rest -= 1
        res_dic = dict(filter(lambda x: x[0] in ips, list(res_dic.items())))
        return json.dumps(res_dic)

    def _open_tmp(self, service):
        #up_sql = """UPDATE running_tmp set flag=1 WHERE service='{0}'""".format(
        #    service)
        in_sql = """INSERT INTO running_tmp (service, flag) values('{0}', 1)""".format(
            service)
        with DBConnectionManager(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DB) as db_client:
            cur = db_client.connection.cursor()
            db_client.cur = cur
            cur.execute(in_sql)
            db_client.connection.commit()

    def _close_tmp(self, service):
        #up_sql = """UPDATE running_tmp set flag=0 WHERE service='{0}'""".format(
        #    service)
        del_sql = """DELETE FROM running_tmp WHERE service='{0}'""".format(
            service)
        with DBConnectionManager(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DB) as db_client:
            cur = db_client.connection.cursor()
            db_client.cur = cur
            cur.execute(del_sql)
            db_client.connection.commit()

    def get_ips_scheduler(self):
        for hostid in self.hostids:
            Thread(target=self._get_ips, args=(hostid, )).start()
    
    def _handle_count(self, request, result):
        self.Count += 1

    def main_loop(self):
        worker = 10
        if len(self.hostids) < worker:
            worker = len(self.hostids)
        pool = ThreadPool(worker)
        count = 0
        while self.Count < len(self.hostids) - len(self.err_hosts):

            while True:
                if count == len(self.hostids) - len(self.err_hosts):
                    break
                time.sleep(0.3)
                # host is like (10010, '{"192.168.0.2": vlan1, "127.0.0.1": "vlan2"}')
                try:
                    host = self.host_ip_q.get(block=False)
                except Exception:
                    continue
                count += 1
                #print(host)
                req_data = [(host, {})]
                reqs = makeRequests(
                    self._run_ping,
                    req_data,
                    callback=self._handle_count,
                    exc_callback=self._handle_exception)
                for req in reqs:
                    #print("Add request %s ", str(req))
                    pool.putRequest(req)
            try:
                time.sleep(0.5)
                pool.poll()
            except KeyboardInterrupt:
                break
            except NoResultsPending:
                logger.info("Waiting to run ping for new host ...")
                continue
            except Exception as e:
                print(e)
                logger.error("Create request failed %s ", e.args)
                continue

        if pool.dismissedWorkers:
            pool.joinAllDismissedWorkers()

    def __enter__(self):
        self._open_tmp("ppp_subscribers_ping")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_tmp("ppp_subscribers_ping")

    def _run_ping(self, *req_data):
        hostid = req_data[0]
        ip_vlan_map = json.loads(req_data[1])
        ip_list = list(ip_vlan_map.keys())
        ips = ' '.join(ip_list)
        fping_cmd = PING_MAPPER[self.schema].format(ips)
        proc = subprocess.Popen(fping_cmd, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.poll()
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        all_str = stdout + stderr
        self._hand_ping_result(hostid, all_str, ip_vlan_map)

    def _hand_ping_result(self, hostid, fping_result, ip_vlan_map):
        fping_res = re.findall(
            r"(\d+\.\d+\.\d+\.\d+).*?xmt/rcv/%loss\s+=\s+(\d+)/(\d+)/(\d+)%(?:,.*?min/avg/max\s+=\s+([0-9\.]+)/([0-9\.]+)/([0-9\.]+)|)",
            fping_result, re.S)
        fping_res = [[hostid, ip_vlan_map[r[0]], r[0], r[1], r[2], r[3], r[4] if r[4] else 0, r[5] if r[5] else 0, r[6] if r[6] else 0, self.time_str]
                     for r in fping_res]
        #print(fping_res)
        with DBConnectionManager(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DB) as db_client:
            cur = db_client.connection.cursor()
            db_client.cur = cur
            inser_sql = """INSERT INTO ppp_subscribers_ping (hostid, vlan, target_ip, sent_packs, recv_packs, loss, min_delay, avg_delay, max_delay, run_time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cur.executemany(inser_sql, fping_res)
            db_client.connection.commit()

    def _handle_exception(self, request, exc_info):
        if not isinstance(exc_info, tuple):
            # Something is seriously wrong...
            self.logger.error(exc_info)
            raise SystemExit
        self.Count += 1
        self.logger.error("**** Exception occured in request #%s: %s" %
                          (request.requestID, exc_info))

    def __call__(self, *args, **kwargs):
        self.get_ips_scheduler()
        time.sleep(1)
        self.main_loop()

    def _get_host_macros(self, hostid):
        search = {
            'selectMacros': ["macro", "value"],
            'hostids': hostid
        }
        res = self.rtm_api.host.get(**search)
        return {data["macro"]: data["value"] for data in res[0]["macros"]}


if __name__ == '__main__':
    with PingProcess(1, 5, [10117,10118,13029,13034,13037,13040]) as pro:
        pro()
        print("end")


