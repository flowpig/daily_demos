# -*- coding: utf-8 -*-

import os
import platform
import datetime
import time
import signal
from subprocess import PIPE, Popen


MYSQL_BIN = "/usr/bin/mysql"
MYSQL_USER = "zabbix"
MYSQL_PWD = "zabbix"
MYSQL_DB = "zabbix"
MYSQL_PORT = "3306"
MYSQL_HOST = "127.0.0.1"

# 历史数据保留时间，单位天
HISTORY_DAYS = 30

# 趋势数据保留时间，单位月
TREND_MONTHS = 12


class Mysql(object):
    HISTORY_TABLE = "history, history_log, history_str, history_text, history_uint"
    TREND_TABLE = "trends, trends_uint"
    PARTITION_SELECT = """SELECT PARTITION_NAME FROM INFORMATION_SCHEMA.PARTITIONS WHERE TABLE_NAME = '{table}';"""
    CREATE_PARTITION = """ALTER TABLE {table} PARTITION BY RANGE( clock ) (PARTITION p{partition_date}  VALUES LESS THAN ({time_s}));"""
    ADD_PARTITION = """ALTER TABLE {table}  ADD PARTITION (PARTITION p{partition_date} VALUES LESS THAN ({time_s}));"""
    DEL_PARTITION = """ALTER TABLE {table} DROP PARTITION {partition};"""

    def __init__(self, host=MYSQL_HOST, username=MYSQL_USER,
                 password=MYSQL_PWD, port=MYSQL_PORT, db=MYSQL_DB):
        self._host = host
        self._username = username
        self._password = password
        self._port = port
        self._db = db
        self._mysql_prefix_cmd = self._init_pre_cmd()

    def _init_pre_cmd(self):
        base_cmd = "{mysql_bin} -u{user} -p{pwd} -h{host} -P{port} {db} -e"
        return base_cmd.format(mysql_bin=MYSQL_BIN, user=self._username,
                               pwd=self._password, host=self._host, port=self._port, db=self._db)

    def run_cmd(self, cmdstr):
        sql_cmd = '{0} "{1}"'.format(self._mysql_prefix_cmd, cmdstr)
        cmd_ut = Cmds(sql_cmd, timeout=2)
        stdo = cmd_ut.stdo()
        stde = cmd_ut.stde()
        retcode = cmd_ut.code()

        if retcode != 0:
            raise Exception('run cmd error: {}'.format(stde))
        else:
            return stdo

    def _hand_partition_res(self, p_res, drop_pre_stand):
        """
        :param p_res: select table partition return info
        :param drop_pre_stand: drop data according to the date num
        :return: will drop partition name list
        """
        pars_li = filter(lambda x: x[1:].isdigit(), p_res.split())
        res = filter(lambda x: int(x[1:]) <= drop_pre_stand, pars_li)
        return list(res)

    def create_partitions_history(self):
        for table in self.HISTORY_TABLE.split(","):
            table = table.strip()
            print(table)
            query_parti = self.PARTITION_SELECT.format(table=table)
            p_res = self.run_cmd(query_parti)
            p_li = list(filter(lambda x: x[1:].isdigit(), p_res.split()))
            if not p_li:
                td = str(datetime.datetime.today().date())
                td = ''.join(td.split("-"))
                timest = int(
                    time.mktime(
                        time.strptime(
                            "{} 23:59:59".format(td),
                            "%Y%m%d %H:%M:%S")))
                try:
                    sql_cmd = self.CREATE_PARTITION.format(
                        table=table, partition_date=td, time_s=timest)
                    # print(sql_cmd)
                    self.run_cmd(sql_cmd)
                    print(
                        "table {0} create partition {1} succeed".format(
                            table, "p" + td))
                except Exception as e:
                    print(
                        "table {0} create partition {1} failed".format(
                            table, "p" + td))
                    print(e)
                    continue
            after_days = list(map(lambda x: ''.join(
                x.split("-")), Util.get_after_days(7)))
            for d in after_days:
                if "p{}".format(d) not in p_li:
                    time_s = int(
                        time.mktime(
                            time.strptime(
                                "{} 23:59:59".format(d),
                                "%Y%m%d %H:%M:%S")))
                    try:
                        self.run_cmd(
                            self.ADD_PARTITION.format(
                                table=table,
                                partition_date=d,
                                time_s=time_s))
                        print(
                            "table {0} create partition {1} succeed".format(
                                table, "p" + d))
                    except Exception as e:
                        print(
                            "table {0} create partition {1} failed".format(
                                table, "p" + d))
                        print(e)
                        continue

    def create_partitions_trend(self):
        for table in self.TREND_TABLE.split(","):
            table = table.strip()
            print(table)
            query_parti = self.PARTITION_SELECT.format(table=table)
            p_res = self.run_cmd(query_parti)
            p_li = list(filter(lambda x: x[1:].isdigit(), p_res.split()))
            if not p_li:
                tm = time.strftime("%Y%m", time.localtime())
                tm_time = tm + "01 00:00:00"
                timest = int(
                    time.mktime(
                        time.strptime(
                            tm_time,
                            "%Y%m%d %H:%M:%S")))
                try:
                    sql_cmd = self.CREATE_PARTITION.format(
                        table=table, partition_date=tm, time_s=timest)
                    self.run_cmd(sql_cmd)
                    print(
                        "table {0} create partition {1} succeed".format(
                            table, "p" + tm))
                except Exception as e:
                    print(
                        "table {0} create partition {1} failed".format(
                            table, "p" + tm))
                    print(e)
                    continue
            after_months = Util.get_after_months(5)
            for d in after_months:
                if "p{}".format(d) not in p_li:
                    time_s = int(
                        time.mktime(
                            time.strptime(
                                d + "01 00:00:00",
                                "%Y%m%d %H:%M:%S")))
                    try:
                        self.run_cmd(
                            self.ADD_PARTITION.format(
                                table=table,
                                partition_date=d,
                                time_s=time_s))
                        print(
                            "table {0} create partition {1} succeed".format(
                                table, "p" + d))
                    except Exception as e:
                        print(
                            "table {0} create partition {1} failed".format(
                                table, "p" + d))
                        print(e)
                        continue

    def drop_partitions_history(self):
        for table in self.HISTORY_TABLE.split(","):
            table = table.strip()
            query_parti = self.PARTITION_SELECT.format(table=table)
            p_res = self.run_cmd(query_parti)
            pre_day = ''.join(Util.get_pre_day(HISTORY_DAYS).split("-"))
            will_del_pars = self._hand_partition_res(p_res, pre_day)
            for par in will_del_pars:
                self.run_cmd(
                    self.DEL_PARTITION.format(
                        table=table, partition=par))

    def drop_partitions_trend(self):
        for table in self.TREND_TABLE.split(","):
            table = table.strip()
            query_parti = self.PARTITION_SELECT.format(table=table)
            p_res = self.run_cmd(query_parti)
            pre_month = Util.get_pre_month(TREND_MONTHS)
            will_del_pars = self._hand_partition_res(p_res, pre_month)
            for par in will_del_pars:
                self.run_cmd(
                    self.DEL_PARTITION.format(
                        table=table, partition=par))


