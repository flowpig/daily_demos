import os


class SettingError(TypeError):
    pass


class _setting(object):

    def __setattr__(self, name, value):
        if name in self.__dict__.keys():
            raise SettingError("can't rebind setting (%s)" % name)
        self.__dict__[name] = value


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
setting = _setting()

setting.HourSec = 3600
setting.DaySec = 24 * setting.HourSec

# config project01 related items
setting.CFFile = os.path.join(BASE_DIR, "confs", "pro.cfg")
