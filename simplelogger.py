# 对付着用用吧
# I cannot understand logging so
import time

QUIET=0
NORMAL=1
DEVELOP=2
DEBUG=3
DEBUG_LEVEL=3

def set_debug_level(d):
    global DEBUG_LEVEL
    DEBUG_LEVEL=d

'''
0:no any info,warn,err,debug (quiet)
1:info (normal)
2:info,warn,err (develop)
3:info,warn,err,debug (debug)
'''



class Logger:
    def __init__(self,name,debug_level=DEBUG_LEVEL):
        self.name=name
        self.history=[]
        self.debug_level=debug_level
    def info(self,*message):
        if self.debug_level>QUIET:
            self.logger('INFO',*message)
    def warn(self,*message):
        if self.debug_level>=DEVELOP:
            self.logger('WARN',*message)
    def error(self,*message):
        if self.debug_level>=DEVELOP:
            self.logger('ERROR',*message)
    def debug(self,*message):
        if self.debug_level>=DEBUG:
            self.logger('DEBUG',*message)
    def logger(self,level,*message):
        logtext='[%s/%s] %s %s'%(level,self.name,time.strftime('%Y-%m-%d %H:%M:%S'),' '.join(map(lambda x:str(x),message)))
        print('\n'+logtext,end='')
        self.history.append((level,self.name,time.time())+tuple(message))
class Logger_global:
    def __init__(self,name):
        self.name=name
        self.history=[]
    def info(self,*message):
        if DEBUG_LEVEL>QUIET:
            self.logger('INFO',*message)
    def warn(self,*message):
        if DEBUG_LEVEL>=DEVELOP:
            self.logger('WARN',*message)
    def error(self,*message):
        if DEBUG_LEVEL>=DEVELOP:
            self.logger('ERROR',*message)
    def debug(self,*message):
        if DEBUG_LEVEL>=DEBUG:
            self.logger('DEBUG',*message)
    def logger(self,level,*message):
        logtext='[%s/%s] %s %s'%(level,self.name,time.strftime('%Y-%m-%d %H:%M:%S'),' '.join(map(lambda x:str(x),message)))
        print('\n'+logtext,end='')
        self.history.append((level,self.name,time.time())+tuple(message))

mainlogger=Logger_global('main')