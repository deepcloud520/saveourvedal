import sys,time

sys.path.append(sys.path[0] + '/def/saveourvedal')

from rocketcore import *
from evilcore import *
from evilcore import _load_process_
from os import getpid
from annycore import *
import resmanager,pickle,psutil
import pygame.locals as PGKEY
from newcoretiny import *
import airiscore as airis
import hiyoricore as hiyori
from airiscore import MyTrigger,MyTriggerPlus
from storyteller import *
import scriptcore,importlib

# 1d = 24h = 24*60 s
def trans_time(second):
    if second <= 24*30:
        return (second,'s')
    elif second <= 12*24*60:
        return  (second/60,'h')
    else:
        return (second/(60*24),'d')





class EntityTouchPadLeft(EntityTouchPad):
    '''仅可以左右移动的TouchPad'''
    def __init__(self, pos, boxrect, bottomcolor=(20, 65, 70, 80), deep=0, defname='', showdeep=0):
        super().__init__(pos=pos, boxrect=boxrect, bottomcolor=bottomcolor,deep=deep, defname=defname, showdeep=showdeep)
        self.lines=[]
    def eventupdate(self, evt, bias):
        if evt.type == PGKEY.MOUSEBUTTONDOWN and pointin(point(evt.pos[0], evt.pos[1]), self.get_hitbox_pos() - bias,
                                                         self.hitbox.rect):
            self.press = True
        elif evt.type == PGKEY.MOUSEMOTION and self.press:
            self.bias.x += tuple2point(evt.dict['rel']).x
        elif evt.type == PGKEY.MOUSEBUTTONUP:
            self.press = False
    def draw(self,scr,bias):
        for item in self.lines:
            pg.draw.line(scr,(100,100,100,150),
                         point2tuple((item[0]+bias-self.bias)),
                         point2tuple((item[1]+bias-self.bias)),2)
        super().draw(scr,bias)



BUTTONWIDTH = 50
BUTTONHEIGHT = 30
BUTTONBETWEEN = 18
IDNN = (point(-BUTTONWIDTH - BUTTONBETWEEN, 0),
        point(BUTTONWIDTH + BUTTONBETWEEN, 0),
        point(0, -BUTTONHEIGHT - BUTTONBETWEEN),
        point(0, BUTTONHEIGHT + BUTTONBETWEEN))



# 这是TouchPadRight专属映射器
def get_default_mirror(pos, ftype, definedfunction, mirrorname, font, bias):
    # 返回映射按钮
    ret = EntityButton((pos + IDNN[ftype] - bias) if ftype is not None else pos - bias,
                        point(0, 0), point(BUTTONWIDTH, BUTTONHEIGHT),
                        mirrorname, font,
                        (150, 150, 250, 220), (10, 10, 10, 250), definedfunction,
                        deep=0, defname=mirrorname, showdeep=0)
    return ret


def set_mirror(buildframe,tablemiddle):
    def warp2(touchpad):
        # 按钮触发 将焦点转移到按钮映射的stage上
        def warp(defname):
            newfocus=touchpad.stages[defname]
            touchpad.set_focus(newfocus)
            # 更换focus。重设label
            buildframe.get_control('labelfocus').change_text('Focus:' + defname, yaheifont, (20, 80, 50, 10),
                                                             (255, 80, 50, 200))
            buildframe.get_control('labelmass').change_text(resmanager.NameResourceDomain.get_resource('info.build.rocketinfo.mass').replace('[mass]',str(newfocus.mass)), yaheifont, (20, 80, 50, 10),
                                                             (255, 80, 50, 200))
            buildframe.get_control('labelthrust').change_text(resmanager.NameResourceDomain.get_resource('info.build.rocketinfo.thrust').replace('[thrust]',str(newfocus.thrust)), yaheifont, (20, 80, 50, 10),
                                                             (255, 80, 50, 200))
            buildframe.get_control('labelcost').change_text(resmanager.NameResourceDomain.get_resource('info.build.rocketinfo.cost').replace('[cost]',str(newfocus.cost)), yaheifont, (20, 80, 50, 10),
                                                             (255, 80, 50, 200))
            # 传递parts_stack
            tablemiddle.list_clear()
            for part in touchpad.focus.parts_stack:
                tablemiddle.list_append((resmanager.NameResourceDomain.get_resource(resmanager.DefResourceDomain.get_resource(part)['name']),part))
        return warp

    return warp2


buttonmirror = None
def set_buttonmirror(bm):
    global buttonmirror
    buttonmirror = bm
CONNECTCOLOR = ((60,80,250,200),(250,250,250,200))



