from newcoretiny import *
from local import *
import resmanager,itertools
from evilcore import *
from tool import *



def add_effects(effects):
    def warp(eventrunner):
        get_world().effects.extend(effects)
    return warp
def add_runables(runables,ring):
    def warp(eventrunner):
        get_world().eventrunner.Runables[ring].extend(runables)
    return warp
def add_trigger(trigger,*args,**kwargs):
    def warp(func):
        get_world().eventrunner.put_event(trigger(func,*args,**kwargs))
        return func
    return warp
def trigger(content):
    def warp(master):
        master.trigger(content)
    return warp



# (tick,command,text)
class TerminalCore(Runable):
    def __init__(self,terminal,content,destory=None):
        super().__init__()
        self.terminal=terminal
        self.content=content.copy()
        self.content.reverse()
        self.destory=destory
    def update(self,tick,master):
        if len(self.content)==0:
            if self.destory:
                MCO_target_classname(_class='MainInterfaceRunable').framemanager.remove_control(self.destory)
            return True
        if self.lasttick+self.content[-1]['delay']<=tick:
            content = self.content.pop()
            self.lasttick=tick
            if content['command']=='w':
                self.terminal.write(content['text'],color=tuple(content['color']))
            elif content['command']=='c':
                for i in range(int(content['num'])):
                    self.terminal.pop(-1)
            elif content['command']=='f':
                self.terminal.flush()
            elif content['command']=='wl':
                self.terminal.write_lines(content['lines'])
            if len(self.content)>0 and self.content[-1]['delay']==0:
                self.update(tick,master)
    



class StoryTellerTrigger(Trigger):
    '''反射trigger事件至故事'''
    def __init__(self,source):
        self.source = source
        self.fastmap={}
        self.sort()
    def sort(self):
        self.source.sort(key=lambda x:x['priority'])
        self.fastmap={story['defname']:story for story in self.source}
    def run(self,event,eventrunner):
        for story in self.source:
            if event == story['trigger']:
                if all((self.fastmap[k]['active'] for k in story['need'])):
                    story['active'] = True
                    eventrunner.trigger(story['mirror'])
        return (False,False)
    def complete_story(self,defname):
        self.fastmap[defname]['active'] = True
        return self.fastmap[defname]

class TheHeartofNeuroRunable(Runable):
    def __init__(self,terminal:EntityTerminal,heartheartheart:list,heartdelay:list,destory=None):
        super().__init__()
        self.terminal = terminal
        self.heart = heartheartheart.copy()
        self.heartdelay = heartdelay.copy()
        self.heart.reverse()
        self.heartdelay.reverse()
        self.destory = destory
    def update(self,tick,master):
        if self.lasttick == 0:
            self.lasttick = tick
        if len(self.heart) == 0:
            if self.destory:
                MCO_target_classname('MainInterfaceRunable').framemanager.remove_control(self.destory)
            return True
        if self.lasttick + self.heartdelay[-1] <= tick:
            content = self.heart.pop(-1)
            self.heartdelay.pop(-1)
            self.lasttick=tick
            talkername = resmanager.NameResourceDomain.get_resource('name.talker.'+content[0])
            self.terminal.write(talkername+':'+'\n'.join(content[1]) + '\n',color=resmanager.DefResourceDomain.get_resource('color.talker.'+content[0]))
            if content[4]==0:
                print_dialog(talkername,content[1])



class AirisCoreRunable(Runable):
    def __init__(self,player):
        super().__init__()
        self.player = player
        self.freeze = False
        self.effects={}
        self.key_map={}
    def eventupdate(self,evt):
        if evt.type == pg.locals.KEYDOWN:
            key = evt.dict['key']
            if key == pg.locals.K_j:
                self.player.jump(2.5)
            elif key in range(pg.locals.K_1,pg.locals.K_9+1):
                num = key-pg.locals.K_1+1
                if num in self.key_map:
                    self.key_map[num].oninteracted(self.player)
            elif key==pg.locals.K_r:
                mifr = MCO_target_classname('MainInterfaceRunable')
                if 'debate' in mifr.framemanager.hide:
                    mifr.framemanager.show_control('debate')
                else:
                    mifr.framemanager.hide_control('debate')
    def set_freeze(self,bl):
        self.freeze = bl
    def draw(self,bs):
        pass
    def update(self,tick,master):
        global DIST
        keys = pg.key.get_pressed()
        if keys[pg.locals.K_a]:
            # 向左
            self.player.move(-1)
        elif keys[pg.locals.K_d]:
            # 向右
            self.player.move(1)
        get_world().engine.camera_pos = get_centre_u(self.player.pos, point(0, 0) - get_world().window)+point(0,-80)
        # 处理interact
        engine=get_world().engine
        rm_mark=list(self.effects.keys())
        self.key_map={}
        i=1
        image_args=((250,228,239,249),chinesefont2)
        for entity in itertools.chain(engine.blockeds_line,engine.livings_line,engine.images_line):
            if entity.info and segment_oneforone(self.player,entity):
                specific = hash(entity)
                info = ''
                if entity.interfunc:
                    info ='[%s]' % str(i)
                    self.key_map.update({i:entity})
                    i+=1
                info+=entity.info
                
                if specific not in self.effects:
                    self.effects.update({specific:effect_roll(entity.pos+point(0,-10)-get_world().engine.camera_pos,info,*image_args,fall_vel=0.06,fall_conv=fast_to_slow)})
                    get_world().effects.append(self.effects[specific])
                elif specific in self.effects:
                    rm_mark.remove(specific)
                    self.effects[specific].pos = entity.pos+point(0,-10)-get_world().engine.camera_pos
                    if self.effects[specific].text!=info:
                        self.effects[specific].set_image(info,*image_args)
        for rm in rm_mark:
            get_world().effects.remove(self.effects.pop(rm))




            

class TimerRunable(Runable):
    def __init__(self,func,time):
        super().__init__()
        self.func=func
        self.lasttime=time
        self.lock=False
    def update(self,tick,master):
        if not self.lock:
            self.lock=True
            self.lasttick=tick
        if self.lasttick+self.lasttime<=tick:
            self.func(master)
            return True