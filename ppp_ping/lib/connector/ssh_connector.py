import re
import socket
import time


from .base_ssh import MAX_BUFFER
from .base_ssh import SSHConnection
from .base_ssh import NetMikoTimeoutException


class SSHConnector(SSHConnection):

    def __init__(self, device_info):
        if 'address' not in device_info.keys():
            device_info["address"] = "127.0.0.1"

        if 'username' not in device_info.keys():
            device_info["username"] = "root"

        if 'password' not in device_info.keys():
            device_info["password"] = "root"
        self.host = device_info.get('address')
        self.username = device_info.get('username')
        self.password = device_info.get('password')
        if "port" in device_info.keys():
            port = int(device_info["port"])
            super(SSHConnection, self).__init__(ip=self.host,
                                                username=self.username,
                                                password=self.password,
                                                port=port
                                                )
        else:
            super(SSHConnection, self).__init__(ip=self.host,username=self.username,password=self.password)

    def create_telent_tunnel(self, ip, user, passwd):
        expect_login = 'ogin:'
        expect_str = "Password:"
        login_cmd = "telnet  " + ip
        tem_str = self.send_command_expect(login_cmd, expect_login)
        tem_str = self.send_command_expect(user, expect_str)
        tem_str = self.send_command_expect(passwd, "#")
        prompt = self.set_base_prompt()
        

    def create_ssh_tunnel(self,ip,user,passwd):
        auth_info = 'Are you sure you want to continue connecting \(yes/no\)\?'
        expect_str = "assword:|Are you sure you want to continue connecting \(yes/no\)\?"
        expect_password='assword'
        if use is not None:
            login_cmd = 'ssh '+ user + "@" + ip
        else:
            login_cmd = 'ssh '+ ip
        if passwd is None:
            tem_str = self.send_command_expect(login_cmd,"#|\$")
        else:
            tem_str = self.send_command_expect(login_cmd,expect_str)

            if re.search(expect_str,tem_str):
                tem_str = self.send_command_expect("yes",expect_password)

            tem_str = self.send_command_expect(passwd,"#")
        prompt = self.set_base_prompt()

    def create_tunnel(self,protocol,ip,user,passwd):
        if protocol == "telnet":
            self.create_telent_tunnel(ip,user,passwd)
            return 1
        elif protocol == "ssh":
            self.create_ssh_tunnel(ip,user,passwd)
            return 1
        else:
            return None

    def set_base_prompt(self, pri_prompt_terminator='$',
                        alt_prompt_terminator='#', delay_factor=.1):
        """Determine base prompt."""
        return super(SSHConnection, self).set_base_prompt(
            pri_prompt_terminator=pri_prompt_terminator,
            alt_prompt_terminator=alt_prompt_terminator,
            delay_factor=delay_factor)

    def send_config_set(self, config_commands=None, exit_config_mode=True, **kwargs):
        """Can't exit from root (if root)"""
        if self.username == "root":
            exit_config_mode = False
        return super(SSHConnection, self).send_config_set(config_commands=config_commands,
                                                          exit_config_mode=exit_config_mode,
                                                          **kwargs)

    def check_config_mode(self, check_string='#'):
        """Verify root"""
        return self.check_enable_mode(check_string=check_string)

    def config_mode(self, config_command='sudo su'):
        """Attempt to become root."""
        return self.enable(cmd=config_command)

    def exit_config_mode(self, exit_config='exit'):
        return self.exit_enable_mode(exit_command=exit_config)

    def check_enable_mode(self, check_string='#'):
        """Verify root"""
        return super(SSHConnection, self).check_enable_mode(check_string=check_string)

    def exit_enable_mode(self, exit_command='exit'):
        """Exit enable mode."""
        output = ""
        if self.check_enable_mode():
            self.remote_conn.sendall(self.normalize_cmd(exit_command))
            time.sleep(.3)
            self.set_base_prompt()
            if self.check_enable_mode():
                raise ValueError("Failed to exit enable mode.")
        return output

    def enable(self, cmd='sudo su', pattern='ssword', re_flags=re.IGNORECASE):
        """Attempt to become root."""
        output = ""
        if not self.check_enable_mode():
            self.remote_conn.sendall(self.normalize_cmd(cmd))
            time.sleep(.3)
            pattern = re.escape(pattern)
            try:
                output += self.remote_conn.recv(MAX_BUFFER).decode('utf-8', 'ignore')
                if re.search(pattern, output, flags=re_flags):
                    self.remote_conn.sendall(self.normalize_cmd(self.secret))
                self.set_base_prompt()
            except socket.timeout:
                raise NetMikoTimeoutException("Timed-out reading channel, data not available.")
            if not self.check_enable_mode():
                raise ValueError("Failed to enter enable mode.")
        return output

    def close_session(self):
        try:
            self.disconnect()
        except Exception as e:
            pass

