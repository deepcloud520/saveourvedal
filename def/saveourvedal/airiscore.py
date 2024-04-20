from worldcore import *
from evilcore import loadjson,add_dialog,print_dialog
from local import *
from newcoretiny import Runable,Trigger
import resmanager

ROOMS={}
NOWROOM=None


def get_rooms():
    global ROOMS
    return ROOMS
#{"type":"EntityDoor","data":{"defname":"dooreast","pos":"0x0","rect":"30x580","transportpos":"0x500"}}
def clear_rooms():
    global ROOMS
    ROOMS={}
def get_nowroom():
    global NOWROOM
    return NOWROOM

class MyTrigger(Trigger):
    '''运行函数'''
    def __init__(self,func,tarevent,breaknow=True):
        self.func=func
        self.tarevent=tarevent
        self.breaknow=breaknow
    def run(self,event,eventrunner):
        if event==self.tarevent:
            self.func(eventrunner)
            return (True,self.breaknow)



class MyTriggerPlus(MyTrigger):
    '''增加runable'''
    def __init__(self,func,tarevent,ring,breaknow=True):
        super().__init__(func,tarevent)
        self.ring=ring
        self.breaknow=breaknow
    def run(self,event,eventrunner):
        if event==self.tarevent:
            eventrunner.Runables[self.ring].append(self.func)
            return (True,self.breaknow)


class EntityWindow(Entity):
    def __init__(self,pos,deep=0,defname=None,brightness=8):
        super().__init__(pos,point(0,0),point(0,0),deep=0,defname=None)
        self.brightness=brightness
    def update(self,tick):
        pass
    def draw(self,scr,camarapos):
        pass
    def get_brightinfo(self):
        return get_centre(self),self.brightness



class Room:
    def __init__(self,roomname,rect,image=[],blocked=[],living=[]):
        self.roomname=roomname
        self.rect=rect
        self.blockeds=blocked
        self.livings=living
        self.images=image
    def build(self,worldengine):
        global NOWROOM
        worldengine.blockeds_line=self.blockeds.copy()
        worldengine.livings_line=self.livings.copy()
        worldengine.images_line=self.images.copy()
        # 修改现在的房间
        NOWROOM=self.roomname
    def resume(self,worldengine):
        self.blockeds=worldengine.blockeds_line.copy()
        self.libings=worldengine.livings_line.copy()
        self.images=worldengine.images_line.copy()



class EntityDoor(EntityBlocked):
    def __init__(self,pos,rect,defname=None,transportpos=None,info=''):
        super().__init__(pos,rect,defname=defname)
        self.onactive=False
        self.interfunc=self.oninteracted
        self.transportpos=transportpos
        self.isblocked=False
        self.extra_info=info
        self.update_info()
    def set_target(self,nowroomname,targetroomname,targetdoor):
        self.nowroomname=nowroomname
        self.targetroomname=targetroomname
        self.targetdoor=targetdoor
        self.transportpos=targetdoor.pos if not self.transportpos else self.transportpos
    def onhited(self,living,nhp,wayp,hittype):
        if self.onactive and isinstance(living,EntityPlayerBase):
            self.sync(False)
            self.transport(living)
    def transport(self,living):
        living.pos=self.transportpos.copy()
        nowroom=get_rooms()[self.nowroomname]
        newroom=get_rooms()[self.targetroomname]
        nowroom.livings.remove(living)
        newroom.livings.append(living)
        nowroom.resume(get_world().engine)
        newroom.build(get_world().engine)
        get_world().engine.camera_pos=get_world().get_centre(living.pos)+living.vel*100
        living.vel=point(0,0)
        #print('transport',str(living.pos),str(self.pos))
    def sync(self,onactive):
        #if not self.targetdoor:return
        self.onactive=onactive
        self.targetdoor.onactive=onactive
        self.update_info()
        self.targetdoor.update_info()
    def update_info(self):
        if self.onactive==False:
            self.info=self.extra_info+'(closed)'
        else:
            self.info=self.extra_info+'(opened)'
    def oninteracted(self,fromentity):
        if self.onactive==True:
            self.sync(False)
        else:
            self.sync(True)



class EntityDoorPaper(EntityDoor):
    def __init__(self,pos,rect,defname=None,transportpos=None):
        super().__init__(pos,rect,defname=defname,transportpos=transportpos)
        self.interfunc=self.oninteracted
        self.update_info()
    def update_info(self):
        self.info='Door'
    def oninteracted(self,fromentity):
        if isinstance(fromentity,EntityPlayerBase):self.transport(fromentity)
    def onhited(self,*args,**kwargs):
        pass




class EntityDoorImm(EntityDoor):
    def __init__(self,pos,rect,defname=None,transportpos=None):
        super().__init__(pos,rect,defname=defname,transportpos=transportpos)
        self.interfunc=None
        self.update_info()
    def update_info(self):
        self.info=''
    def onhited(self,living,nhp,wayp,hittype):
        if isinstance(living,EntityPlayerBase):
            self.sync(False)
            self.transport(living)




