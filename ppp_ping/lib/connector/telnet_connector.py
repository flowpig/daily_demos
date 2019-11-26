# Copyright 2015 Brocade Communications System, Inc.
# All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

""" Implementation of Telnet Connector """
import telnetlib
import time
import re
import os
import sys
from utils import *

TELNET_PORT = 23
LOGIN_USER_TOKEN = "ogin:"
LOGIN_USER_TOKEN2 = "sername:"
LOGIN_PASS_TOKEN = "assword:"

END_OF_LINE = "\n"
PROMPT = "#"

MIN_TIMEOUT = 24
AVG_TIMEOUT = 24
MAX_TIMEOUT = 24

RESET_PROMPT = "export PS1='#'"
MORE_INPUT = 'Press any key to continue \(Q to quit\)'
N_MORE_INPUT = 'Press any key to continue (Q to quit)'

class TelnetTimeoutException():
    """Telnet session timed trying to connect to the device."""
    pass
class TelnetConnector(object):

    """
    Uses Telnet to connect to device
    """
    def __init__(self, device_info):
        self.host = device_info.get('address')
        self.username = device_info.get('username')
        self.password = device_info.get('password')
        self.transport = device_info.get('transport')
        self.prompt = device_info.get('prompt')
        self.logger =  Logger.get_logger();
        self.logger.debug(device_info);
        self.connector = None;
        self.need_clear_buffer = 0;
        self.disconnected = 0;
        self.jump_host_prompt = None;
        self.connect();

    def wait_for_recv_ready(self, delay_factor=.1, max_loops=100, send_newline=False):
        """Wait for data to be in the buffer so it can be received."""
        i = 0
        time.sleep(delay_factor)
        while i <= max_loops:
            if self.connector.sock_avail():
                return True
            else:
                time.sleep(delay_factor)
                i += 1
        raise TelnetTimeoutException("Timed out waiting for recv_ready");
    @staticmethod
    def normalize_linefeeds(a_string):
        """Convert '\r\r\n','\r\n', '\n\r' to '\n."""
        newline = re.compile(r'(\r\r\r\n|\r\r\n|\r\n|\n\r)')
        return newline.sub('\n', a_string)


    def find_prompt(self, delay_factor=.1):
        """Finds the current network device prompt, last line only."""
        prompt = ''

        self.connector.write("\n")
        # Initial attempt to get prompt
        count = 0
        while count <= 10 and not prompt:
            if self.wait_for_recv_ready():
                prompt = self.connector.read_very_eager().decode('utf-8', 'ignore');
                prompt = prompt.strip()
                self.logger.debug("prompt2a: {}".format(repr(prompt)))
                self.logger.debug("prompt2b: {}".format(prompt))
            else:
                self.connector.write("\n")
                time.sleep(delay_factor)
            count += 1

        self.logger.debug("prompt3: {}".format(prompt))
        # If multiple lines in the output take the last line
        prompt = self.normalize_linefeeds(prompt)
        prompt = prompt.split('\n')[-1]
        prompt = prompt.strip()
        prompt = prompt.replace('*','')
        prompt = prompt.replace('\\','\\\\')
        if not prompt:
            raise ValueError("Unable to find prompt: {}".format(prompt))
        time.sleep(delay_factor)
        self.logger.debug("prompt str is :" + prompt)
        return prompt

    def send_command_expect(self,cmd,expected):
        """
        Executes the command passed, if the response matches the prompt
        """
        tem_result=''
        self.connector.write( cmd + END_OF_LINE);
        n,match,previous_test = self.connector.expect(expected,timeout = AVG_TIMEOUT);
        if n == -1:
            raise IOError("Search pattern never detected in send_command_expect: {0}".format(expected));
        else:
            return previous_test;

    def create_telent_tunnel(self,ip,user,passwd):
        login_cmd = "telnet  " + ip;
        if user is None:
            tem_str = self.send_command_expect(login_cmd,[re.compile(b"#"),re.compile(b"\$")]);
        else:
            tem_str = self.send_command_expect(login_cmd,[LOGIN_USER_TOKEN]);
            if passwd is None:
                tem_str = self.send_command_expect(user,[re.compile(b"#"),re.compile(b"\$")]);
            else:
                tem_str = self.send_command_expect(user,[LOGIN_PASS_TOKEN]);
                tem_str = self.send_command_expect(passwd,[re.compile(b"#"),re.compile(b"\$")]);
        #self.connector.write(passwd + END_OF_LINE)
        self.prompt = self.find_prompt();
        

    def create_ssh_tunnel(self,ip,user,passwd):
        auth_info = 'you sure you want to continue connecting \(yes/no\)\?'
        if user is None:
            login_cmd = 'ssh ' + ip;
        else:
            login_cmd = 'ssh '+ user + "@" + ip;
        if passwd is None:
            tem_str = self.send_command_expect(login_cmd,[re.compile(b"#"),re.compile(b"\$")]);
        else:
            tem_str = self.send_command_expect(login_cmd,[re.compile(LOGIN_PASS_TOKEN),re.compile(auth_info)]);
            if re.search(auth_info,tem_str):
                tem_str = self.send_command_expect("yes",[re.compile(LOGIN_PASS_TOKEN),]);
            if passwd is not None:
                tem_str = self.send_command_expect(passwd,[re.compile(b"#"),re.compile(b"\$")]);
        self.prompt = self.find_prompt();

    def create_tunnel(self,protocol,ip,user,passwd):
        self.jump_host_prompt = self.prompt;
        if protocol == "telnet":
            self.create_telent_tunnel(ip,user,passwd);
        elif protocol == "ssh":
            self.create_ssh_tunnel(ip,user,passwd);
        #Need more adapt.Currently latest prompt is same with jump host prompt then login failed.
        if self.prompt is None or self.jump_host_prompt == self.prompt:
            self.logger.error("login in host " + str(ip) +  " failed");
            return None;
        else:
            return 1;
    def connect(self):
        """
        Connect to device via Telnet
        """
        if self.prompt is None:
            self.prompt = "#";
        if len(self.prompt.strip()) == 0:
           self.prompt = PROMPT;
        try:
            self.connector = telnetlib.Telnet(host=self.host, port=TELNET_PORT,timeout = AVG_TIMEOUT);

            n,match,output = self.connector.expect([re.compile(LOGIN_USER_TOKEN),re.compile(LOGIN_USER_TOKEN2)],timeout = AVG_TIMEOUT);
            if n == -1 :
                raise Exception(("Can't get the user token %s"),{str(output)})
            self.connector.read_until(LOGIN_USER_TOKEN, AVG_TIMEOUT)
            self.connector.write(self.username + END_OF_LINE)
            self.connector.read_until(LOGIN_PASS_TOKEN, AVG_TIMEOUT)
            #self.connector.write(self.password + END_OF_LINE)
            tem_str = self.send_command_expect(self.password,[re.compile(b"#"),re.compile(b"\$")]);
            self.prompt = self.find_prompt();
            self.logger.debug("first prompt is : " + self.prompt)
        except Exception as e:
            self.logger.error(("Connect failed to switch %(host)s with error"
                              " %(error)s"),
                          {'host': self.host, 'error': e.args})
            raise Exception(("Connection Failed"))

    def clear_buffer(self):
        tmp = self.connector.read_very_eager()
        return tmp;
            

    def send_command(self,command):
        """
        Executes the command passed, if the response matches the prompt
        """
        if self.disconnected == 1:
            return None;
        tem_result=''
        self.clear_buffer();
        self.connector.write( str(command.decode('utf-8','ignore')) + END_OF_LINE);
        need_try_again = 1;
        self.logger.debug("cmd:"+command);
        while need_try_again > 0:
            n,match,previous_test = self.connector.expect([self.prompt,MORE_INPUT],timeout = AVG_TIMEOUT);
            if previous_test is not None:
                tem_result = tem_result + previous_test;
                self.logger.debug("previous data:"+previous_test)
                self.logger.debug("temp data:"+tem_result)
                
            if n == 1:
                tem_result = tem_result.replace(N_MORE_INPUT,'');
                self.connector.write(" ");
            elif n == -1:
                if previous_test is not None and len(previous_test) > 0:
                    continue;
                need_try_again = need_try_again -1;
                if need_try_again == 0:
                    #Tried too many times and set the connection with failed.
                    self.disconnected = 1;
                    return None;
            else:
                self.logger.debug("result:"+tem_result)
                break;

        tem_result = tem_result.replace('\r','');
        tem_result = tem_result.encode('utf-8', 'ignore');
        return tem_result;

    def close_session(self):
        """Close TELNET session."""
        if self.connector:
            self.connector.write('logout\n')
            self.connector = None


if __name__ == '__main__':
    device_info = {"address":"10.69.183.131",
                   "username":"root",
                   "password":"password",
                   "transport":"telnet",
                   "prompt":"#"};
    connector = TelnetConnector(device_info);
    i = 0;
    while(i < 1) :
        i = i+1;
        connector.create_tunnel("ssh","10.56.227.18","nokia","nokia")

        result = connector.send_command("show card detail");
        print(result)
    connector.close_session();
