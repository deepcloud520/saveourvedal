

dotpath='def/lilitanah/'
import sys,json,os
sys.path.append(sys.path[0]+'/def/lilitanah')

from worldcore import *
from newcoretiny import TextDisplay,puttext,ImmEvent,EnterEvent,loadscript
from resmanager import DefResourceDomain
from lilycore import makerooms,str2point,loadjson
from blueberrylocals import *
from yellowpeachscripts import curgue_0_0,paimon_0

import pygame as pg
pg.init()




def init():
    world=get_world()
    
    loadconfig=loadjson('res/load.json')
    for key,item in loadconfig[0].items():
        DefResourceDomain.add_resource(key,pg.transform.scale2x(pg.image.load(dotpath+'/res/'+item)).convert_alpha())
    for key,item in loadconfig[1].items():
        DefResourceDomain.add_resource(key,pg.transform.scale2x(pg.image.load(dotpath+'/res/'+item)).convert_alpha())
        DefResourceDomain.add_resource('e'+key,pg.transform.flip(pg.transform.scale2x(pg.image.load(dotpath+'/res/'+item)),True,False).convert_alpha())
    get_rooms().update(makerooms('/room.json'))
    player=EntityPlayer(point(100,10),point(10,0),point(16,64),'rainbow',{'e_0':(40,'e_1','living.player.rainbow.e_0'),
                                                                         'e_1':(80,'e_2','living.player.rainbow.e_1'),
                                                                         'e_2':(40,'e_0','living.player.rainbow.e_2'),
                                                                         'w_0':(40,'w_1','living.player.rainbow.w_0'),
                                                                         'w_1':(35,'w_2','living.player.rainbow.w_1'),
                                                                         'w_2':(35,'w_3','living.player.rainbow.w_2'),
                                                                         'w_3':(35,'w_4','living.player.rainbow.w_3'),
                                                                         'w_4':(35,'w_1','living.player.rainbow.w_4'),
                                                                         'ew_0':(35,'ew_1','eliving.player.rainbow.w_0'),
                                                                         'ew_1':(35,'ew_2','eliving.player.rainbow.w_1'),
                                                                         'ew_2':(35,'ew_3','eliving.player.rainbow.w_2'),
                                                                         'ew_3':(35,'ew_4','eliving.player.rainbow.w_3'),
                                                                         'ew_4':(35,'ew_1','eliving.player.rainbow.w_4'),
                                                                         })
    set_player(player)
    get_rooms()['0_4'].livings.append(player)
    get_rooms()['0_4'].build(world.engine)
def postinit():
    world=get_world()
    loadscript('0_1','curgue',curgue_0_0)(world.eventrunner)
    loadscript('0_0','paimon',paimon_0)(world.eventrunner)

        