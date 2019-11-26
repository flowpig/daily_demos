
import os
import sys

import paramiko
import time
import shlex
from subprocess import Popen, PIPE

from utils import *

SCR_FOLDER = "/../device/external_script/";

class ScriptConnector(object):

    """
    Uses SSH to connect to device
    """

    def __init__(self, device_info):
        self.logger = Logger.get_logger();
        self.logger.debug(device_info);
        self.connect();

    def connect(self):
        """
        Connect to the device
        """
        return;


    def get_exitcode_stdout_stderr(self,cmd):
        """
        Execute the external command and get its exitcode, stdout and stderr.
        """
        args = shlex.split(cmd);
        self.logger.debug("Script args %s",str(args))

        proc = Popen(args, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        exit_code = proc.returncode
        #
        return exit_code, out, err


    def send_command(self,command):
        """
        Executes the command passed
        """
        result = [];
        parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        command = parentdir + SCR_FOLDER + command;
        try:
            exit_code, out, err = self.get_exitcode_stdout_stderr(command);
            if exit_code < 0:
                self.logger.error("cmd " + str(command) + " result: "+ str(err));
            else:
                self.logger.debug("cmd " + str(command) + " result: "+ str(out));
            return out;
        except Exception as e:
            self.logger.error("Excute script %s failed %s",command,e.args)
        return None;

    def close_session(self):
         return;


if __name__ == '__main__':
    device_info = {"address":"127.0.0.1",
                   "username":"root",
                   "password":"root",
                   "transport":"ssh"};
    connector = ScriptConnector(device_info);
    connector.connect();
    result = connector.send_command("..ddddd/usr/lib/zabbix/externalscripts/PersonalIF.py");