class EntityTouchPad_Right(EntityTouchPad):
    def __init__(self, pos, boxrect, bottomcolor=(20, 40, 50, 50), def_buttonmirror=None,deep=0, defname='', showdeep=0):
        super().__init__(pos=pos, boxrect=boxrect, bottomcolor=bottomcolor, deep=deep, defname=defname,
                         showdeep=showdeep)
        global buttonmirror
        self.focus = None
        self.stages = {}
        self.lines = {}
        self.main_stage = None
        # 只用一个对象
        self.def_buttonmirror= (buttonmirror(self) if not def_buttonmirror else def_buttonmirror(self))
    def init_stage(self,_stage=None):
        if not _stage:
            _stage=Stage(None)
        self.controllst=[]
        self.stages={}
        self.lines = {}
        self.set_focus(_stage)
        self.stages.update({self.focus.name:self.focus})

        self.add_control(get_default_mirror(point(0, 0), None,
                                            self.def_buttonmirror,
                                            self.focus.name,
                                            font=yaheifont,bias=point(0,0)))
        self.main_stage = self.focus
    def get_focus(self):
        return self.focus

    def set_focus(self, f):
        self.focus = f

    def add_left_child(self, ctype,_stage=None, _focus=None):
        if not _stage:
            _stage=Stage(None)
        if not _focus:
            _focus=self.focus
        temp = _focus.add_left_child(ctype,_stage)
        if temp:
            temp = temp[0]
            self.stages.update({temp.name:temp})
            father = self.get_control(_focus.name)
            child = self.add_control(
                    get_default_mirror(father.pos, LEFT, self.def_buttonmirror, temp.name,
                                       font=yaheifont,bias=self.pos))
            self.lines.update({temp.name:(get_centre(father),get_centre(child),ctype)})

    def add_right_child(self, ctype,_stage=None, _focus=None):
        if not _stage:
            _stage=Stage(None)
        if not _focus:
            _focus=self.focus
        temp = _focus.add_right_child(ctype,_stage)
        if temp:
            temp = temp[0]
            father = self.get_control(_focus.name)
            child = self.add_control(
                    get_default_mirror(father.pos, RIGHT, self.def_buttonmirror, temp.name,
                                       font=yaheifont,bias=self.pos))
            self.stages.update({temp.name:temp})
            self.lines.update({temp.name:(get_centre(father),get_centre(child),ctype)})

    def add_up_child(self, ctype,_stage=None, _focus=None):
        if not _stage:
            _stage=Stage(None)
        if not _focus:
            _focus=self.focus
        temp = _focus.add_up_child(ctype,_stage)
        if temp:
            temp = temp[0]
            father = self.get_control(_focus.name)
            child = self.add_control(
                    get_default_mirror(father.pos, UP, self.def_buttonmirror, temp.name,
                                       font=yaheifont,bias=self.pos))
            self.stages.update({temp.name:temp})
            self.lines.update({temp.name:(get_centre(father),get_centre(child),ctype)})

    def add_down_child(self, ctype,_stage=None, _focus=None):
        if not _stage:
            _stage=Stage(None)
        if not _focus:
            _focus=self.focus
        temp = _focus.add_down_child(ctype,_stage)
        if temp:
            temp = temp[0]
            father = self.get_control(_focus.name)
            child = self.add_control(
                    get_default_mirror(father.pos, DOWN, self.def_buttonmirror, temp.name,
                                       font=yaheifont,bias=self.pos))
            self.stages.update({temp.name:temp})
            self.lines.update({temp.name:(get_centre(father),get_centre(child),ctype)})
    def draw(self,scr,bias):
        for key,item in self.lines.items():
            pg.draw.line(scr,CONNECTCOLOR[item[2]],point2tuple((item[0]+bias-self.bias)),point2tuple((item[1]+bias-self.bias)),1)
        super().draw(scr,bias)



