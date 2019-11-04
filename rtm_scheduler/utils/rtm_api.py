# -*- encoding: utf-8 -*-


import requests
from utils.logger import LoggerUtil


logger = LoggerUtil().get_logger()


class RtmAPI(object):

    def __init__(self, url, user=None, password=None):
        self.url = url
        self.user = user
        self.passwprd = password
        self.req = requests
        self._get_token()

    def _get_token(self):
        if self.user is None or self.passwprd is None:
            return
