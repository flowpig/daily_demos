import abc
import six
@six.add_metaclass(abc.ABCMeta)
class Task(object):
    @abc.abstractmethod
    def run(self):
        pass
