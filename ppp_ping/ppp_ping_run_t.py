#!/usr/bin/python
# -*- coding: utf-8 -*-


import subprocess
import datetime
import re
from collections import defaultdict
import pymysql
# from lib.rtm_api.rtm_api import RTMAPI
from lib.utils.logger import Logger
import time
from lib.utils.threadpool import makeRequests, ThreadPool, NoResultsPending
import threading
from threading import Thread
from device.device import Device


MYSQL_USER = "inspect"
MYSQL_PWD = "inspect"
MYSQL_DB = "inspect_ppp"
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
    pass


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
        # self.rtm_api = RTMAPI.get_api()
        self.rtm_api = api
        self.host_ip_q = Queue.Queue()
        self.time_str = str(datetime.datetime.now()).split('.')[0]

    def _get_ips(self, hostid):
        self.host_ip_q.put((10010, json.dumps(IP_VLAN_MAP)))
        return
        macro_res = self._get_host_macros(hostid)
        login_info = macro_res[MACRO_MAPPER["login_info"]]
        ppp_service_id = macro_res[MACRO_MAPPER["ppp_service_id"]]
        device = Device(login_info)
        match_ip_cmd = MATCH_IP_CMD.format(
            ppp_service_id, self.users * 2 + 200)
        result = device.run_cmd(match_ip_cmd)
        ip_vlan_map = self._parse_ppp_ip(result, self.users)
        self.host_ip_q.put((hostid, ip_vlan_map))

    def _parse_ppp_ip(self, result, users):
        res = re.findall(r"(s.*?)mac.*?(\d+\.\d+\.\d+\.\d+)", result, re.S)
        lag_set = set(list(map(lambda x: x[0].split(':')[2][1:], res)))
        count_dic = defaultdict(int)
        res_dic = {x[1].strip(): x[0].strip() for x in res}
        ips = []
        per, rest = divmod(users, len(lag_set))
        per_all = users - rest
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
        up_sql = """UPDATE running_tmp set flag=1 WHERE service='{0}'""".format(service)
        with DBConnectionManager(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DB) as db_client:
            cur = db_client.connection.cursor()
            db_client.cur = cur
            cur.execute(up_sql)
            db_client.connection.commit()

    def _close_tmp(self, service):
        up_sql = """UPDATE running_tmp set flag=0 WHERE service='{0}'""".format(service)
        with DBConnectionManager(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DB) as db_client:
            cur = db_client.connection.cursor()
            db_client.cur = cur
            cur.execute(up_sql)
            db_client.connection.commit()

    def get_ips_scheduler(self):
        for hostid in self.hostids:
            Thread(target=self._get_ips, args=(hostid, )).start()

    def _handle_count(self, request, result):
        L.Count += 1

    def main_loop(self):
        worker = 20
        if len(self.hostids) < worker:
            worker = len(self.hostids)
        pool = ThreadPool(worker)
        count = 0
        while L.Count < len(self.hostids):

            while True:
                if count == len(self.hostids):
                    break
                time.sleep(0.3)
                # host is like (10010, '{"192.168.0.2": vlan1, "127.0.0.1": "vlan2"}')
                try:
                    host = self.host_ip_q.get(block=False)
                except Exception:
                    continue
                count += 1
                print(host)
                req_data = [(host, {})]
                reqs = makeRequests(
                    self._run_ping,
                    req_data,
                    callback=self._handle_count,
                    exc_callback=self._handle_exception)
                for req in reqs:
                    print("Add request %s ", str(req))
                    pool.putRequest(req)
            try:
                time.sleep(0.2)
                print('ttttttttttt')
                pool.poll()
            except KeyboardInterrupt:
                break
            except NoResultsPending:
                print(222222222222222)
                logger.info("Waiting to collect data for new host ...")
                continue
            except Exception as e:
                print(e)
                logger.error("Create request failed %s ", e.args)
                continue
        print(33333)

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
        print(ip_vlan_map)
        #self._hand_ping_result(hostid, ALL_STR, ip_vlan_map)
        #return
        ip_list = list(ip_vlan_map.keys())
        ips = ' '.join(ip_list)
        fping_cmd = PING_MAPPER[self.schema].format(ips)
        print(fping_cmd)
        proc = subprocess.Popen(fping_cmd, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #all_str = proc.communicate()[1].decode()
        #proc.wait()
        proc.poll()
        #time.sleep(5)
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        all_str = stdout + stderr
        all_str = all_str.decode()
        #all_str = stdout
        print("11111")
        print(all_str)
        self._hand_ping_result(hostid, all_str, ip_vlan_map)

    def _hand_ping_result(self, hostid, fping_result, ip_vlan_map):
        fping_res = re.findall(
            r"(\d+\.\d+\.\d+\.\d+).*?xmt/rcv/%loss\s+=\s+(\d+)/(\d+)/(\d+)%.*?min/avg/max\s+=\s+([0-9\.]+)/([0-9\.]+)/([0-9\.]+)",
            fping_result, re.S)
        fping_res = [[hostid, ip_vlan_map[r[0]], r[0], r[1], r[2], r[3], r[4], r[5], r[6], self.time_str]
                     for r in fping_res]
        print(fping_res)
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
        self.logger.error("**** Exception occured in request #%s: %s" %
                          (request.requestID, exc_info))

    def __call__(self, *args, **kwargs):
        self.get_ips_scheduler()
        self.main_loop()

    def _get_host_macros(self, hostid):
        search = {
            'selectMacros': ["macro", "value"],
            'hostids': hostid
        }
        res = self.rtm_api.host.get(**search)
        print(res[0])
        return {data["macro"]: data["value"] for data in res[0]["macros"]}


if __name__ == '__main__':
    import json
    import ssl
    import sys
    try:
        import urllib2
    except ImportError:
        import urllib.request as urllib2
    try:
        import Queue  # Python 2
    except ImportError:
        import queue as Queue  # Python 3

    def ssl_context_compat(func):
        def inner(req):
            # We shoul explicitly disable cert verification to support
            # self-signed certs with urllib2 since Python 2.7.9 and 3.4.3

            default_version = (2, 7, 9)
            version = {
                2: default_version,
                3: (3, 4, 3),
            }

            python_version = sys.version_info[0]
            minimum_version = version.get(python_version, default_version)

            if sys.version_info[0:3] >= minimum_version:
                # Create default context to skip SSL cert verification.
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                res = func(req, context=ctx)
            else:
                res = func(req)

            return res

        return inner

    @ssl_context_compat
    def urlopen(*args, **kwargs):
        return urllib2.urlopen(*args, **kwargs)

    class RtmAPIException(Exception):
        """RtmAPI exception class.

        :code list:
        :32602: Invalid params (eg already exists)
        :32500: No permissions
        """
        pass

    class RtmAPIObjectClass(object):
        """RtmAPI Object class.

        :type group: str
        :param group: Rtm API method group name.
            Example: `apiinfo.version` method it will be `apiinfo`.

        :type parent: :class:`rtm.api.RtmAPI` object
        :param parent: RtmAPI object to use as parent.
        """

        def __init__(self, group, parent):
            self.group = group
            self.parent = parent

        def __getattr__(self, name):
            """Dynamically create a method.

            :type name: str
            :param name: Rtm API method name.
                Example: `apiinfo.version` method it will be `version`.
            """

            def fn(*args, **kwargs):
                if args and kwargs:
                    raise TypeError("Found both args and kwargs")

                method = '{0}.{1}'.format(self.group, name)

                return self.parent.do_request(
                    method,
                    args or kwargs
                )['result']

            return fn

    class RtmAPI(object):

        def __init__(self, url='https://localhost/rtm',
                     use_authenticate=False, user='admin', password='rtm'):
            self.use_authenticate = use_authenticate
            self.auth = None
            self.url = url + '/api_jsonrpc.php'
            self._login(user, password)

        def __getattr__(self, name):
            """Dynamically create an object class (ie: host).

            :type name: str
            :param name: Rtm API method group name.
                Example: `apiinfo.version` method it will be `apiinfo`.
            """

            return RtmAPIObjectClass(name, self)

        def _login(self, user='', password=''):
            """Do login to rtm server.

            :type user: str
            :param user: Rtm user

            :type password: str
            :param password: Rtm user password
            """

            self.auth = None

            if self.use_authenticate:
                self.auth = self.user.authenticate(
                    user=user, password=password)
            else:
                self.auth = self.user.login(user=user, password=password)

        def api_version(self):
            """Return version of server Rtm API.

            :rtype: str
            :return: Version of server Rtm API.
            """

            return self.apiinfo.version()

        def do_request(self, method, params=None):
            """Make request to Rtm API.

            :type method: str
            :param method: RtmAPI method, like: `apiinfo.version`.

            :type params: str
            :param params: RtmAPI method arguments.
            """

            if method.strip() == "configuration.imports":
                method = "configuration.import"
            request_json = {
                'jsonrpc': '2.0',
                'method': method,
                'params': params or {},
                'id': '1',
            }

            # apiinfo.version and user.login doesn't require auth token
            if self.auth and (method not in ('apiinfo.version', 'user.login')):
                request_json['auth'] = self.auth

            data = json.dumps(request_json)
            if not isinstance(data, bytes):
                data = data.encode("utf-8")

            req = urllib2.Request(self.url, data)
            req.get_method = lambda: 'POST'
            req.add_header('Content-Type', 'application/json-rpc')

            try:
                res = urlopen(req)
                res_str = res.read().decode('utf-8')
                res_json = json.loads(res_str)
            except ValueError as e:
                raise RtmAPIException("Unable to parse json: %s" % e.message)

            res_str = json.dumps(res_json, indent=4, separators=(',', ': '))
            if 'error' in res_json:
                err = res_json['error'].copy()
                err.update({'json': str(request_json)})
                msg_str = "Error {code}: {message}, {data} while sending {json}"
                msg = msg_str.format(**err)
                raise RtmAPIException(msg, err['code'])

            return res_json

        def get_id(self, item_type, item=None,
                   with_id=False, hostid=None, **args):
            """Return id or ids of rtm objects.

            :type item_type: str
            :param item_type: Type of rtm object. (eg host, item etc.)

            :type item: str
            :param item: Name of rtm object. If it is `None`, return list of
                all objects in the scope.

            :type with_id: bool
            :param with_id: Returned values will be in rtm json `id` format.
                Examlpe: `{'itemid: 128}`

            :type name: bool
            :param name: Return name instead of id.

            :type hostid: int
            :param hostid: Filter objects by specific hostid.

            :type templateids: int
            :param tempateids: Filter objects which only belong to specific
                templates by template id.

            :type app_name: str
            :param app_name: Filter object which only belong to specific
                application.

            :rtype: int or list
            :return: Return single `id`, `name` or list of values.
            """

            result = None
            name = args.get('name', False)

            type_ = '{item_type}.get'.format(item_type=item_type)

            item_filter_name = {
                'mediatype': 'description',
                'trigger': 'description',
                'triggerprototype': 'description',
                'user': 'alias',
                'usermacro': 'macro',
            }

            item_id_name = {
                'discoveryrule': 'item',
                'graphprototype': 'graph',
                'hostgroup': 'group',
                'itemprototype': 'item',
                'map': 'selement',
                'triggerprototype': 'trigger',
                'usergroup': 'usrgrp',
                'usermacro': 'hostmacro',
            }

            filter_ = {
                'filter': {
                    item_filter_name.get(item_type, 'name'): item,
                },
                'output': 'extend'}

            if hostid:
                filter_['filter'].update({'hostid': hostid})

            if args.get('templateids'):
                if item_type == 'usermacro':
                    filter_['hostids'] = args['templateids']
                else:
                    filter_['templateids'] = args['templateids']

            if args.get('app_name'):
                filter_['application'] = args['app_name']

            response = self.do_request(type_, filter_)['result']

            if response:
                item_id_str = item_id_name.get(item_type, item_type)
                item_id = '{item}id'.format(item=item_id_str)
                result = []
                for obj in response:
                    # Check if object not belong current template
                    if args.get('templateids'):
                        if (not obj.get('templateid') in ("0", None) or
                                not len(obj.get('templateids', [])) == 0):
                            continue

                    if name:
                        o = obj.get(item_filter_name.get(item_type, 'name'))
                        result.append(o)
                    elif with_id:
                        result.append({item_id: int(obj.get(item_id))})
                    else:
                        result.append(int(obj.get(item_id)))

                list_types = (list, type(None))
                if not isinstance(item, list_types):
                    result = result[0]

            return result

    api = RtmAPI('http://124.160.0.79:8090/service_robot',
                 user='Admin', password='RTMAdmin!')
    ALL_STR = """
    10.255.243.236       : xmt/rcv/%loss = 4/4/0%, min/avg/max = 0.03/0.04/0.05
    10.255.225.144    : xmt/rcv/%loss = 4/4/0%, min/avg/max = 35.8/35.9/36.1
    10.255.232.64 : xmt/rcv/%loss = 4/4/0%, min/avg/max = 0.96/1.03/1.07
    10.255.198.178 : xmt/rcv/%loss = 4/4/0%, min/avg/max = 0.96/1.03/1.08
    10.255.247.9 : xmt/rcv/%loss = 4/4/0%, min/avg/max = 0.96/1.03/1.09
    """
    #IP_VLAN_MAP = {'10.255.243.236': 'svc:100 sap:[lag-8:3737.486]', '10.255.225.144': 'svc:100 sap:[lag-2:3750.133]', '10.255.232.64': 'svc:100 sap:[lag-7:3952.963]', '10.255.198.178': 'svc:100 sap:[lag-18:3046.850]', '10.255.247.9': 'svc:100 sap:[lag-17:3972.1118]'}
    IP_VLAN_MAP = {'127.0.0.1': 'svc:100 sap:[lag-8:3737.486]', '39.156.69.79': 'svc:100 sap:[lag-2:3750.133]', '110.185.121.221': 'svc:100 sap:[lag-7:3952.963]', '118.121.193.140': 'svc:100 sap:[lag-18:3046.850]', '110.185.121.218': 'svc:100 sap:[lag-17:3972.1118]'}
    L = threading.local()
    L.Count = 0
    with PingProcess(1, 200, [10010]) as pro:
        pro()
        print("end")

