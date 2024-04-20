import importlib
import json

CWD='./def'

class BaseScriptRunner:
    def __init__(self,file,master):
        pass
    
class PythonScriptRunner(BaseScriptRunner):
    def __init__(self,file,master):
        self.script=importlib.import_module('def.'+file.replace('.py','').replace('/','.'))
        self.master=master
        self.name=file
        self.script.get_master(self)
        self.script.init()
    def get_master(self):
        return self.master
    def get_scriptattr(self,name):return getattr(self.script,name)
    def reload_script(self):
        self.script.reload()

def create_scriptRunner(file,scrtype='null',master=None):
    def warp():
        if scrtype=='python':
            return PythonScriptRunner(file,master)
        elif scrtype=='json':
            return JSONScriptRunner(file,master)
        elif scrtype=='null':
            return BaseScriptRunner(file,master)
    return warp