class EntityRealDoor(EntityDoor):
    '''~~EntityDoor可以直接指定transpos，不需要set_target，所以可以做单向门，但是这个不行~~ 修正：EntityDoor不行，因为sync会用到targetdoor'''
    def transport(self,living:EntityLiving):
        assert self.transportpos
        assert self.targetdoor
        toward = living.pos.x-self.pos.x
        v = living.pos.y-self.pos.y
        if toward > 0:
            # 从右边进
            living.pos = self.targetdoor.pos + point(-living.hitbox.rect.x,v)
        elif toward < 0:
            living.pos = self.targetdoor.pos + point(self.targetdoor.hitbox.rect.x,v)
        else:
            # NOT TODO
            pass
        #print(toward,living.pos)
        nowroom=get_rooms()[self.nowroomname]
        newroom=get_rooms()[self.targetroomname]
        
        nowroom.livings.remove(living)
        newroom.livings.append(living)
        
        nowroom.resume(get_world().engine)
        newroom.build(get_world().engine)
        
        get_world().engine.camera_pos = get_centre_u(living.pos, point(0, 0) - get_world().window)+point(0,-80)
        living.vel=point(0,0)
        #print('transport',str(living.pos),str(self.pos))
    def onhited(self,living:Entity,nhp,wayp,hittype):
        if self.onactive and isinstance(living,EntityPlayerBase) and hittype not in ('p1','p3'):
            # 说实话 我已经无法理解之前我写的那个物理引擎了
            self.sync(False)
            self.transport(living)

class EntityRealDoorLocked(EntityRealDoor):
    '''这个要时装的话还要重写sync'''
    def __init__(self,pos,rect,locked=False,defname=None,transportpos=None,info=''):
        self.locked=locked
        super().__init__(pos,rect,defname,transportpos,info)
    def unlock(self):
        self.locked=False
        self.update_info()
    def lock(self):
        self.locked=True
        self.update_info()
    def onhited(self,living,nhp,wayp,hittype):
        if not self.locked:
            super().onhited(living,nhp,wayp,hittype)
    def update_info(self):
        if self.locked:
            self.info = self.extra_info + '(locked)'
        else:
            if self.onactive==False:
                self.info=self.extra_info+'(closed)'
            else:
                self.info=self.extra_info+'(opened)'



class EntityBlocked_blank(Entity):
    def __init__(self,pos,rect,color,defname=None):
        super().__init__(pos,rect,defname=defname)
        self.fillcolor=tuple(color)
    def draw(self,scr,bias):
        pg.draw.rect(scr,self.fillcolor,(*(self.pos-bias)._intlist(),*self.hitbox.rect._intlist()),0)







#
# textures=[{0:(image,delay),1}]
# No r
#
        
class EntityNeuro(EntityPlayerBase):
    def __init__(self,pos,boxpos,boxrect,name,textures,domain='texture.',deep=0,defname=None,showdeep=0):
        super().__init__(pos,boxpos,boxrect,deep=deep,defname=defname,showdeep=showdeep)
        self.name = name
        self.textures = textures
        self.lasttick = 0
        self.stat = 1
        self.frame_counter = 0
        self.domain = domain
        self.frame = 0
        self.reset_jumpcount()
        self.canmove = 0
        assert self.textures[0]
    def reset_jumpcount(self):
        self.jumpcount = 1
        
    def get_draw_frame(self):
        return self.domain+self.textures[self.frame][0]+( 'r' if self.stat==-1 else '')
    def draw(self, scr, bias):
        super().draw(scr, bias)
        self.image = DefResourceDomain.get_resource(self.get_draw_frame())
        Entity.draw(self, scr, bias)
    def move(self,forward):
        self.vel.x+=forward * 0.32
        self.stat = forward
    def jump(self, force=10):
        if self.jumpcount > 0:
            self.vel.y -= force
            self.jumpcount -= 1
    def update(self,tick):
        # super().update(tick)
        self.pos += self.vel
        self.vel.x *= 0.9
        #if not hitflag else 0.945
        self.vel.y *= 0.99
        '''
        # 根据鼠标位置更换朝向
        mouse = tuple2point(pg.mouse.get_pos())
        if mouse.x >= get_world().window.x:
            self.stat = 1
        else:
            self.stat = -1
        '''
        if self.vel.y==0:
            self.frame_counter += abs(self.vel.x)
        if self.frame_counter >= self.textures[self.frame][1]:
            self.frame += 1
            self.frame_counter = 0
            if self.frame >= len(self.textures):
                self.frame = 0
    def onnothitflag(self):
        self.vel.y += 0.1
    def onhited(self, target, nhp, wayp, hittype):
        if target.isblocked:
            if hittype == 'nh':
                self.canmove = 2
            elif hittype == 'p4' or hittype == 'p2' and self.canmove != 2:
                if wayp.x < 0:
                    self.canmove = 1
                elif wayp.x > 0:
                    self.canmove = -1
            elif self.canmove != 2:
                self.canmove = 0
            if hittype in ('p1', 'p3') and wayp.y < 0:
                self.reset_jumpcount()



