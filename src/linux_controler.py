from .BaseControl import *
import paramiko
from paramiko import SSHClient
import src.config as config

class Linux(BaseControl):
    def __init__(self, host, user) -> None:
        self._user = user
        self._host = host
        self._pwd = '~'

        self.remoter = SSHClient()
        self.remoter.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.remoter.connect(hostname=self._host, username=self.user)

    @property
    def args_prefix(self):
        return ['cd', self.pwd, "&&"]

    @property
    def user(self):
        return self._user

    @property
    def host(self):
        return self._host

    @property
    def pwd(self):
        return self._pwd

    @pwd.setter
    def pwd(self, path):
        code, *_ = self.shell(f"test -d {path}")
        if code == 0:
            self._pwd = path
        else:
            raise FileNotFoundError(f"path:{self.host},{path} not exist.")

    # @shell_check_decorate
    def shell(self, *args):
        args = self.args_prefix + list(args)
        remote_cmd = args_to_cmd(args)
        stdin, stdout, stderr = self.remoter.exec_command(remote_cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            raise Exception(f"error cmd:{remote_cmd}, stdout:{stdout.read().decode()}, status_code:{exit_status}")
        elif config.DEBUG:
            print(f"{self.host}:{remote_cmd}")

        return exit_status, stdout.read().decode(), stderr.read().decode()

    def push(self, local_path, remote_path):
        try:
            sftp = self.remoter.open_sftp()
            sftp.put(local_path, remote_path)
            return True
        except Exception as e:
            print(f"Failed to transfer file: {e}")
            return False
        finally:
            if config.DEBUG:
                print(f"{self.host}:push {local_path} {remote_path}")
            sftp.close()

    def pull(self, remote_path, local_path):
        try:
            sftp = self.remoter.open_sftp()
            sftp.get(remote_path, local_path)
            return True
        except Exception as e:
            print(f"Failed to transfer file: {e}")
            return False
        finally:
            if config.DEBUG:
                print(f"{self.host}:pull {remote_path} {local_path}")
            sftp.close()

    @property
    def name(self):
        return 'posix'


    def get_file_timestamp(self, path):
        code, stdout, _ = self.shell("stat", "-c", "%Y", path)
        return int(stdout)

    def file_exist(self, path):
        code, stdout, stderr = self.shell(f"test -e {path} && echo true || echo false")
        return stdout.strip() == "true" # TODO: 莫名奇妙回车符

