from .BaseControl import *
import os

class LocalHost(BaseControl):
    @property
    def pwd(self):
        return self._pwd

    @pwd.setter
    def pwd(self, path):
        code = os.path.exists(path) and os.path.isdir(path)
        if code:
            self._pwd = path
            os.chdir(self.pwd)
        else:
            print(f"path:{path} not exist. or not is dir")
            return False

    @property
    def name(self):
        return os.name

    @property
    def host(self):
        return "localhost"

    def get_file_timestamp(self, path):
        return int(os.stat(path).st_mtime)

    def file_exist(self, path):
        return os.path.exists(path)