class EntityScreen(Entity):
    def __init__(self, pos,boxpos,boxrect,deep=0, defname=None, showdeep=0,info=''):
        super().__init__(pos, boxpos=boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep,info=info)
        self.image = pg.Surface(point2tuple(boxrect)).convert_alpha()


LASTEFFECT=None


def push_dialog(res):
    res=resmanager.NameResourceDomain.get_resource(res)
    talker=res[0]
    talkname = resmanager.NameResourceDomain.get_resource('name.talker.'+talker)
   
    dbf=MCO_target_classname('MainInterfaceRunable').framemanager.get_control('debate')
    window=get_world().window
    def warp(self,fromentity):
        global LASTEFFECT
        if LASTEFFECT and LASTEFFECT.alive:return
        #get_world().eventrunner.add_trigger(MyTrigger(PlayText(dbf,*res),'nexttext'))
        add_dialog(dbf,*res)
        
        LASTEFFECT=print_dialog(talkname,res[1])
    return warp



def push_trigger(trigger):
    def warp(*args):
        get_world().eventrunner.trigger(trigger)
    return warp



def makerooms(file,extra_map={}):
    # 这是我旧年涓的雨水，总舍不得拿来用
    roomjson=loadjson(file)
    entitymap = {
        'EntityImage':EntityImage,'EntityPlayer':EntityPlayer,'EntityDoor':EntityDoor,'EntityWindow':EntityWindow,
        'EntityDoorPaper':EntityDoorPaper,'EntityBlocked_blank':EntityBlocked_blank,'EntityBlocked':EntityBlocked,
        'EntityDoorImm':EntityDoorImm,"EntityNeuro":EntityNeuro,"EntityScreen":EntityScreen,"EntityRealDoor":EntityRealDoor,"EntityRealDoorLocked":EntityRealDoorLocked}
    entitymap.update(extra_map)
    doorclass= ('EntityDoor','EntityDoorPaper','EntityDoorImm','EntityRealDoor','EntityRealDoorLocked')
    interfuncmap={'push_dialog':push_dialog,'push_trigger':push_trigger}
    rooms={}
    doortree={}
    doorcache={}
    for roominfo in roomjson:
        roomname=roominfo['roomname']
        entitys={'images':[],'livings':[],'blockeds':[],}
        doortemp={}
        for entype in ('images','livings','blockeds'):
            for e in roominfo[entype]:
                # 数据预处理
                # 对默认的pos进行str2point
                for conv in ('pos','rect','boxpos','boxrect','transportpos'):
                    if conv in e['data']:
                        e['data'][conv]=str2point(e['data'][conv])
                #转换贴图，（EntityNeuro用到）
                if 'textures' in e['data']:
                    if len(e['data']['textures'][list(e['data']['textures'].keys())[0]])==2:
                        e['data']['textures'] = {int(i):j for i,j in e['data']['textures'].items()}
                # 转换info
                if 'info' in e['data']:
                    e['data']['info'] = resmanager.NameResourceDomain.get_resource(e['data']['info'])
                # 转换interfunc
                # inject_type:"f" 直接注入到oninteracted上
                kwargs={}
                if 'interfunc' in e['data']:
                    kwargs=e['data']['interfunc']
                    inject_type = '' if 'inject_type' not in e['data']['interfunc'] else e['data']['interfunc']['inject_type']
                    e['data'].pop('interfunc')
                #生成entity
                entity=entitymap[e['type']](**e['data'])
                if kwargs:
                    if 'f' in inject_type:
                        entity.oninteracted = interfuncmap[kwargs['type']](**kwargs['data'])
                    else:
                        entity.interfunc = interfuncmap[kwargs['type']](**kwargs['data'])
                entitys[entype].append(entity)
                #加入门
                if e['type'] in doorclass:
                    doortemp.update({entity.defname:entity})
        doorcache.update({roomname:doortemp})
        doortree.update({roomname:roominfo['doorinfo']})
        wallfill=roominfo['isfillwall']
        abspos=str2point(roominfo['roombox'][0])
        size=str2point(roominfo['roombox'][1])
        if wallfill:
            # use 10-width for default
            entitys['blockeds'].append(EntityBlocked(abspos-point(10,10),point(size.x+20,10)))
            entitys['blockeds'].append(EntityBlocked(abspos-point(10,-size.y),point(size.x+20,10)))
            entitys['blockeds'].append(EntityBlocked(abspos-point(10,0),point(10,size.y)))
            entitys['blockeds'].append(EntityBlocked(abspos+point(size.x,0),point(10,size.y)))
        rooms.update({roomname:Room(roomname,size,entitys['images'],entitys['blockeds'],entitys['livings'])})
    # 设置传送通道
    # 因为撒单向设置，所以可以设置单向门??
    for roomname,room in rooms.items():
        doorinfo=doortree[roomname]
        for defname,info in doorinfo.items():
            #print(roomname,defname,info[0],info[1])
            doorcache[roomname][defname].set_target(roomname,info[0],doorcache[info[0]][info[1]])
    return rooms
    

'''"interfunc":
                        {
                            "type":"push_trigger",
                            "inject_type":"f",
                            "data":
                            {
                                "trigger":"story0_quithome"
                            }
                        }'''