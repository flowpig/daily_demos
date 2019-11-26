from lib.connector.ssh_connector import SSHConnector
from lib.connector.telnet_connector import TelnetConnector
from lib.utils.logger import Logger
from lib.utils.utils_funs import parse_uri


logger = Logger.get_logger()



class Device(object):

    def __init__(self, login_info, *args, **kwargs):
        self.login_keys = ["transport","address","username","password","port"]
        self.logger = Logger.get_logger()
        self.login_info = []
        self._parse_login_info(login_info)
        self.connection = None
        self.connect_tried_count = 0
        self.connection_failed_reason = None

    def _parse_login_info(self):
        info = parse_uri(self.login_info)
        self.login_info.append(dict(zip(self.login_keys, info)))

    def run_cmd(self, cmd, para=None):
        """
            Create a new protocol if needed;
        """
        result = None
        if para is not None:
            cmd_line = cmd + ' ' + para
        else:
            cmd_line = cmd
        if self.connection is None and self.connect_tried_count <= 1:
            self.connect_tried_count = self.connect_tried_count + 1
            try:
                ret = self.create_connection()
            except Exception as e:
                self.logger.exception('Create connection failed %s ', e.args)
                ret = None

            if ret is None:
                if self.connection is not None:
                    self.connection.close_session()
                    self.connection = None
        if self.connection is None or self.connect_tried_count > 1:
            return
        try:
            result = self.connection.send_command(cmd_line)
        except Exception as e:
            self.connect_tried_count = self.connect_tried_count + 1
            self.logger.exception(e)

        return result

    def create_first_jump(self, protocol, info):
        device_class_ = globals()[protocol]
        try:
            self.connection = device_class_(info)
            self.logger.debug('Create a new protocol %s', protocol)
        except Exception as e:
            self.logger.error('Connect failed  with error %(error)s', {'error': e.args})
            self.connection_failed_reason = str(e.args)
            return

        return

    def create_jump(self, protocol, info):
        username = info.get('username')
        ip = info.get('address')
        password = info.get('password')
        ret = self.connection.create_tunnel(protocol, ip, username, password)
        if ret is None:
            return
        return ret

    def create_connection(self):
        first_protocol = 1
        if self.login_info is not None:
            for protocol in self.login_info:
                self.logger.debug('Protocol is  %s', protocol)
                if str(protocol['transport']).lower() == str('ssh').lower():
                    if first_protocol == 1:
                        connector = 'SSHConnector'
                    else:
                        connector = 'ssh'
                else:
                    if str(protocol['transport']).lower() == str('telnet').lower():
                        if first_protocol == 1:
                            connector = 'TelnetConnector'
                        else:
                            connector = 'telnet'
                    else:
                        self.logger.debug("Can't find protocol %s defination", protocol)
                        return
                self.logger.debug('1--- Protocol is  %s', protocol)
                if first_protocol == 1:
                    self.create_first_jump(connector, protocol)
                    first_protocol = 0
                else:
                    if self.connection is None:
                        return
                    if self.create_jump(connector, protocol) is None:
                        self.logger.error('Create tunnel failed %s', {str(protocol)})
                        return
            return 1
        return