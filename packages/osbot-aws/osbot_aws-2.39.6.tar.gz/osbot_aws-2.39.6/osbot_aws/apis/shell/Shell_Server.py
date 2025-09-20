from osbot_utils.utils.Process import Process

class Shell_Server:

    def invoke(self, data):
        method_name   = data.get('method_name')
        method_kwargs = data.get('method_kwargs')
        if method_name:
            if hasattr(Shell_Server,method_name):
                method = getattr(Shell_Server, method_name)
                if type(method_kwargs) is dict:
                    return_value = method(**method_kwargs)
                else:
                    return_value = method()
                return { "method_invoked" : True          ,
                         "method_name"    : method_name   ,
                         "method_kwargs"  : method_kwargs ,
                         "return_value"   : return_value  }
        return None


    @staticmethod  # note: this method by design allows extra commands injection via | and ;
    def bash(command, cwd=None):
        bash_command = 'bash'
        bash_params  = ['-c', command]
        return Shell_Server.process_run(bash_command, bash_params, cwd)


    @staticmethod
    def process_run(executable, params=None, cwd='.'):
        return Process.run(executable,params, cwd)

    @staticmethod
    def ping():
        return 'pong'

    @staticmethod
    def python_exec(code):
        try:
            exec(code)
            return locals().get('result')
        except Exception as error:
            return {'error': f'{error}'}

    # helper process_run methods
    @staticmethod
    def pwd():
        return Shell_Server.process_run('pwd').get('stdout')

    @staticmethod
    def disk_space():
        return Shell_Server.bash('df -h').get('stdout').strip()

    @staticmethod
    def file_contents(path):
        return Shell_Server.process_run('cat',[path]).get('stdout')

    @staticmethod
    def list_processes():
        return Shell_Server.bash('ps -aux').get('stdout').strip()

    @staticmethod
    def memory_usage():
        return Shell_Server.file_contents('/proc/meminfo')
        #as.asd()
        #return Shell_Server.bash('cat /proc/meminfo').get('stdout')
