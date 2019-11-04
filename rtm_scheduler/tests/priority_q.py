import time

try:
    import Queue            # Python 2
except ImportError:
    import queue as Queue   # Python 3


class Host(object):
    def __init__(self, hostid, rtm_api, interval):
        self.hostid = hostid
        self.rtm_api = rtm_api
        self.interval = interval
        self.time = time.time()

    def __cmp__(self, other):
        if self.time < other.time:
            return -1
        elif self.time == other.time:
            return 0
        else:
            return 1

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0



pq = Queue.PriorityQueue(maxsize=0)

pq.put(Host(10111, "api01", 300))
pq.put(Host(10112, "api02", 300))
# pq.put(time.time(), Host(10111, "api01", 300))
# pq.put(time.time(), Host(10112, "api02", 300))
a = pq.get()
b = pq.get()
print(a.hostid)
print(b.hostid)
