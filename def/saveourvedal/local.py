import typing,simplelogger

SCRIPTMASTER=None
WORLD=None
MAINCONTROLOBJ=[]
dotpath='def/saveourvedal/'

FORMALNAME = 'Loneliness,neurOsama,supernoVa,Existence and '
INTERNALNAME='Saveourvedal'
FN_STANDFOR='LNSE'
VERSION='d8'
LASTUPDATE='2024.4.04'
AUTHOR='archotechsporeeta'
VERSION_D='L.N.S.E(%s) %s (%s) by %s' % (INTERNALNAME,VERSION,LASTUPDATE,AUTHOR)
loclogger = simplelogger.Logger(INTERNALNAME+' ' + VERSION)
LOADPROCESSER = None

def get_master(m):
    global SCRIPTMASTER,WORLD
    SCRIPTMASTER=m
    WORLD=m.get_master()

def get_scriptmaster():
    global SCRIPTMASTER
    return SCRIPTMASTER
def set_loadprocesser(p):
    global LOADPROCESSER
    LOADPROCESSER = p
def get_loadprocesser():
    global LOADPROCESSER
    return LOADPROCESSER
def get_world():
    global WORLD
    return WORLD
def set_MCO(mco):
    global MAINCONTROLOBJ
    MAINCONTROLOBJ = mco

def add_MCO(mco):
    global MAINCONTROLOBJ
    MAINCONTROLOBJ.append(mco)
def get_MCO():
    global MAINCONTROLOBJ
    return MAINCONTROLOBJ
def MCO_eventupdate(evt):
    global MAINCONTROLOBJ
    for m in MAINCONTROLOBJ:
        m.eventupdate(evt)
def MCO_draw(bs):
    global MAINCONTROLOBJ
    for m in MAINCONTROLOBJ:
        m.draw(bs)
def MCO_target(_class):
    global MAINCONTROLOBJ
    for m in MAINCONTROLOBJ:
        if isinstance(m,_class):return m
def MCO_target_classname(_class):
    '''太作弊了'''
    global MAINCONTROLOBJ
    for m in MAINCONTROLOBJ:
        if m.__class__.__name__==_class:return m
def MCO_destory(_class):
    global MAINCONTROLOBJ
    for m in MAINCONTROLOBJ:
        if isinstance(m,_class):
            MAINCONTROLOBJ.remove(m)
            return m

try:
    import numpy
except ModuleNotFoundError:
    numpy = None

try:
    import psutil
except ModuleNotFoundError:
    psutil = None

try:
    import soundfile as sf
except ModuleNotFoundError:
    sf = None

try:
    import simpleaudio as SA
except ModuleNotFoundError:
    SA = None
