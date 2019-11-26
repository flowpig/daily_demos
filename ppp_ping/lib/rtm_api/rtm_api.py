#g -*- encoding: utf-8 -*-
#
# Copyright © 2014 Alexey Dubkov
#
# This file is part of py-rtm.
#
# Py-rtm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Py-rtm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with py-rtm. If not, see <http://www.gnu.org/licenses/>.

import json
import ssl
import sys
import socket
import threading

socket.setdefaulttimeout(15)

# For Python 2 and 3 compatibility
try:
    import urllib2
except ImportError:
    # Since Python 3, urllib2.Request and urlopen were moved to
    # the urllib.request.
    import urllib.request as urllib2

from lib.utils.logger import Logger
from utils.const import const
from utils.config import SRServiceConf

logger = Logger.get_logger();

'''
rtmapi.hostinterface.get(output=["dns","ip","useip"],selectHosts=["host"],filter={"main":1,"type":1}):
'''


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
            #logger.debug("Call %s method", method)

            return self.parent.do_request(
                method,
                args or kwargs
            )['result']

        return fn


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
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            res = func(req,context=ctx)

        return res

    return inner


@ssl_context_compat
def urlopen(*args, **kwargs):
    return urllib2.urlopen(*args, **kwargs)


class RtmAPI(object):
    """RtmAPI class, implement interface to rtm api.

    :type url: str
    :param url: URL to rtm api. Default: `https://localhost/rtm`

    :type use_authenticate: bool
    :param use_authenticate: Use `user.authenticate` method if `True` else
        `user.login`.

    :type user: str
    :param user: Rtm user name. Default: `admin`.

    :type password: str
    :param password: Rtm user password. Default `rtm`.

    >>> from pyrtm import RtmAPI
    >>> z = RtmAPI('https://rtm.server', user='admin', password='rtm')
    >>> # Get API Version
    >>> z.api_info.version()
    >>> u'2.2.1'
    >>> # or
    >>> z.do_request('apiinfo.version')
    >>> {u'jsonrpc': u'2.0', u'result': u'2.2.1', u'id': u'1'}
    >>> # Get all disabled hosts
    >>> z.host.get(status=1)
    >>> # or
    >>> z.do_request('host.getobjects', {'status': 1})
    """

    #def __init__(self, url='https://localhost/rtm',
    #             use_authenticate=False, user='admin', password='rtm'):
    #    self.use_authenticate = use_authenticate
    #    self.auth = None
    #    self.url = url + '/api_jsonrpc.php'
    #    self._login(user, password)
    #    logger.debug("JSON-PRC Server: %s", self.url)

    
    def __init__(self, **kwargs):
        self.use_authenticate = False
        self.auth = None
        if "auth" in kwargs.keys():
            self.auth = kwargs["auth"]
        self.url = kwargs["url"] + '/api_jsonrpc.php'
        if self.auth is None:
            self._login(kwargs["user"],kwargs["password"])
        #logger.debug("JSON-PRC Server: %s", self.url)

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

        logger.debug("RtmAPI.login({0},{1})".format(user, password))

        self.auth = None

        if self.use_authenticate:
            self.auth = self.user.authenticate(user=user, password=password)
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

        >>> from pyrtm import RtmAPI
        >>> z = RtmAPI()
        >>> apiinfo = z.do_request('apiinfo.version')
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
        str_par = json.dumps(request_json)
        if str_par.find("password") < 0:
            logger.debug(
                'urllib2.Request({0}, {1})'.format(
                    self.url,
                    json.dumps(request_json)))
        else:
            logger.debug("Try to login through the api")

        data = json.dumps(request_json)
        if not isinstance(data, bytes):
            data = data.encode("utf-8")
        count = 0
        while count < 2:
            count = count + 1
            try:
                #print data
                req = urllib2.Request(self.url, data)
                req.get_method = lambda: 'POST'
                req.add_header('Content-Type', 'application/json-rpc')
                #print count

                try:
                    res = urlopen(req)
                    res_str = res.read().decode('utf-8')
                    res_json = json.loads(res_str)
                    res_str = json.dumps(res_json, indent=4, separators=(',', ': '))
                    #logger.debug("Response Body: %s", res_str)

                    if 'error' in res_json:
                        err = res_json['error'].copy()
                        err.update({'json': str(request_json)})
                        msg_str = "Error {code}: {message}, {data} while sending {json}"
                        msg = msg_str.format(**err)
                        raise RtmAPIException(msg, err['code'])

                    return res_json
                except ValueError as e:
                    raise RtmAPIException("Unable to parse json: %s" % e.message)
            except urllib2.URLError as e:
                logger.info("connect url failed  : %d"%(count))
                if count >= 2:
                    raise RtmAPIException("Connection between server failed: %s" % e.message)



    def get_id(self, item_type, item=None, with_id=False, hostid=None, **args):
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

        logger.debug(
            'do_request( "{type}", {filter} )'.format(
                type=type_,
                filter=filter_))
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

class RTMAPI():
    __rtm_lock = threading.Lock()
    rtm_auth = None
    
    def __init__(self):
        self.rtm = None
        config = SRServiceConf.get_conf()
        self.url = config.get(const.CFSR,const.CFSer)
        self.user = config.get(const.CFSR,const.CFUser)
        self.password = config.get(const.CFSR,const.CFPass)
        if self.url is None or \
                self.user is None or\
                self.password is None:
            logger.error("Service Robot parameter is missing")
            return

        if RTMAPI.rtm_auth is not None:
            self.rtm = RtmAPI(auth=RTMAPI.rtm_auth,\
                    url=self.url)
        self._test_connection()
        
        if self.rtm is None:
            self._create_rtm()
    def _create_rtm(self):
        try:
            with self.__rtm_lock:
                if self.rtm is None:
                    self.rtm = RtmAPI(
                            url = self.url,
                            user=self.user,
                            password = self.password)
                    RTMAPI.rtm_auth = self.rtm.auth

        except:
            logger.exception("create RTM failed")

    def _test_connection(self):
        try:
            if RTMAPI.rtm_auth is None:
                return
            host_info = self.rtm.host.get(hostids = ["1000"],output = ["key_","name"])
        except RtmAPIException,e:
            self.rtm =  None
            with self.__rtm_lock:
                RTMAPI.rtm_auth = None
    @classmethod
    def get_api(self):
        rtm = self()
        return rtm.rtm



if __name__ == '__main__':

    z = RtmAPI('http://10.69.178.141/service_robot', user='Admin', password='zabbix')
    a = z.host.get(status = 0);
    for host in a :
        print(host["hostid"] +  "      " + host["name"]);
    a = z.item.get(hostids =["10107"],output = ["itemid","key_","name"]);
    for host in a :
        print(host);
