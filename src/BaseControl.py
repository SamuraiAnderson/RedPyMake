class BaseControl(object):
    '''
        android rv1106 时间会快一点
    '''
    def push(self, local_path, remote_path):
        raise NotImplementedError()

    def pull(self, remote_path, local_path):
        raise NotImplementedError()

    def shell(self, *args, **kwargs)->[int, str, str]:
        raise NotImplementedError()

    def pwd(self):
        raise NotImplementedError()

    def name(self):
        raise NotImplementedError()

    def home(self):
        code, stdout, stderr = self.shell("echo $HOME")
        return stdout

    def get_file_timestamp(self, file):
        raise NotImplementedError()

    def file_exist(self, path):
        raise NotImplementedError()


def args_to_cmd(args_li):
    cmd = ' '.join(args_li)
    return cmd 

def subprocess_run(cmd):
    import subprocess
    process = subprocess.Popen(cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                shell=True
            )
    stdout, stderr = process.communicate()
    return (process.returncode, 
            stdout,
            stderr
        )

def shell_check_decorate(func):
    def decorated_error(*args, **kwargs):
        code, stdout, stderr = func(*args, **kwargs)
        if code != 0:
            message = f"Run Error, so Stop.err:{stdout} {args}"
            raise Exception(message)
        return code, stdout, stderr
    return decorated_error
