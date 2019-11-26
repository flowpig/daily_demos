import sys
import time
import re

 
from lib.utils.logger import Logger
from utils.const import const
logger = Logger.get_logger()

#5 mins
INTERVAL = 5 * 60

class RTMItem(object):
    def __init__(self,item_attri,interval=300):
        self.attri = item_attri
        self.handle_key_parameter()
        self.interval = interval
        self.delay_time = 0
        self.lastclock = 0
        self.refresh_flag = 1
        self.trend_data = None
        self.max_value = const.MaxTrendValue
        self.min_value = const.MinTrendValue
        self.total = 0.0
        self.count = 0
        self.avg = 0.0
        self._init_delay_time()
        #logger.debug("Dump item : %s ",self.attri)
        return


    def handle_key_parameter(self):
        '''
            Handle some dynamic found items such as :
            test2[eth0]
            IFTX.py[ "-t" , "T", "-i",  lo]
        '''
        split_key = re.search('(.*)\[(.*)\]',self.attri["key_"])
        if (split_key is not None):
            self.attri.update({"key_without_param":split_key.group(1)})
            self.attri.update({"key_param":split_key.group(2)})
            #logger.debug("Split key %s with parameter %s",self.attri["key_"],self.attri["key_param"])
        return


    def update_item(self,item_attri):
        delay = "delay"
        self.refresh_flag = 1

        if delay in item_attri.keys():
            if self.attri[delay] != item_attri[delay]:
                self.attri[delay] = item_attri[delay]
                self.delay_time = int(item_attri["delay"])
        if 'lastclock' in item_attri.keys():
            if self.attri["lastclock"] != item_attri["lastclock"]:
                self.attri["lastclock"] = item_attri["lastclock"]
                self.lastclock = int(item_attri["lastclock"])
        return
    def get_last_value(self):
        return self.attri.get('lastvalue',None)
    def get_key(self):
        return self.attri["key_"]

    def get_key_without_para(self):
        if "key_without_param" in self.attri.keys():
            return self.attri["key_without_param"]
        return self.attri["key_"]

    def get_key_para(self):
        if "key_param" in self.attri.keys():
            return self.attri["key_param"]
        return None

    def get_para_value(self):
        if "params" in self.attri.keys():
            return self.attri["params"]
        return None

    def _init_delay_time(self):
        delay = "delay"
        if delay in self.attri.keys():
            self.delay_time = int(self.attri["delay"])
        if 'lastclock' in self.attri.keys():
            self.lastclock = int(self.attri["lastclock"])

    '''
       The function was disabled 
    '''
    def need_collect(self):
        self.refresh_flag = 0
        if self.delay_time == 0 or self.lastclock == 0:
            return True
        timeout = self.lastclock + self.delay_time - self.interval/2 - time.time()
        if timeout < 0:
            return True
        else:
            return False

    def process_trend_data(self):
        if self.trend_data is None:
            return
        bandwidth = ["port_bandwidth_in_ratio","port_bandwidth_out_ratio"]
        if "key_without_param" in self.attri.keys() and self.attri["key_without_param"] in bandwidth:
            return self._process_bandwidth_data()
        self.total = 0
        self.count = 0
        for data in self.trend_data: 
            #get max value
            temp = float(data['value_max'])
            if temp > self.max_value:
                self.max_value = temp
            #get min value
            temp_min = float(data['value_min'])
            if temp_min < self.min_value:
                self.min_value = temp_min

            self.count += int(data['num'])
            self.total += int(data['num']) * float(data['value_avg'])
        if self.count == 0:
            return
        #get average value
        self.avg = int(self.total/self.count)

    def _process_bandwidth_data(self):
        self.max_value = 0
        self.total = 0
        self.count = 0
        self.min_value = 0
        all_data = []
        for data in self.trend_data: 
            temp = float(data['value_max'])
            all_data.append(temp)
            self.count += int(data['num'])
            self.total += int(data['num']) * float(data['value_avg'])
        if self.count == 0:
            return
        self.avg = int(self.total/self.count)
        num = len(all_data) * const.BitRate/100
        if num > 0:
            num = num -1
        all_data.sort()
        self.max_value = all_data[num]
        return

    def get_trends_current_hour_min(self):
        all_data = []
        current_hour = int(time.time())%86400/3600
        for data in self.trend_data:
            clock = int(data['clock'])
            hour = clock%86400/3600
            if hour == current_hour:
                all_data.append(float(data['value_min']))
        all_data.sort()
        return all_data[0]







if __name__ == '__main__':
   for i in range(1,100):
       a = RTMItem({"key_":"bb"})
       print(sys.path)

