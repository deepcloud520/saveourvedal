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

'''
class ACIMTScriptRunner(BaseScriptRunner):
    def __init__(self,file,master):
        self.script=[]
        f=open('./def/'+file)
        temp=f.readlines()
        f.close()
        self.script
        self.name=file
        self.master=master
        self.runnum=-1
        self.global_vars={}
        self.local_vars={}
        self.lasttick=0
    def script_init(self,temp):
        for line in temp:
            stack=[]
            for single in line:
            # str
                if single=='"':     
                    if ('ps','"') in stack:
                        start=stack.index(('ps','"'))
                        editing=stack[start+1:]
                        stack=stack[:start]        
                        stack.append(('string',''.join([i[1] for i in editing])))
                    else:
                        stack.append(('ps','"'))
                # list
                elif single=='[':
                    stack.append(('ps','['))
                elif single==']':
                    if ('ps','[') in stack:
                        start=stack.index(('ps','['))
                        if ('ps','"') in stack  and stack.index(('ps','"'))<start:continue
                        editing=stack[start+1:]
                        stack=stack[:start]
                        stack.append(('list',[i for i in editing]))
                    else:
                        stack.append(('ps',']'))
                # eval
                elif single=='(':
                    stack.append(('ps','('))
                elif single==')':
                    if ('ps','(') in stack:
                        start=stack.index(('ps','('))
                        if ('ps','"') in stack  and stack.index(('ps','"'))<start:continue
                        editing=stack[start+1:]
                        stack=stack[:start]
                        stack.append(('eval',[i for i in editing]))
                    else:
                        stack.append(('ps',')'))
                elif single=='d':
                    if ('ps','d') in stack:
                        start=stack.index(('ps','d'))
                        #print(('ps','"') in stack and stack.index(('ps','"'))<start)
                        if ('ps','"') in stack and stack.index(('ps','"'))<start:continue
                        editing=stack[start+1:]
                        stack=stack[:start]
                        stack.append(('int',int(''.join([i[1] for i in editing]))))
                    else:
                        stack.append(('ps','d'))
                # vars(inc func)
                elif single=='%':
                    if ('ps','%') in stack:
                        start=stack.index(('ps','%'))
                        #print(('ps','"') in stack and stack.index(('ps','"'))<start)
                        if ('ps','"') in stack and stack.index(('ps','"'))<start:continue
                        editing=stack[start+1:]
                        stack=stack[:start]
                        stack.append(('vars',''.join([i[1] for i in editing])))
                    else:
                        stack.append(('ps','%'))
                elif single=='-':
                    if ('ps','-') in stack:
                        start=stack.index(('ps','-'))
                        #print(('ps','"') in stack and stack.index(('ps','"'))<start)
                        if ('ps','"') in stack and stack.index(('ps','"'))<start:continue
                        editing=stack[start+1:]
                        stack=stack[:start]
                        stack.append(('basestruct',''.join([i[1] for i in editing])))
                    else:
                        stack.append(('ps','-'))
                else:
                    stack.append(('sa',single))
            self.script.append(stack)
    def get_finaleval(self,scripteval):
        buffer=''
        for sing in scripteval[1]:
            if sing[0]=='eval':
                buffer+=get_final_eval(sing)
            elif sing[0]=='vars':
                buffer+=self.findvar(sing[1])
            else:
                buffer+=sing[1]
                
        return '('+buffer+")"
    def findvar(self,var):
        if var in self.global_vars:return self.global_vars[var]
        if var in self.local_vars:return self.local_vars[var]
        return None
    def run_script(self):
        def func_print(singeval):
            if singeval[0]!='eval':
                self.raise_scripterror('if needs eval,not any other shit')
            print(eval(self.get_final_eval(singeval)))
        self.global_vars={'print',func_print}
    def get_master(self):
        return self.master
    def raise_scripterror(self,info):
        print('Error in',str(self.runnum),info)
        raise TypeError
    def update(self,tick):
        pass
'''