BD_WIDTH = 20  # 底条宽度
class MainInterfaceRunable(Runable):
    
    def __init__(self):
        super().__init__()
        self.reload()
    
    def saveourvedal_open(self,*args):
        #
        # 加载/保存游戏的目的是仅为了*提供可以保存进度的游戏体验*，而不保证*使用S/L大法的游戏与一直游玩的游戏能保持一致*。
        # 保存的只有SaveResourceDomain. 像随机数种子这样的，以及其他长期运行的对象，如TimeCoreRunable，会重新生成
        # *在目前这个版本中* 正在发射的时候发射数据会直接丢失，请注意
        #

        # 从文件中加载pickle
        try:
            f = open(dotpath+'save/default',mode='rb')
        except FileNotFoundError:
            fast_print('file not found')
            return
        resmanager.SaveResourceDomain = pickle.load(f)
        fast_print('open save complete!')
        # 替换播放列表，播放音乐
        DefResourceDomain.get_resource('play_action')('replace play_list',play_list=resmanager.DefResourceDomain.get_resource('music.bd'))
        DefResourceDomain.get_resource('play_action')('playnow source',source=resmanager.DefResourceDomain.get_resource('realmusic.saveload'))
        tcr=TimeCoreRunable()
        get_world().eventrunner.Runables[RING0].append(tcr)
        
        get_world().eventrunner.triggers.insert(0,StoryTellerTrigger(resmanager.SaveResourceDomain.get_resource('story')))
        self.framemanager.hide_all()
        self.framemanager.show_control('bd')
    
    def saveourvedal_newgame(self,*args):
        DefResourceDomain.get_resource('play_action')('playnow source',source=resmanager.DefResourceDomain.get_resource('realmusic.saveload'))
        resmanager.SaveResourceDomain.resource['time']=0
        resmanager.SaveResourceDomain.add_resource('story',resmanager.DefResourceDomain.get_resource('story'))
        resmanager.SaveResourceDomain.add_resource('compute_total',1)
        resmanager.SaveResourceDomain.add_resource('science_points_total',0)
        resmanager.SaveResourceDomain.add_resource('research',resmanager.DefResourceDomain.get_resource('research'))
        resmanager.SaveResourceDomain.add_resource('GUI.build',resmanager.DefResourceDomain.get_resource('GUI.build'))
        resmanager.SaveResourceDomain.add_resource('nowresearch',None)
        resmanager.SaveResourceDomain.add_resource('neuros',1145141919810)
        resmanager.SaveResourceDomain.add_resource('blueprint',{})
        resmanager.SaveResourceDomain.add_resource('medals',{})
        resmanager.SaveResourceDomain.add_resource('stageCounter',Counter('STA'))
        # 加载并替换时间运行器
        tcr=TimeCoreRunable()
        get_world().eventrunner.Runables[RING0].append(tcr)
        # 加载Storyteller
        get_world().eventrunner.triggers.insert(0,StoryTellerTrigger(resmanager.SaveResourceDomain.get_resource('story')))
        # 滚动按钮
        self.rolling_controls()
        # 触发
        get_world().eventrunner.Runables[RING3].append(TimerRunable(trigger('newgame'),1//0.01))
    
    def saveourvedal_build(self,*args):
        window = get_world().window
        top = point(0, window.y - BD_WIDTH)
        # 建造界面
        buildframe = EntityFrame(point(0, 0), point(window.x, top.y), defname='build', bottomcolor=(18,20,18,200))
        # 左偏中 显示每段的部件
        tablemiddle = EntityTable(point(window.x*0.2,0),point(window.x*0.2-10,window.y*0.8),
                                          mirror=middle_label_mirror)
        # 右侧触屏 stage
        set_buttonmirror(set_mirror(buildframe,tablemiddle))
        touchpadright = EntityTouchPad_Right(point(window.x * 0.4, 0),
                                                     point(window.x * 0.6, window.y - 35 - 20),
                                                     (40, 160, 40, 155),
                                                     defname='tpr')
        ete=EntityTextEditer(point(window.x*0.4, 2), point(0, 0), point(window.x*0.3-10,25),qingkongsmall,(20, 80, 50, 10), (165, 120, 189, 200))
        
        buildframe.add_control(touchpadright)
        buildframe.add_control(tablemiddle)
        buildframe.add_control(ete)
        
        
        def update_info():
            buildframe.get_control('labelmass').change_text(resmanager.NameResourceDomain.get_resource('info.build.rocketinfo.mass').replace('[mass]',str(touchpadright.focus.mass)), yaheifont, (20, 80, 50, 10),
                                                             (255, 80, 50, 200))
            buildframe.get_control('labelthrust').change_text(resmanager.NameResourceDomain.get_resource('info.build.rocketinfo.thrust').replace('[thrust]',str(touchpadright.focus.thrust)), yaheifont, (20, 80, 50, 10),
                                                             (255, 80, 50, 200))
            buildframe.get_control('labelcost').change_text(resmanager.NameResourceDomain.get_resource('info.build.rocketinfo.cost').replace('[cost]',str(touchpadright.focus.cost)), yaheifont, (20, 80, 50, 10),
                                                             (255, 80, 50, 200))
                
        def mtablepop(defname):
            tablemiddle.list_pop(-1)
            try:
                touchpadright.focus.parts_stack.pop(-1)
                touchpadright.focus.update_info()
                update_info()
            except IndexError:
                fast_print('已经没有东西了！')
                
        def mtableclear(defname : str):
            tablemiddle.list_clear()
            touchpadright.focus.parts_stack = []
            touchpadright.focus.update_info()
            update_info()
                
        def mtablesave(defname : str):
            # 临时用
            if ete.text:
                resmanager.SaveResourceDomain.get_resource('blueprint').update({ete.text:touchpadright.main_stage})
            else:
                fast_print('Name Filited')
        # 打开蓝图 将mainstage重新写到touchpadright中
        def stageopen(args):

            stage=args[0]
            name=args[1]

            def warp_(wstage):
                # 递归加载火箭stage
                if wstage.left_child:
                    touchpadright.add_left_child(wstage.left_child[1],_stage=wstage.left_child[0],_focus=wstage)
                    warp_(wstage.left_child[0])
                if wstage.right_child:
                    touchpadright.add_right_child(wstage.right_child[1],_stage=wstage.right_child[0],_focus=wstage)
                    warp_(wstage.right_child[0])
                if wstage.up_child:
                    touchpadright.add_up_child(wstage.up_child[1],_stage=wstage.up_child[0],_focus=wstage)
                    warp_(wstage.up_child[0]) 
                if wstage.down_child:
                    touchpadright.add_down_child(wstage.down_child[1],_stage=wstage.down_child[0],_focus=wstage)
                    warp_(wstage.down_child[0]) 
            
            touchpadright.init_stage(stage)
            warp_(stage)
            # 使用set_mirror函数的功能,更新一系列数据
            set_mirror(buildframe,tablemiddle)(touchpadright)(stage.name)
            # 改掉TextEditer
            ete.text = name
            ete.change_text()
        # 蓝图的打开选择界面
        def buildopen(defname):
            if buildframe.get_control('fbuildopen'):
                buildframe.remove_control('fbuildopen')
                return
            # 设置
            buildopenframe=EntityFrame(point(window.x*0.3,window.y*0.3),point(window.x*0.4,window.y*0.4),defname='fbuildopen')
            ot=EntityTable(point(0,0),point(window.x*0.4,window.y*0.4-20),
                                          mirror=left_button_mirror,defname='opentable')
            buildopenframe.add_control(ot)
            buildframe.add_control(buildopenframe)
            for name,stage in resmanager.SaveResourceDomain.get_resource('blueprint').items():
                ot.list_append((name,(stage,name),stageopen))
            
                
        buildframe.add_control(EntityButton(point(window.x*0.2, window.y*0.8), point(0, 0),point(window.x*0.1-5,35),
                                                'Pop',
                                               yaheibig,
                                               (20, 80, 50, 10),(36,206,144,200), defname='Pop',definedfunction=mtablepop))
        buildframe.add_control(EntityButton(point(window.x*0.3-5, window.y*0.8), point(0, 0),point(window.x*0.1-5,35),
                                                   'Clear',
                                                   yaheibig,
                                                   (20, 80, 50, 10),(36,206,144,200), defname='Clear',definedfunction=mtableclear))
                
        buildframe.add_control(EntityButton(point(window.x*0.2, window.y*0.8+35), point(0, 0),point(window.x*0.1-5,35),
                                                   'Save',
                                                   yaheibig,
                                                   (20, 80, 50, 10),(36,206,144,200), defname='save',definedfunction=mtablesave))
        buildframe.add_control(EntityButton(point(window.x*0.3-5, window.y*0.8+35), point(0, 0),point(window.x*0.1-5,35),
                                                   'Open',
                                                   yaheibig,
                                                   (20, 80, 50, 10),(36,206,144,200), defname='open',definedfunction=buildopen))
                
        # 左侧 向火箭stage中加减元件
        tableleft = EntityTable(point(0,0),point(window.x*0.2,window.y*0.8),mirror=left_button_mirror,bottomcolor=(20,40,50,90))
        buildframe.add_control(tableleft)
        def add_part(defname):
            res=resmanager.DefResourceDomain.get_resource(defname)
            if res['class']=='Pod' and touchpadright.focus!=touchpadright.main_stage:
                fast_print('你不能在其他地方放置控制仓！')
                return
            tablemiddle.list_append((resmanager.NameResourceDomain.get_resource(res['name']),defname))
            touchpadright.focus.parts_stack.append(defname)
            touchpadright.focus.update_info()
            update_info()
        def tableshift(name):
            # 清楚明白
            tableleft.list_clear()
            for item in resmanager.SaveResourceDomain.get_resource('GUI.build')[name]:
                # 写一个加的函数
                tableleft.list_append((resmanager.NameResourceDomain.get_resource(resmanager.DefResourceDomain.get_resource(item)['name']),item,add_part))
        buildframe.add_control(EntityButton(point(0, window.y*0.8), point(0, 0),point(80,25),
                                                'Pod',
                                               yaheibig,
                                               (80,190,230,100), (180, 160, 250, 200), defname='Pod',definedfunction=tableshift))
        buildframe.add_control(EntityButton(point(80, window.y*0.8), point(0, 0),point(80,25),
                                                'Thrust',
                                               yaheibig,
                                               (80,190,230,100), (180, 160, 250, 200), defname='Thrust',definedfunction=tableshift))
        buildframe.add_control(EntityButton(point(0, window.y*0.8+25), point(0, 0),point(80,25),
                                                'Fuel',
                                               yaheibig,
                                               (80,190,230,100), (180, 160, 250, 200), defname='Fuel',definedfunction=tableshift))

        buildframe.add_control(EntityLabel(point(window.x * 0.7+10, 15), point(0, 0),
                                                   'Focus:None',
                                                   yaheifont,
                                                   (20, 80, 50, 10), (255, 80, 50, 200), defname='labelfocus'))
                
                
        buildframe.add_control(EntityLabel(point(window.x*0.4+2, window.y*0.7), point(0, 0),
                                                   '',
                                                   yaheifont,
                                                   (20, 80, 50, 10), (255, 80, 50, 200), defname='labelmass'))
        buildframe.add_control(EntityLabel(point(window.x*0.4+2, window.y*0.7+25), point(0, 0),
                                                   '',
                                                   yaheifont,
                                                   (20, 80, 50, 10), (255, 80, 50, 200), defname='labelthrust'))
        buildframe.add_control(EntityLabel(point(window.x*0.4+2, window.y*0.7+50), point(0, 0),
                                                   '',
                                                   yaheifont,
                                                   (20, 80, 50, 10), (255, 80, 50, 200), defname='labelcost'))
                
                
        # 底下的5个控制按钮
        tprlength = touchpadright.hitbox.rect.x
        begin = touchpadright.get_hitbox_pos().x
        tprwidth = touchpadright.hitbox.rect.y
        def warp_delete(target):
            touchpadright.remove_control(target.name)
            if target.left_child:
                warp_delete(target.left_child[0])
            if target.right_child:
                warp_delete(target.right_child[0])
            if target.up_child:
                warp_delete(target.up_child[0])
            if target.down_child:
                warp_delete(target.down_child[0])
            touchpadright.lines.pop(target.name)
        def handlebutton(defname):
            if not touchpadright.focus:
                return
            state = buildframe.get_control('state').statenum
            if state == 2:
                # 删除
                try:
                    if defname=='left':
                        warp_delete(touchpadright.focus.left_child[0])
                        touchpadright.focus.left_child = None
                    elif defname=='right':
                        warp_delete(touchpadright.focus.right_child[0])
                        touchpadright.focus.right_child = None
                    elif defname=='up':
                        warp_delete(touchpadright.focus.up_child[0])
                        touchpadright.focus.up_child = None
                    elif defname=='down':
                        warp_delete(touchpadright.focus.down_child[0])
                        touchpadright.focus.down_child = None
                except TypeError:
                    fast_print('不知道是为什么，反正就是不能这么做！')
                    #MainInterfaceRunable.__init__.build.handlebutton
            else:
                if defname=='left' and not touchpadright.focus.left_child:
                    touchpadright.add_left_child(state)
                elif defname=='right' and not touchpadright.focus.right_child:
                    touchpadright.add_right_child(state)
                elif defname=='up' and not touchpadright.focus.up_child:
                    touchpadright.add_up_child(state)
                elif defname=='down' and not touchpadright.focus.down_child:
                    touchpadright.add_down_child(state)
        
        # 显示对火箭段控制的5个按钮
        buildframe.add_control(EntityButton(point(begin, tprwidth), point(0, 0),point(tprlength*0.2,35),
                                            'LEFT',
                                            yaheifont,
                                            (20, 80, 50, 10), (255, 80, 50, 200), definedfunction=handlebutton,
                                            defname='left'))
        buildframe.add_control(EntityButton(point(begin+tprlength*0.2, tprwidth), point(0, 0),point(tprlength*0.2,35),
                                            'RIGHT',
                                            yaheifont,
                                            (20, 80, 50, 10), (255, 80, 50, 200), definedfunction=handlebutton,
                                            defname='right'))
        buildframe.add_control(EntityButton(point(begin+tprlength*0.4, tprwidth), point(0, 0),point(tprlength*0.2,35),
                                            'UP',
                                            yaheifont,
                                            (20, 80, 50, 10), (255, 80, 50, 200), definedfunction=handlebutton,
                                            defname='up'))
        buildframe.add_control(EntityButton(point(begin+tprlength*0.6, tprwidth), point(0, 0),point(tprlength*0.2,35),
                                            'DOWN',
                                            yaheifont,
                                            (20, 80, 50, 10), (255, 80, 50, 200), definedfunction=handlebutton,
                                            defname='down'))
        buildframe.add_control(EntitySwitch(point(begin+tprlength*0.8, tprwidth), point(0, 0),point(tprlength*0.2,35),
                                            yaheifont,
                                            (20, 80, 50, 10), (255, 80, 50, 200), stateenum={0:'Ha',1:'Se',2:'Rm'},
                                            defname='state'))
        # 显示建造界面，准备初始stage和映射
        if not self.framemanager.add_control(buildframe, mux=True):
            # 互斥。清除原数据
            self.framemanager.remove_control('build')
            self.framemanager.add_control(buildframe, mux=True)
        self.framemanager.hide_all()
        self.framemanager.show_control('bd')
        self.framemanager.show_control('build')

        touchpadright.init_stage()
        buildframe.get_control('labelfocus').change_text('Focus:' + touchpadright.focus.name, yaheibig, (80, 100, 80, 200),
                                                            (255, 80, 50, 200))
    def rolling_controls(self):
        label_neuro=self.framemanager.get_control('main').get_control('label_neuro')
        button_startgame=self.framemanager.get_control('main').get_control('button_startgame')
        button_resume=self.framemanager.get_control('main').get_control('button_resume')
        button_exit=self.framemanager.get_control('main').get_control('button_exit')
        get_world().eventrunner.Runables[RING3].append(RollControlRunable(control=label_neuro,targetpos=label_neuro.pos-point(250,0), rolling=slow_to_fast,vel=0.04))
        get_world().eventrunner.Runables[RING3].append(RollControlRunable(control=button_startgame,targetpos=button_startgame.pos-point(250,0), rolling=slow_to_fast,vel=0.02))
        get_world().eventrunner.Runables[RING3].append(RollControlRunable(control=button_resume,targetpos=button_resume.pos-point(250,0), rolling=slow_to_fast,vel=0.018))
        get_world().eventrunner.Runables[RING3].append(RollControlRunable(control=button_exit,targetpos=button_exit.pos-point(250,0), rolling=slow_to_fast,vel=0.015))
    
    def saveourvedal_info(self,*args):
        infoframe=self.framemanager.get_control('info')
        infoframe.controllst=[]
        create_textlines(infoframe,
                             map(lambda x:x.replace('[neuros]',str(resmanager.SaveResourceDomain.get_resource('neuros'))).replace('[science_points_total]',str(resmanager.SaveResourceDomain.get_resource('science_points_total'))).replace('[compute_total]',str(resmanager.SaveResourceDomain.get_resource('compute_total'))),
                                 resmanager.NameResourceDomain.get_resource('info.maininfo')),
                                 qingkongsmall,point(2,2),2,(0,0,0,0),(123,234,234,250)
                                 )
        create_textlines(infoframe,
                             map(lambda x:resmanager.NameResourceDomain.get_resource(x['info']),resmanager.SaveResourceDomain.get_resource('medals').values()),
                                 qingkongsmall,point(2,170),2,(50,50,50,50),(234,234,123,250)
                                 )
        
        self.framemanager.hide_all()
        self.framemanager.show_control('info')
        self.framemanager.show_control('bd')
    
    def saveourvedal_research(self,*args):
        window=get_world().window

        top = point(0, window.y - BD_WIDTH)
        researchframe = EntityTouchPadLeft(point(0, 0), point(window.x-250,top.y), defname='research',bottomcolor=(30,90,90,90))
        researchinfo = EntityFrame(point(window.x-250, 0), point(250,top.y), bottomcolor=(25,35,40,230),defname='rsinfo')
        rtree=resmanager.SaveResourceDomain.get_resource('research')

        def set_research(defname):
            # 重设置研究对象，填充researchinfo
            researchinfo = self.framemanager.get_control('rsinfo')
            
            researchinfo.controllst=[]
            start_pos=point(4,40)
            resear=resmanager.SaveResourceDomain.get_resource('research')[defname]
                
            for info in resmanager.NameResourceDomain.get_resource(resear['info']):
                researchinfo.add_control(EntityLabel(start_pos,point(0,0),info,
                                                         qingkongsmall,(0,0,0,0),(200,200,200,250)))
                start_pos.y+=20
            # 解锁部件
            researchinfo.add_control(EntityLabel(start_pos,point(0,0),resmanager.NameResourceDomain.get_resource('info.research.tail.part_start'),
                                                    qingkongsmall,(40,40,40,50),(82,121,240,250)))
            start_pos.y+=20
            for info,type_ in resear['part']:
                researchinfo.add_control(EntityLabel(start_pos,point(0,0),resmanager.NameResourceDomain.get_resource(resmanager.DefResourceDomain.get_resource(info)['name']),
                                                         qingkongsmall,(0,0,0,0),(82,121,240,250)))
                start_pos.y+=20
            # 小尾巴
            science_points=resear['science_points']
            compute_points=resear['compute_points']
            remain=compute_points/resmanager.SaveResourceDomain.get_resource('compute_total')
            for info in resmanager.NameResourceDomain.get_resource('info.research.tail'):
                researchinfo.add_control(EntityLabel(start_pos,point(0,0),
                                                         info.replace('[science_points]',str(science_points)).replace('[compute_points]',str(compute_points)).replace('[remain]',str(remain)),
                                                         qingkongsmall,(0,0,0,0),(160,250,250,250)))
                    
                start_pos.y+=20
            # 研究状态判断
            for need in resear['need_research']:
                need=rtree[need]
                if need['compute_points']>0 or need['science_points']>0:
                    info='info.research.tail.science_need'
                    break
            else:
                if compute_points==0 and science_points==0:
                    info='info.research.tail.complete'
                elif resmanager.SaveResourceDomain.get_resource('science_points_total')<science_points:
                    info='info.research.tail.science_points_need'
                else:
                    info='info.research.tail.success'
                    resmanager.SaveResourceDomain.resource['science_points_total']-=science_points
                    resear['science_points']=0
                    resmanager.SaveResourceDomain.add_resource('nowresearch',defname)
                
            researchinfo.add_control(EntityLabel(start_pos,point(0,0),
                                                resmanager.NameResourceDomain.get_resource(info),
                                                qingkongsmall,(0,0,0,0),(100,190,160,250)))
            researchinfo.add_control(EntityLabel(point(2,2),point(0,0),resmanager.NameResourceDomain.get_resource(resear['name']),
                                                 qingkongbig,(0,0,0,0),(190,190,220,250)))
        
        # 填充研究树    
        BUTTONSIZE = point(100,25)
        for rsname,rsitem in rtree.items():
            fatherpos=str2point(rsitem['pos'])
            researchframe.add_control(EntityButtonImmerse(fatherpos, point(0, 0), BUTTONSIZE, resmanager.NameResourceDomain.get_resource(rsitem['name']),
                                                       qingkongverysmall, (100, 100, 100, 100),(200, 200, 200, 200),set_research,press_speed=0.02,defname=rsname,fill_bottom=False))
            fatherpos_u=get_centre_u(fatherpos,BUTTONSIZE)
            for need in rsitem['need_research']:
                researchframe.lines.append(
                                              (fatherpos_u,get_centre_u(str2point(rtree[need]['pos']),BUTTONSIZE))
                                              )
            
        
        # 添加researchframe   
        if not self.framemanager.add_control(researchframe, mux=True):
            # 互斥。清除原数据
            self.framemanager.remove_control('research')
            self.framemanager.remove_control('rsinfo')
        
        self.framemanager.add_control(researchframe, mux=True)
        self.framemanager.add_control(researchinfo)
        
        self.framemanager.hide_all()
        
        self.framemanager.show_control('research')
        self.framemanager.show_control('rsinfo')
        self.framemanager.show_control('bd')

    def saveourvedal_launch(self,*args):
        window = get_world().window
        # 是的我又在超代码 事build中的buildopen
        if self.framemanager.get_control('flaunchopen'):
            self.framemanager.remove_control('flaunchopen')
            return
        # 设置的是选择发射的界面
        launchopenframe=EntityFrame(point(window.x*0.1,window.y*0.1),point(window.x*0.8,window.y*0.8),defname='flaunchopen',bottomcolor=(160,167,188,200))
        self.framemanager.add_control(launchopenframe)

        launchopenframe.add_control(EntityLabel(point(window.x*0.4-50,window.y*0.8-30),point(0,0),
                                                      resmanager.NameResourceDomain.get_resource('info.launch.bottom'),qingkongbig,(0,0,0,0),(220,220,255,220)))
        ot=EntityTable(point(2,2),point(window.x*0.8,window.y*0.8-30),
                                          mirror=launch_button_mirror,bottomcolor=(160,167,188,25),defname='opentable')
        launchopenframe.add_control(EntityStatImage(point(window.x*0.8-100,window.y*0.8-180),point(0,0),
                                                      resmanager.DefResourceDomain.get_resource('texture.stall.neuro')))
            
        def launch(args):
            stage,name = args
            # 开始构建火箭！！
            rocket=EntityLiving_Rocket(point(0,-120),stage)
            # 我不正常
            rocket.update_info()
                
            cost=sum(map(lambda x:x.cost,rocket.parts)) # 计算价格
            if resmanager.SaveResourceDomain.get_resource('neuros')<cost:
                # 在这个版本触发这个也真的很困难
                fast_print('Neuro提醒您：再去攒点money！')
                return
            # 准备工作
            class RocketStateUpdaterRunable(Runable):
                def __init__(self,rocket,k_att_label,k_vel_label,resource_labels):
                    super().__init__()
                    self.rocket=rocket
                    self.k_att_label=k_att_label
                    self.k_vel_label=k_vel_label
                    self.resource_labels = resource_labels
                def update(self,tick,master):
                    if self.lasttick + 10 <= tick:
                        self.lasttick = tick
                        self.k_att_label.change_text('{:0>6}'.format((abs(int(self.rocket.get_attitude())))), led1,(0,0,0,0),(0,200,200,255))
                        self.k_vel_label.change_text('%s m/s' % str(int(rocket.get_realvel())), yaheibig,(0,0,0,0),(123,234,248,213))
                        
                        i = 0
                        for name,num in self.rocket.resource.items():
                            cons = self.rocket.resource_consumption[name]
                            eta = trans_time(num//cons//50) if cons!=0 else (0,'-')
                            self.resource_labels[i].change_text('%s: %s [%s] ETA %s' % (name, '{:.2f}'.format(num), '{:.2f}'.format(cons), str(int(eta[0]))+eta[1],),
                                                                yaheifont,(0,0,0,0),((198,167,244,250) if eta[1]!='s' or eta[0]>=30 else (244,127,158,250)),)
                            i+=1
            def warp_(wstage):
                # 从build哪里超的
                # controlpad.set_foucs(wstage)
                if wstage.left_child:
                    controlpad.add_left_child(wstage.left_child[1],_stage=wstage.left_child[0],_focus=wstage)
                    warp_(wstage.left_child[0])
                if wstage.right_child:
                    controlpad.add_right_child(wstage.right_child[1],_stage=wstage.right_child[0],_focus=wstage)
                    warp_(wstage.right_child[0])
                if wstage.up_child:
                    controlpad.add_up_child(wstage.up_child[1],_stage=wstage.up_child[0],_focus=wstage)
                    warp_(wstage.up_child[0]) 
                if wstage.down_child:
                    controlpad.add_down_child(wstage.down_child[1],_stage=wstage.down_child[0],_focus=wstage)
                    warp_(wstage.down_child[0]) 
            def stageactive(cp):
                def warp(defname):
                    # 激活所选焦点
                    stage=rocket.stages[defname]
                    cp.focus=stage
                    if stage.active:
                        stage.active=False
                    else:
                        stage.active=True
                return warp
            controlpad=EntityTouchPad_Right(point(window.x-400,0),point(400,window.y-100),(10,20,30,40),
                                                def_buttonmirror=stageactive,
                                                defname='cp')
            def sepa():
                def warp_delete(target):
                    controlpad.remove_control(target.name)
                    if target.left_child:
                        warp_delete(target.left_child[0])
                    if target.right_child:
                        warp_delete(target.right_child[0])
                    if target.up_child:
                        warp_delete(target.up_child[0])
                    if target.down_child:
                        warp_delete(target.down_child[0])
                    controlpad.lines.pop(target.name)
                if controlpad.focus.name not in rocket.connects:
                    fast_print('你不能这么分离！')
                    return
                father=rocket.stages[rocket.connects[controlpad.focus.name]]
                if father.left_child and father.left_child[0].name==controlpad.focus.name:
                    father.left_child=None
                elif father.right_child and father.right_child[0].name==controlpad.focus.name:
                    father.right_child=None
                elif father.down_child and father.down_child[0].name==controlpad.focus.name:
                    father.down_child=None
                elif father.up_child and father.up_child[0].name==controlpad.focus.name:
                    father.up_child=None
                rocket.connects.pop(controlpad.focus.name)
                TS=rocket.part_clear()
                rocket.stages=TS
                warp_delete(controlpad.focus)
                controlpad.focus=father
                print(rocket.vel)
            def back():
                get_world().engine.clear_all()
                self.framemanager.remove_control('cf')
                self.framemanager.remove_control('cp')
                self.framemanager.remove_control('sf')
                self.framemanager.show_control('bd')
                get_world().eventrunner.remove_runable(RING2,RocketStateUpdaterRunable)
                DefResourceDomain.get_resource('play_action')('resume')
            DefResourceDomain.get_resource('play_action')('stop')
            resmanager.SaveResourceDomain.resource['neuros']-=cost # 失去金金金金，钱钱钱钱            
            self.framemanager.hide_all()
            controlpad.init_stage(rocket.stages[rocket.mainstage.name])
            controlframe = EntityFrame(point(window.x-200, window.y-100), point(200,100),defname='cf')
            controlframe.add_control(
                EntityButtonImmerse(point(50, 0), point(0,0), point(100, 35), 'SEPA', qingkongbig,
                     (148,131,175,255), (148,131,175,200), sepa,press_speed=0.032))
            controlframe.add_control(
                EntityButtonImmerse(point(0, 35), point(0,0), point(200, 35), 'Finish Mission', qingkongbig,
                     (148,131,175,255), (148,131,175,200), back,press_speed=0.042))
            self.framemanager.add_control(controlframe) 
            # 火箭状态显示                
            stateframe = EntityFrame(point(0, 0), point(window.x,50),bottomcolor=(40,80,40,60),defname='sf')
            att_label=EntityLabel(point(window.x//2-120,0),point(0,0),'000000',led1,(0,0,0,0),(220,255,255,255))
            vel_label=EntityLabel(point(window.x//2+70,0),point(0,0),'0 m/s',yaheibig2,(0,0,0,0),(220,255,255,255))
            stateframe.add_control(att_label)
            stateframe.add_control(vel_label)
            self.framemanager.add_control(stateframe)
            resource_labels = tuple(
                [stateframe.add_control(
                    EntityLabel(point(20,10 + 19*i ),point(0,0),'Connecting...',yaheibig2,(0,0,0,0),(255,255,180,255))) for i in range(len(rocket.resource))
                    ]
                )
            get_world().eventrunner.Runables[RING2].append(RocketStateUpdaterRunable(rocket,att_label,vel_label,resource_labels))
                
            warp_(rocket.stages[rocket.mainstage.name]) # 递归添加到控制版上
            #if not self.framemanager.add_control(controlpad, mux=True):
            #    # 互斥。清除原数据
            #    self.framemanager.remove_control('cp')
            self.framemanager.add_control(controlpad, mux=True)
                
            # 出现吧！
            get_world().engine.livings_line.append(rocket)
            get_world().engine.blockeds_line=[]
            class EntityImageBlocked(EntityBlocked):
                def draw(self, scr, bias):
                    if abs(bias.y)<1000:
                        scr.blit(DefResourceDomain.get_resource('texture.terr'),point2tuple(self.pos - bias + self.hitbox.pos))
            get_world().engine.blockeds_line.append(EntityImageBlocked(point(-400, 0), point(800, 100)))
        
        launchopenframe.add_control(ot)
        for name,stage in resmanager.SaveResourceDomain.get_resource('blueprint').items():
            ot.list_append((name,(stage,name),launch))
    
    def reload(self):
        loclogger.info('loading MainInterface...')

        self.framemanager = FrameManager()
        
        # 加载音乐
        mcr=DefResourceDomain.get_resource('MusicCoreRunableType')()
        
        get_MCO().append(mcr)
        resmanager.DefResourceDomain.add_resource('play_action',mcr.play_action)
        window = get_world().window.copy()
        BD_WIDTH = 20  # 底条宽度
        top = point(0, window.y - BD_WIDTH)

        #     
        # 底条
        #

        bottomdisplay = EntityFrame(point(0,0), window.copy(), defname='bd')
        bottomdisplay.add_control(
            EntityStatImage(point(0, 0), point(0,0), resmanager.DefResourceDomain.get_resource(resmanager.ConfigResourceDomain.get_resource('saveourvedal')['background'][0]))
            )
        bottomdisplay.add_control(
            EntityButton(point(0, window.y - BD_WIDTH), point(0, 0), point(window.x*0.2, BD_WIDTH), 'Info', yaheifont, (100, 100, 200, 100),
                         (158,231,175,200),self.saveourvedal_info))
        bottomdisplay.add_control(
            EntityButton(point(window.x*0.2, window.y - BD_WIDTH), point(0, 0), point(window.x*0.2, BD_WIDTH), 'Build', yaheifont, (100, 100, 200, 100),
                         (148,231,185,200), self.saveourvedal_build))
        bottomdisplay.add_control(
            EntityButton(point(window.x*0.4, window.y - BD_WIDTH), point(0, 0), point(window.x*0.2, BD_WIDTH), 'Launch', yaheifont, (100, 100, 200, 100),
                         (178,221,175,200), self.saveourvedal_launch))
        bottomdisplay.add_control(
            EntityButton(point(window.x*0.6, window.y - BD_WIDTH), point(0, 0), point(window.x*0.2, BD_WIDTH), 'Research', yaheifont, (100, 100, 200, 100),
                         (148,231,175,200),self.saveourvedal_research))
        bottomdisplay.add_control(
            EntityLabel(point(window.x*0.8, window.y - BD_WIDTH), point(0,0),'0 H', yaheifont, (100, 100, 200, 100),
                         (148,211,195,200),defname='time'))

        self.framemanager.add_control(bottomdisplay)
        
        #
        # 概况
        #
        
        infoframe = EntityFrame(point(0, 0), point(window.x,top.y), bottomcolor=(10,10,30,200),defname='info')
        self.framemanager.add_control(infoframe)
        self.framemanager.hide_control('info')
        
        #
        # 开始界面
        #

        mainframe = EntityFrame(point(0, 0), window, defname='main')

        mainframe.add_control(
            EntityStatImage(point(0,0),point(0,0),
                        resmanager.DefResourceDomain.get_resource(resmanager.ConfigResourceDomain.get_resource('entiy'))))
        label_neuro = EntityLabel(point(20, window.y-190), point(0, 0), 'Neuro是大家的!!', qingkongbig,
                        (20, 80, 50, 10), (255, 180, 150, 200),defname='label_neuro')
        button_startgame = EntityButtonImmerse(point(20, window.y-150), point(0, 0), point(150, 30), 'NewGame', yaheifont,
                         (187,198,203,255), (187,198,203,255), self.saveourvedal_newgame,press_speed=0.02,defname='button_startgame')
        button_resume = EntityButtonImmerse(point(20, window.y-110), point(0, 0), point(150, 30), 'ResumeGame', yaheifont,
                         (187,198,203,255), (187,198,203,255), self.saveourvedal_open,press_speed=0.02,defname='button_resume')
        button_exit = EntityButtonImmerse(point(20, window.y-70), point(0, 0), point(150, 30), 'Exit', yaheifont,
                         (187,198,203,255), (187,198,203,255), sys.exit,press_speed=0.02,defname='button_exit')
        canvas = EntityCanvas(point(200, window.y-300), point(0, 0), point(28, 28), scalx=5)
        canvas2 = EntityCanvas(point(400, window.y-300), point(0, 0), point(28, 28), scalx=5)
        get_world().eventrunner.Runables[RING3].append(RollControlRunable(control=label_neuro,targetpos=label_neuro.pos,startpos=label_neuro.pos-point(200,0),rolling=fast_to_slow,vel=0.04))
        get_world().eventrunner.Runables[RING3].append(RollControlRunable(control=button_startgame,targetpos=button_startgame.pos,startpos=button_startgame.pos-point(200,0),rolling=fast_to_slow,vel=0.02))
        get_world().eventrunner.Runables[RING3].append(RollControlRunable(control=button_resume,targetpos=button_resume.pos,startpos=button_resume.pos-point(200,0),rolling=fast_to_slow,vel=0.018))
        get_world().eventrunner.Runables[RING3].append(RollControlRunable(control=button_exit,targetpos=button_exit.pos,startpos=button_exit.pos-point(200,0),rolling=fast_to_slow,vel=0.015))
        

        mainframe.add_control(button_startgame)
        mainframe.add_control(button_resume)
        mainframe.add_control(label_neuro)
        mainframe.add_control(button_exit)


        # 对话框
        debateframe = EntityFrameDebate(point(window.x-DIALOG_WIDTH, 0), point(DIALOG_WIDTH,window.y), defname='debate')
        self.framemanager.add_control(debateframe)
        self.framemanager.hide_control('debate')
            
        self.framemanager.add_control(mainframe)
        self.framemanager.hide_control('bd')
        
        loclogger.info('loading music...')
        # 加载音乐
        _load_process_(resmanager.NameResourceDomain.get_resource('info.loadmusic'))
        
        load_singlesound('music.saveload')
        load_singlesound('music.entiy')
        '''
        musicbd__ = resmanager.DefResourceDomain.get_resource('music.bd')
        # 歌曲本身没有扩展名
        print(musicbd__)
        musicbd = {name:real for name,real in zip(musicbd__,resmanager.DefResourceDomain.get_resource('realmusic.bd'))}
        resmanager.DefResourceDomain.add_resource('realmusic.bd',musicbd)
        '''
        entiy = resmanager.DefResourceDomain.get_resource('music.entiy')
        realentiy = resmanager.DefResourceDomain.get_resource('realmusic.entiy')
        DefResourceDomain.get_resource('play_action')('replace play_list',play_list={entiy:realentiy})
        
        self.add_story()
    def update(self, tick,display):
        self.framemanager.update(tick)
    def draw(self, bs):
        self.framemanager.draw(bs, point(0, 0))
    def eventupdate(self, se):
        self.framemanager.eventupdate(se, point(0, 0))
    def add_story(self):
        loclogger.info('loading storybook...')
        def load_script(scriptname):
            scr = importlib.import_module(scriptname)
            scr.open_storybook(self)
        load_script('story0')







class TimeCoreRunable(Runable):
    def __init__(self):
        super().__init__()
    def next_hour(self):
        resmanager.SaveResourceDomain.resource['time']+=1
        MCO_target_classname('MainInterfaceRunable').framemanager.get_control('bd').get_control('time').change_text(str(resmanager.SaveResourceDomain.resource['time'])+' H',
                                                                                 yaheifont,
                                                                                 (100, 100, 200, 100),
                                                                                 (148,231,175,200))
        # 研究。还有其他什么东西也要写写
        rese=resmanager.SaveResourceDomain.get_resource('nowresearch')
        rtree=resmanager.SaveResourceDomain.get_resource('research')
        if rese:
            temp=rtree[rese]
            temp['compute_points']-=resmanager.SaveResourceDomain.get_resource('compute_total')
            if temp['compute_points']<=0:
                temp['compute_points']=0
                #research complete
                for part,_type in temp['part']:
                    resmanager.SaveResourceDomain.resource['GUI.build'][_type].append(part)
                resmanager.SaveResourceDomain.resource['nowresearch']=None
        # auto save
        if resmanager.SaveResourceDomain.resource['time'] % 30 ==0:
            fast_print('start auto save....')
            save()
                
    def update(self, tick, world):
        if self.lasttick+60<=tick:
            self.lasttick=tick
            self.next_hour()
            

    def eventupdate(se):
        pass
'''
class TriviaRunable(Runable):
    def __init__(self,ter,trivia='trivia.act0'):
        super().__init__()
        self.terminal = ter
        self.trivia = DefResourceDomain.get_resource(trivia)
        
        self.questions = self.trivia["questions"]
        self.stat = {'N':-1,"choice":0}
        self.flush()
    def set_at(self,pos,char):
        self.screen[pos.y][1][pos.x] = char

    def set_line(self,pos,line):
        bias=point(0,0)
        for char in line:
            self.set_at(pos+bias,char)
            bias.x+=1
        
    def eventrunner(self,singleevent):
        pass

    def update(self,tick):
        if self.lasttick+10<=tick:
            self.flush()
            self.set_line(point(0,1),str(self.stat['N']))
    def flush():
        self.screen = copy.copy(self.trivia["start_screen"])
    def screen_update(self):
        self.terminal.screen = self.screen
'''



# 似乎没有用
class FadeInAndOut(Runable):
    def __init__(self,fadetime,lasttime):
        # 单位：tick
        self.fadetime=fadetime
        self.lasttime=lasttime
        self.lasttick=None
        self.buffer_alpha=0
        self.fade_speed=255/fadetime
    def update(self,tick,eventrunner):
        if not self.lasttick:
            self.lasttick=tick
        elif tick-self.lasttick<=self.fadetime:
            self.buffer_alpha += self.fade_speed
            eventrunner.master.buffersurface.fill((0,0,0,int(self.buffer_alpha)))
        elif 0 <= tick-self.lasttick-self.fadetime-self.lasttime<=self.fadetime:
            self.buffer_alpha -= self.fade_speed
            eventrunner.master.buffersurface.fill((0,0,0,int(self.buffer_alpha)))
        else:
            
            return True



def save(*args):
    try:
        f = open(dotpath+'save/default',mode='wb')
    except FileNotFoundError:
        f = open(dotpath+'save/default',mode='ab')
        fast_print('warning: default savecase not found.New case has been set up')
        f.close()
        return
    pickle.dump(resmanager.SaveResourceDomain,f)
    f.close()


def reload():
    get_world().__init__('saveourvedal',get_world().window,get_world().surface,get_world().buffersurface)
    get_world().postinit()

class DebugRunable(Runable):
    def __init__(self):
        super().__init__()
        self.memview=None
        self.fpsview=None
        self.tickview=None
        self.versionview = yaheifont.render(VERSION_D,True,(120,188,188,255)).convert_alpha()
        self.process=psutil.Process(getpid())
        self.open_view = True
        self.change_stat()
    def update(self,tick,world):
        if self.lasttick+60<=tick:
            self.lasttick=tick
            self.change_stat()
    def draw(self,bs):
        if self.open_view:
            bs.blit(self.memview,(2,2))
            bs.blit(self.fpsview,(2,22))
            bs.blit(self.tickview,(2,42))
            bs.blit(self.versionview,(2,62))
    def change_stat(self):
        self.memview = yaheifont.render('Memory: %s MB' % str(self.process.memory_full_info().uss/1024/1024),True,(120,168,134,255))
        self.fpsview = yaheifont.render('Fps: %s' % str(get_world().fps),True,(120,168,134,255))
        self.tickview = yaheifont.render('Ticks: %s' % self.lasttick,True,(120,168,134,255))
    def eventupdate(self,se):
        if se.type==PGKEY.KEYDOWN:
            if se.dict['unicode']=='`':
                mifr = MCO_target(MainInterfaceRunable)
                if 'debug' in mifr.framemanager.hide:
                    mifr.framemanager.show_control('debug')
                else:
                    mifr.framemanager.hide_control('debug')
            
            elif se.dict['key']==PGKEY.K_F1:
                self.open_view = not self.open_view
