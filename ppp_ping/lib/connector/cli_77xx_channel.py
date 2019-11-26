
from lib.utils.logger import Logger
from scp import SCPClient
from ssh_connector import  SSHConnector
from telnet_connector import TelnetConnector


class Cli77xxChannel(object):
    def __init__(self, login_info):

        self.Cmd_Set_Env = "environment no more"
        keys = ["protocol", "address", "username", "password", "port"]
        self.logger = Logger.get_logger()
        if len(login_info) != 5:
            return

        self.login_info = dict(zip(keys, login_info))
        self.protocol = self.login_info["protocol"]

        self.cli_connection_status = 0
        self.connection = None
        pass

    def _create_connection(self):
        protocol = self.login_info["protocol"]
        if protocol == "ssh":
            protocol = "SSHConnector"
        elif protocol == "telnet":
            protocol = "TelnetConnector"

        device_class_ = globals()[protocol]
        try:
            self.connection = device_class_(self.login_info)
            self.connection.send_command(self.Cmd_Set_Env)
            self.logger.debug("Create a new protocol %s", protocol)
        except Exception as e:
            self.logger.error("Connect failed  with error %(error)s",
                              {'error': e.args})
            self.cli_connection_status = 1
            return

    def run(self, cmd):
        result = None
        try:
            if self.connection is None:
                self._create_connection()
            result = self.connection.send_command(cmd)
            if result is None:
                return None
            result = result.replace('\x00', '\n').replace('\r07', '\n')
            result = result.replace('\r', '\n')
        except Exception as e:
            self.logger.exception(e)
        return result

    def get(self, r_file, l_file):
        try:
            if self.connection is None:
                self._create_connection()
            if self.protocol != "ssh" or self.connection is None:
                self.logger.error("Can't download file with scp protocol is %s "
                                  "or connection is None"%self.protocol)
                return
            scp = SCPClient(self.connection.remote_conn_pre.get_transport())
            scp.get(remote_path=r_file, local_path=l_file)
        except Exception as e:
            self.logger.exception("Down load file %s failed"%r_file)
        finally:
            return None

    def close(self):
        if self.connection is not None:
            self.connection.send_command("logout")
        self.connection.close_session()