class Cmds(object):
    def __init__(self, *args, **kwargs):
        self.ps = None
        self.stdout = None
        self.stderr = None
        self.retcode = 0
        self.cmds(*args, **kwargs)

    def cmds(self, command, env=None, stdout=PIPE, stderr=PIPE, timeout=None):

        if platform.system() == "Linux":
            self.ps = Popen(
                command,
                stdout=stdout,
                stdin=PIPE,
                stderr=stderr,
                shell=True)
        else:
            self.ps = Popen(
                command,
                stdout=stdout,
                stdin=PIPE,
                stderr=stdout,
                shell=False)

        if timeout:
            start = datetime.datetime.now()
            while self.ps.poll() is None:
                time.sleep(0.2)
                now = datetime.datetime.now()
                if (now - start).seconds > timeout:
                    os.kill(self.ps.pid, signal.SIGINT)
                    self.retcode = -1
                    self.stdout = None
                    self.stderr = None
                    return self

        kwargs = {'input': self.stdout}
        (self.stdout, self.stderr) = self.ps.communicate(**kwargs)
        self.retcode = self.ps.returncode
        return self

    def __repr__(self):
        return self.stdo()

    def __unicode__(self):
        return self.stdo()

    def __str__(self):
        try:
            import simplejson as json
        except BaseException:
            import json
        res = {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "retcode": self.retcode}
        return json.dumps(res, separators=(',', ':'),
                          ensure_ascii=False).encode('utf-8')

    def stdo(self):
        if self.stdout:
            return self.stdout.strip().decode('utf-8')
        return ''

    def stde(self):
        if self.stderr:
            return self.stderr.strip().decode('utf-8')
        return ''

    def code(self):
        return self.retcode


class Util(object):

    @staticmethod
    def get_pre_days(days):
        end = datetime.datetime.today().date()
        day_all = [str(end)]
        while days:
            end -= datetime.timedelta(days=1)
            day_all.append(str(end))
            days -= 1
        return day_all[::-1]

    @staticmethod
    def get_pre_day(days):
        return str(datetime.datetime.today().date() -
                   datetime.timedelta(days=days))

    @staticmethod
    def get_after_days(days):
        start = datetime.datetime.today().date()
        day_all = [str(start)]
        while days:
            start += datetime.timedelta(days=1)
            day_all.append(str(start))
            days -= 1
        return day_all

    @staticmethod
    def get_pre_months(months):
        end = int(time.strftime("%Y%m", time.localtime()))
        month_all = [str(end)]
        while months:
            if str(end).endswith("01"):
                end -= 89
            else:
                end -= 1
            month_all.append(str(end))
            months -= 1
        return month_all[::-1]

    @staticmethod
    def get_pre_month(months):
        end = int(time.strftime("%Y%m", time.localtime()))
        while months:
            if str(end).endswith("01"):
                end -= 89
            else:
                end -= 1
            months -= 1
        return str(end)

    @staticmethod
    def get_after_months(months):
        start = int(time.strftime("%Y%m", time.localtime()))
        month_all = [str(start)]
        while months:
            if str(start).endswith("12"):
                start += 89
            else:
                start += 1
            month_all.append(str(start))
            months -= 1
        return month_all


def main():
    mysql = Mysql(
        host=MYSQL_HOST,
        username=MYSQL_USER,
        password=MYSQL_PWD,
        port=MYSQL_PORT,
        db=MYSQL_DB)
    mysql.create_partitions_history()
    mysql.create_partitions_trend()
    mysql.drop_partitions_history()
    mysql.drop_partitions_trend()


if __name__ == '__main__':
    main()

