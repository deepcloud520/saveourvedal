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
from local import *
import pygame as pg
import pygame.locals as PGKEY
from neurocore import *

import pickle,time,atexit
from evilcore import _load_process_,SENTENCE,LOAD_PROCESS,resentence,HISTORY,EntityTerminalDebug
from annycore import start_mulitprocess,ALL,check_modules



'''
  人人都爱小AI
'''

MAX_WORKERS=1

def whenexit():
    print('exit')
def whenexit2():
    if get_world().eventrunner.Runables[RING2]:
        mcr = get_world().eventrunner.Runables[RING2][0]
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

def postinit():
    world=get_world()
    
    start_time = time.time()

    
    resmanager.ConfigResourceDomain.load_resource(dotpath+'config.json')
    _default_=resmanager.ConfigResourceDomain.get_resource('startmode')
    
    parser = argparse.ArgumentParser(description='Saveourvedal基于命令行启动',epilog='本main.py不具有超级牛力')
    parser.add_argument('--startmode',action='store',default=_default_)
    parser.add_argument('--trigger',action='store')
    parser.add_argument('--inlinedebug',action='store',default=resmanager.ConfigResourceDomain.get_resource('inlinedebug'))
    args = parser.parse_args()
    

    startmode = args.startmode
    inlinedebug = int(args.inlinedebug)
    load_process = LOAD_PROCESS[startmode]
    

    
    # 多语种支持
    name=resmanager.ConfigResourceDomain.get_resource('name')
    resmanager.NameResourceDomain.load_resource(dotpath + 'Name/' + name)
    
    
    if startmode=='text':
        
        load_process(VERSION_D,(13,184,186,220))
        time.sleep(0.2)
        for st in resmanager.NameResourceDomain.get_resource('info.textload2'):
            load_process(st,(220,184,186,220))
            time.sleep(0.5)
        time.sleep(0.8)
        
        HISTORY.extend([None,None,None])
        for st in resmanager.NameResourceDomain.get_resource('info.textload3'):
            load_process(st,(120,184,86,220))
            time.sleep(0.2)
        time.sleep(0.5)
        load_process('boot settings:',(220,194,196,240))
        for name,value in resmanager.ConfigResourceDomain.resource.items():
            load_process(name+':'+str(value),(220,194,196,240))
            time.sleep(0.03)
        HISTORY.extend([None,None,None])
        
        HISTORY.extend([None,None,None])
        
        load_process(SENTENCE,(123,134,156,220))
        time.sleep(1.1)
    # 加载主资源
    if startmode=='text':
        load_process(resmanager.NameResourceDomain.get_resource('info.loaddef'),(220,230,240,240))
    else:
        load_process(resmanager.NameResourceDomain.get_resource('info.loaddef'),tick=int((time.time()-start_time)*1000))
    resmanager.DefResourceDomain.load_resource(dotpath+'loadconfig.json')
    #美丽的滚动效果
    if startmode=='text':
        HISTORY.extend([None,None,None])
        for name,value in resmanager.DefResourceDomain.resource.items():
            load_process(name+':'+str(value),(220,194,196,240))
            time.sleep(0.001)
        time.sleep(0.2)
    
    # 开始转换
    MPT=resmanager.ConfigResourceDomain.get_resource('musicplaytype')
    check_modules(MPT)
    resmanager.DefResourceDomain.resource['music.saveload']=TRANS[MPT](resmanager.DefResourceDomain.resource['music.saveload'])
    resmanager.DefResourceDomain.resource['music.entiy']=TRANS[MPT](resmanager.DefResourceDomain.resource['music.entiy'])
    resmanager.DefResourceDomain.resource['music.bd'] = list(map(TRANS[MPT],resmanager.DefResourceDomain.resource['music.bd']))
    if resmanager.ConfigResourceDomain.resource['musicplaytype'] in ('Simpleaudio',):
        if startmode=='text':
            load_process(resmanager.NameResourceDomain.get_resource('info.transogg'),(220,230,240,240))
        else:
            _load_process_(resmanager.NameResourceDomain.get_resource('info.transogg').replace('[max_workers]',str(MAX_WORKERS)),tick=int((time.time()-start_time)*1000))
        start_mulitprocess(max_workers=MAX_WORKERS)

    # mco
    DefResourceDomain.add_resource('MusicCoreRunableType',ALL[MPT])
    if startmode=='text':
        load_process(resmanager.NameResourceDomain.get_resource('info.loadmco'),(220,230,240,240))
    else:
        _load_process_(resmanager.NameResourceDomain.get_resource('info.loadmco'),tick=int((time.time()-start_time)*1000))
    mir=MainInterfaceRunable()
    set_MCO([mir])
    world.eventrunner.Runables[RING0].extend(get_MCO())
    
    if inlinedebug:
        dr=DebugRunable()
        get_world().eventrunner.Runables[RING2].append(dr)
        add_MCO(dr)

        debug=EntityTerminalDebug(point(10,0),point(5,22),point(700,600),title='debug',font=terminalfont1,shape=point(65,26),defname='debug')
        mir.framemanager.add_control(debug)
        mir.framemanager.hide_control('debug')
    # 从参数触发
    if args.trigger:
        if startmode=='text':
            load_process(args.trigger,(220,230,240,240))
        get_world().eventrunner.trigger(args.trigger)

def init():
    world=get_world()
def gamedraw(bs):
    MCO_draw(bs)
def gameupdate(tick):
    pass
def eventupdate(se):
    MCO_eventupdate(se)
