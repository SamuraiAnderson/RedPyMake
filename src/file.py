from .BaseControl import BaseControl
from .path import *
import os
import sys

class UFile(object):
    '''
        @brief: 文件资源定位
    '''
    def __init__(self, dev:BaseControl, path:str) -> None:
        self._dev = dev
        self._path = path

    @property
    def path(self):
        return self._path

    @property
    def RemoteUser(self):
        return self._dev

    def get_abs_path(self):
        if self.is_absolute_path(self._path):
            return self._path
        return abspath(self._dev.pwd, self._path, self._dev.name) # TODO:

    def is_absolute_path(self, path:str):
        if self._dev.name == 'nt':
            if os.name == 'nt':
                return os.path.isabs(path)
            return isabs_windows(path)
        else: # linux, mac
            return path.startswith('/') or path.startswith('~')

    def get_timestamp(self):
        if self._dev.file_exist(self._path):
            return self._dev.get_file_timestamp(self._path)
        else:
            return None

    def is_file(self):
        pass

    def is_dir(self):
        pass

    def is_exist(self):
        return self._dev.file_exist(self._path)

    def __str__(self) -> str:
        return f"PATH({self._dev.host}, {self._dev.pwd}, {self.path})"

    def __repr__(self) -> str:
        return self.__str__()
