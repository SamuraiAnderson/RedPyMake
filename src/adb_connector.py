import logging
from typing import Union
from .BaseControl import *
import src.config as config

class AdbCnet(BaseControl):
    def __init__(self, host, user=None) -> None:
        self._host:str = host
        self._pwd = '~'
        self._user = 'oem'
        self._connect()

    @property
    def args_prefix(self):
        return ['cd', self.pwd, "&&"]

    @property
    def pwd(self):
        return self._pwd

    @pwd.setter
    def pwd(self, path):
        code, *_ = self.shell(f"[ -d '{path}']")
        if code == 0:
            self._pwd = path
        else:
            print(f"path:{path} not exist.")
            return False

    @property
    def user(self):
        return self._user

    @property
    def host(self):
        return self._host

    def _connect(self)->bool:
        args = ['adb', 'connect', self._host]
        cmd = args_to_cmd(args)
        code, out, err = subprocess_run(cmd)
        # if code != 0:
        #     logging.error(f"connect failed:{err} {cmd}")
        #     return False
        return True

    # @shell_check_decorate
    def shell(self, *args)->[bool, str]:
        args = self.args_prefix + list(args)
        remote_cmd = args_to_cmd(args)
        cmd = ["adb", "shell", remote_cmd]
        code, out, err = subprocess_run(cmd)
        if code != 0:
            raise Exception(f"error cmd:{remote_cmd}, stdout:{out}, status_code:{code}")
        elif config.DEBUG:
            print(f"{self.host}:{cmd}")
        return code, out.decode(), err.decode()


    def push(self, file_local, file_remote): 
        cmd = ['adb', 'push', file_local, file_remote]
        code, out, err = subprocess_run(cmd)
        if code != 0:
            print(f"run {cmd} failed:{err}")
            return False
        elif config.DEBUG:
            print(f"{self.host}:push {file_local} {file_remote}")
        return True

    def pull(self, file_remote, file_local):
        cmd = ['adb', 'pull', file_remote, file_local]
        code, out, err = subprocess_run(cmd)
        if code != 0:
            print(f"run {cmd} failed:{err} {out}")
            return False
        elif config.DEBUG:
            print(f"{self.host}:pull {file_remote} {file_local}")
        return True

    @property
    def name(self):
        return 'posix'

    def get_file_timestamp(self, path):
        code, stdout, _ = self.shell("stat", path)
        return int(stdout)

    def file_exist(self, path):
        code, stdout, stderr = self.shell(f"test -e {path} && echo true || echo false")
        stdout:str
        return stdout.strip() == "true"

        