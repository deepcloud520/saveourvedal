'''
    *wink*
    启动代码

'''

VERSION='d2'


import sys,json,os,argparse
dotpath='def/saveourvedal/'
sys.path.append(sys.path[0]+'/def/saveourvedal')
from worldcore import *
#from resmanager import DefResourceDomain,NameResourceDomain
import resmanager
from newcoretiny import RING0,RING1,RING2

import pygame as pg
import pygame.locals as PGKEY
from neurocore import *

import pickle,time,atexit
from evilcore import _load_process_,SENTENCE,LOAD_PROCESS,resentence,HISTORY,EntityTerminalDebug
from annycore import start_mulitprocess,ALL,check_modules
from local import *


'''
  人人都爱小AI
'''



def whenexit():
    print('exit')
def whenexit2():
    mcr = MCO_target(resmanager.DefResourceDomain.get_resource('MusicCoreRunableType'))
    mcr.play_action('stop')
    import traceback as tb

    # stdout被替换
    if isinstance(sys.stdout,EntityTerminalDebug):
        print()
        outfile=sys._stderr
        print('*'*10+'CONSOLE'+'*'*10,file=outfile)
        print(*map(lambda x:x[0],sys.stdout.history),file=outfile,sep='\n')

# 注册退出回调函数，防止trace被EntityTerminalDebug吞掉
atexit.register(whenexit2)

def init():
    global startmode,load_process,inlinedebug,args,start_time
    start_time = time.time()
    world=get_world()
    loclogger.info('start init...')
    resmanager.ConfigResourceDomain.load_resource(dotpath+'config.json')
    _default_=resmanager.ConfigResourceDomain.get_resource('startmode')
    
    parser = argparse.ArgumentParser(description='Saveourvedal基于命令行启动',epilog='本main.py不具有超级牛力')
    parser.add_argument('--startmode',action='store',default=_default_)
    parser.add_argument('--trigger',action='store')
    parser.add_argument('--inlinedebug',action='store',default=resmanager.ConfigResourceDomain.get_resource('inlinedebug'))
    parser.add_argument('--debuglevel',action='store',default=resmanager.ConfigResourceDomain.get_resource('debuglevel'))
    args = parser.parse_args()
    startmode = args.startmode
    inlinedebug = int(args.inlinedebug)
    loclogger.debug_level = int(args.debuglevel)
    if loclogger.debug_level >= 2:
        def logger(self,level,*message):
            loclogger._logger(self,level,*message)
            text='[%s/%s] %s ' % (level,loclogger.name,' '.join(map(lambda x:repr(x),message))[:100])
            if startmode=='text':
                load_process(text,(220,230,240,240))
            else:
                load_process(text,tick=int((time.time()-start_time)*1000))
        loclogger._logger=loclogger.logger
        loclogger.logger=logger
    load_process = LOAD_PROCESS[startmode]
    set_loadprocesser(load_process)
    print('\n',' '.join(['--%s %s'% (i,k) for i,k in vars(args).items()]))
    
    # 多语种支持
    name=resmanager.ConfigResourceDomain.get_resource('name')
    resmanager.NameResourceDomain.load_resource(dotpath + 'Name/' + name)

    # 加载主资源
    if startmode=='text':
        load_process(resmanager.NameResourceDomain.get_resource('info.loaddef'),(220,230,240,240))
    else:
        load_process(resmanager.NameResourceDomain.get_resource('info.loaddef'),tick=int((time.time()-start_time)*1000))
    resmanager.DefResourceDomain.load_resource(dotpath+'loadconfig.json')
    loclogger.info('init complete!')
def postinit():
    world=get_world()
    # 开始转换
    MPT=resmanager.ConfigResourceDomain.get_resource('musicplaytype')
    check_modules(MPT)
    resmanager.DefResourceDomain.resource['music.saveload']=TRANS[MPT](resmanager.DefResourceDomain.resource['music.saveload'])
    resmanager.DefResourceDomain.resource['music.entiy']=TRANS[MPT](resmanager.DefResourceDomain.resource['music.entiy'])
    #resmanager.DefResourceDomain.resource['music.bd'] = list(map(TRANS[MPT],resmanager.DefResourceDomain.resource['music.bd']))

    # mco
    DefResourceDomain.add_resource('MusicCoreRunableType',ALL[MPT])
    if startmode=='text':
        load_process(resmanager.NameResourceDomain.get_resource('info.loadmco'),(220,230,240,240))
    else:
        _load_process_(resmanager.NameResourceDomain.get_resource('info.loadmco'),tick=int((time.time()-start_time)*1000))
    mir=MainInterfaceRunable()
    get_MCO().append(mir)
    world.eventrunner.Runables[RING0].extend(get_MCO())
    
    if inlinedebug:
        dr=DebugRunable()
        get_world().eventrunner.Runables[RING2].append(dr)
        add_MCO(dr)

        debug=EntityTerminalDebug(point(10,0),point(5,22),point(700,600),title='debug',font=liberationmono,shape=point(65,26),defname='debug')
        mir.framemanager.add_control(debug)
        mir.framemanager.hide_control('debug')
    # 从参数触发
    
    if args.trigger:
        loclogger.info('triggers:',args.trigger)
        if startmode=='text':
            load_process(args.trigger,(220,230,240,240))
        get_world().eventrunner.trigger(args.trigger)
    loclogger.info('postinit complete!')

def gamedraw(bs):
    MCO_draw(bs)
def gameupdate(tick):
    pass
def eventupdate(se):
    MCO_eventupdate(se)
