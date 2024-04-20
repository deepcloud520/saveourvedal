from storyteller import *
import airiscore as airis
from airiscore import MyTrigger,MyTriggerPlus
import hiyoricore as hiyori
import time,os,pygame
from annycore import load_singlesound,load_mutlisound
import mnist,shutil


def create_puzzle(commands):
    source = os.environ['HOME']
    def pathlike(s):
        return resmanager.safe_pathlike(s.format(source=source,dotpath=dotpath))
    for line in commands:
        command = line[0]
        if command == 'mkdir':
            pathlike(line[1]).mkdir(parents=True,exist_ok=True)
            
        elif command == 'copy':
            try:
                shutil.copy(pathlike(line[1]),pathlike(line[2]))
            except shutil.SameFileError:
                print('SameFileError',pathlike(line[1]),pathlike(line[2]))
        elif command == 'copytree':
            try:
                shutil.copytree(pathlike(line[1]),pathlike(line[2]),dirs_exist_ok=True)
            except shutil.SameFileError:
                print('SameFileError',pathlike(line[1]),pathlike(line[2]))
        elif command == 'write_text':
            try:
                f=open(pathlike(line[1]),mode='w')
            except FileNotFoundError:
                f=open(pathlike(line[1]),mode='a')
            f.write(line[2])
            f.close()
        loclogger.debug('create_pizzle:',line[0],*[pathlike(line[i]) for i in range(1,len(line))])
    return source




class FileMonitor(Runable):
    def __init__(self,source_dir,runable:hiyori.StatImageRollRunable):
        super().__init__()
        self.source_dir=resmanager.safe_pathlike(source_dir)  / 'source_0' / 'puzzle' / 'screen00'
        self.exists = [self.source_dir / (str(i) + '.png') for i in range(3)]
        self.correct = False
        self.runable = runable
    def update(self,tick,master):
        if (not self.correct) and self.lasttick + 200 <= tick:
            if not any(map(lambda x:x.exists(),self.exists)):
                # 全部都没有了
                self.correct=True
                self.runable.reset_textures({'s':[1000,'s','texture.story0_cookie2']})


class FingerCheckRunnable(Runable):
    def __init__(self,canvas,info_label,passwd,trigger):
        super().__init__()
        self.info_label = info_label
        self.passwd = passwd
        self.trigger = trigger
        self.m = mnist.Mnist_twolayer(['mnist/dense_4-kernel0','mnist/dense_4-bias0','mnist/dense_5-kernel0','mnist/dense_5-bias0'])
        self.correct=False
        self.canvas = canvas
    def update(self,tick,master):
        if (not self.correct) and self.lasttick + 100 <= tick:
            passwd=''
            for canvas in self.canvas:
                number,confused=self.m.predict(canvas.image_array)
                passwd+=str(number) if confused>-3 else '-'
            self.info_label.change_text(text=passwd)
            if passwd == self.passwd:
                self.correct=True
                self.info_label.change_text(fontcolor=(120,230,120,220))
                get_world().eventrunner.trigger(self.trigger)
            self.lasttick = tick


class EntityFakeDoor(airis.EntityRealDoorLocked):
    def transport(self, living: EntityLiving):
        get_world().eventrunner.trigger('story0_quithome')
    def sync(self,onactive):
        #if not self.targetdoor:return
        self.onactive=onactive
        self.update_info()




def close_storybook():
    pass

def open_storybook(self):
    window = get_world().window
    dbf = self.framemanager.get_control('debate')
    STT = StoryTellerTrigger(resmanager.DefResourceDomain.get_resource('story'))

    def backto(eventrunner):
        dbf.clear_all()
        self.framemanager.hide_all()
        self.framemanager.show_control('bd')
        DefResourceDomain.get_resource('play_action')('resume')
    
    def exitgame(eventrunner):
        #删除存档：
        import os,time
        os.remove(dotpath+'save/default')
        get_world().__init__('saveourvedal',get_world().window,get_world().surface,get_world().buffersurface)
        get_world().postinit()
    
    def loadmusic(eventrunner,respath='music.bd'):
        print(resmanager.DefResourceDomain.get_resource(respath))
        DefResourceDomain.get_resource('play_action')('replace play_list',play_list=resmanager.DefResourceDomain.get_resource(respath))
        

    @add_trigger(MyTrigger,'finale')
    def story_finale(eventrunner):
        DefResourceDomain.get_resource('play_action')('stop')
        get_world().engine.clear_all()
        self.framemanager.hide_all()
        self.framemanager.show_control('debate')
        eventrunner.put_event(MyTrigger(exitgame,'nexttext'))
        for i in range(11,-1,-1):
            eventrunner.put_event(MyTrigger(PlayText(dbf,*resmanager.NameResourceDomain.get_resource('storyfinale.'+str(i))),'nexttext'))
    
    @add_trigger(MyTrigger,'_startgame')
    def story0_realgamestart(eventrunner):
        loadmusic(eventrunner)
        backto(eventrunner)
        eventrunner.trigger('NeuroSingDuvet')

    @add_trigger(MyTrigger,'story0_text')
    def story0_text(eventrunner):
        mp = MCO_target(resmanager.DefResourceDomain.get_resource('MusicCoreRunableType'))
        mp.play_action('stop')
        fast_print(STT.complete_story('ACT0')['name'],pos=point(20,window.y-80))
        fast_print('按任意健或点击鼠标继续')
        self.framemanager.hide_all()
        self.framemanager.show_control('debate')
        get_world().eventrunner.Runables[RING3].append(RollControlRunable(control=dbf,targetpos=point(window.x//2-DIALOG_WIDTH//2,0),startpos=dbf.pos,rolling=fast_to_slow,vel=0.04))
        eventrunner.put_event(MyTrigger(story0_realgamestart,'nexttext'))
        story=resmanager.NameResourceDomain.get_resource('story0.evilchatneuro')[::-1]
        for storyline in story:
            eventrunner.put_event(MyTrigger(PlayText(dbf,*storyline),'nexttext'))
        
        
    @add_trigger(MyTrigger,'story0_home')
    def story_home_loading(eventrunner):
        self.framemanager.hide_all()
        # 加载 rooms
        airis.clear_rooms()
        get_world().engine.clear_all()
        # 启动一大堆效果
        window = get_world().window

        ter2=EntityTerminal(point(window.x//2-200,window.y//2-100),point(5,22),point(window.x//2+130,window.y//2),title='V2TL (Channel #~2)',font=qingkongsmall,shape=point(35,15),defname='ter2',titlecolor=(98,75,28,250),showdeep=2,flags=TER_SWITCH_DRAWORDER)
        ter2.add_control(EntityStatImage(point(0,22),point(0,0),resmanager.DefResourceDomain.get_resource('texture.terminal.neurosamaai_1'),alpha=100))
        self.framemanager.add_control(ter2)
        self.framemanager.hide_control('ter2')
        eventrunner.Runables[RING2].append(TimerRunable(
            func=add_effects(
                (
                effect_title(
                    pos=point(2,window.y-60),
                    text=resmanager.NameResourceDomain.get_resource('welcome.title1'),
                    fontcolor=(255,250,250,255),
                    lasttime=50*1.6,
                    font=sounsobig),)
                             ),
                time=50*11))
        eventrunner.Runables[RING2].append(
            TimerRunable(
                func=add_runables(
                    (TheHeartofNeuroRunable(ter2,resmanager.NameResourceDomain.get_resource('story0.theheartofneuro.init'),resmanager.NameResourceDomain.get_resource('story0.theheartofneuro.init.delay'),destory='ter2'),)
                    ,RING1),
                time=50*9
                )
        )
        eventrunner.Runables[RING2].append(TimerRunable(
            func=add_effects(
                (
                effect_title(
                    pos=point(2,window.y-30),
                    text=resmanager.NameResourceDomain.get_resource('welcome.title4'),
                    fontcolor=(255,230,230,255),
                    lasttime=50*4,
                    font=qingkongsmall),)
                             ),
                time=50*15+20))
        eventrunner.Runables[RING2].append(TimerRunable(
            func=add_effects(
                (
                effect_title(
                    pos=point(2,window.y//2+200),
                    text=resmanager.NameResourceDomain.get_resource('welcome.title2'),
                    fontcolor=(255,230,230,255),
                    lasttime=50*3,
                    font=qingkongsmall),)
                             ),
                time=50*13))
        eventrunner.Runables[RING2].append(TimerRunable(
            func=add_effects(
                (
                effect_showline(
                    pos=point(2,window.y//2+233),
                    process=0,
                    text=resmanager.NameResourceDomain.get_resource('welcome.title3'),
                    fontcolor=(255,230,230,255),
                    roll_vel=0.02,
                    lasttime=50*2,
                    font=qingkongsmall),)
                             ),
                time=50*21))
        
        eventrunner.Runables[RING2].append(TimerRunable(
            func=story0_show_all_infomation,
                time=50*11))
            
    def story0_show_all_infomation(eventrunner):
        ter1=EntityTerminal(point(0,-22),point(5,22),window.copy()+point(0,22),title='terminal1',font=liberationmono,shape=point(100,32),defname='ter1')
        ter1.add_control(EntityStatImage(point(5,22),point(0,0),resmanager.DefResourceDomain.get_resource('texture.terminal.evilneuroai_2'),alpha=50))
        self.framemanager.add_control(ter1)
        self.framemanager.show_control('ter2')
        eventrunner.Runables[RING2].append(
            TimerRunable(
                func=add_runables(
                    (TerminalCore(ter1,resmanager.NameResourceDomain.get_resource('terminal.story0.evilloading'),destory='ter1'),)
                    ,RING1),
                time=0
                )
            )
        timetotal=sum(map(lambda x:x['delay'],resmanager.NameResourceDomain.get_resource('terminal.story0.evilloading')))
        eventrunner.Runables[RING2].append(
            TimerRunable(
                func=story0_home_awake,
                time=timetotal+40
                )
        )
            
        
            
    @add_trigger(MyTrigger,'debug')
    def story0_home_awake(eventrunner):
        # 生成通行pin
        password=['313','528']
        random.shuffle(password)
        ck_password = ''.join(password)
        resmanager.SaveResourceDomain.add_resource('password',ck_password)
        loclogger.debug('Test: password:',ck_password)
        # 加载房间
        airis.get_rooms().update(airis.makerooms(dotpath+'rooms/'+resmanager.DefResourceDomain.get_resource('rooms.story0')['resource'],extra_map={"EntityFakeDoor":EntityFakeDoor}))
        room=airis.get_rooms()[resmanager.DefResourceDomain.get_resource('rooms.story0')['start_room']]
        # 装载房间至引擎
        room.build(get_world().engine)
        # 初始化 Evil Neuro 控制器
        player = get_entity_bydefname(get_world().engine.livings_line,defname='evilneuroai')[0]
        acr = AirisCoreRunable(player)
        get_MCO().append(acr)
        eventrunner.Runables[RING0].append(acr)
        
        '''
        # 加载云
        eventrunner.Runables[RING2].append(
            hiyori.CloudRollRunable(
                resmanager.DefResourceDomain.get_resource('texture.r_cloud'),
                get_entity_bydefname(get_world().engine.images_line,defname='screen')[0]
                )
                )
        '''
        sirr=hiyori.StatImageRollRunable(
                {
                    "s":[100,"tarot1","texture.story0_cookie"],
                    "tarot1":[1350,"tarot2","texture.story0_15_tarot"],
                    "tarot2":[1350,"tarot3","texture.story0_16_tarot"],
                    "tarot3":[2350,"tarot4","texture.story0_17_tarot"],
                    "tarot4":[2850,"tarot1","texture.story0_18_tarot"]
                    },
                get_entity_bydefname(get_world().engine.images_line,defname='cookie')[0]
                )
        eventrunner.Runables[RING2].append(sirr)
        # mnist识别
        bottomcolor = resmanager.NameResourceDomain.get_resource('story0.livingroom.terminal.color')
        mnistframe = EntityFrame(point(window.x*0.05,window.y*0.2),point(window.x*0.9,window.y*0.6),bottomcolor,showdeep=-1,defname='mnistframe')
        info_label = EntityLabel(point(window.x*0.3,window.y*0.4),point(0,0),'',xiaoxiongverybig,(0,0,0,0),(250,250,250,250))
        detla = resmanager.DefResourceDomain.get_resource('texture.detla')
        canvas=[
            mnistframe.add_control(
                EntityCanvas(
                    point(window.x*0.45+(28*4+5)*i,window.y*0.2),point(0,0),point(28,28),4, 
                    rgbbase=pg.surfarray.array3d(detla.subsurface(pg.Rect(window.x*0.45+(28*4+5)*i,window.y*0.2,28*4,28*4))),rgbbottom = numpy.full((28*4,28*4,3),(80,70,67)), alpha=100)
                                                 ) for i in range(-3,3)]
        mnistframe.add_control(info_label)
        
        create_textlines(mnistframe,resmanager.NameResourceDomain.get_resource('story0.livingroom.terminal.top'),qingkongsmall,point(window.x*0.45,30),1,(0,0,0,0),(250,250,230,230),mode='centre')
        create_textlines(mnistframe,resmanager.NameResourceDomain.get_resource('story0.livingroom.terminal.bottom'),qingkongsmall,point(window.x*0.45,window.y*0.6-40),1,(0,0,0,0),(220,220,180,250),mode='centre')
        get_world().eventrunner.Runables[RING1].append(FingerCheckRunnable(canvas,info_label,'555555','unlockdoor'))
        # 创造puzzle文件夹
        get_world().eventrunner.Runables[RING1].append(FileMonitor(create_puzzle(resmanager.NameResourceDomain.get_resource('story0.bedroom.puzzle2.init')),sirr))
        get_world().eventrunner.add_trigger(OpenFrameTrigger('mnistframe',None,'mnistframe'))
        self.framemanager.add_control(mnistframe)
        self.framemanager.hide_all()
        
        
    @add_trigger(MyTrigger,'unlockdoor')
    def unlockdoor(eventrunner):
        # 查找假门
        streamroom=airis.get_rooms()['streamroom']
        door = get_entity_bydefname(streamroom.blockeds,'dreamhead')[0]
        door.unlock()
        if airis.get_nowroom()=='streamroom':
            info = resmanager.NameResourceDomain.get_resource('story0.unlockdoor')
        elif airis.get_nowroom()=='bedroom':
            info = resmanager.NameResourceDomain.get_resource('story0.unlockdoor_2')
        print_dialog(resmanager.NameResourceDomain.get_resource('name.talker.evil'),info)
        
    @add_trigger(MyTrigger,'NeuroSingDuvet')
    def NeuroSingDuvet(eventrunner):
        #在*开始游戏*开始播放
        loclogger.info(resmanager.DefResourceDomain.get_resource('music.bd'))
        mp = MCO_target(resmanager.DefResourceDomain.get_resource('MusicCoreRunableType'))
        mp.play_action('playnow name',name='mus_n_duvet')
        
    @add_trigger(MyTrigger,'story0_quithome')
    def story0_quithome(eventrunner):
        time.sleep(2.5)
        evilneuro=get_entity_bydefname(get_world().engine.livings_line,'evilneuroai')[0]
        get_world().engine.images_line=[]
        get_world().engine.livings_line=[evilneuro]
        get_world().eventrunner.Runables[RING1].append(
            TimerRunable(
                func=story0_quit_home_post,
                time=50*3.2
                )
            )
        if hasattr(evilneuro,'freeze'):evilneuro.freeze()
    @add_trigger(MyTrigger,'debug2')
    def story0_quit_home_post(eventrunner):
        #time.sleep(5.5)
        # story0_secprocess_init
        pygame.quit()
        os.system('python3 ' + 'main.py ' + '--trigger story0_secinit --startmode text')
        sys.exit()
    @add_trigger(MyTrigger,'story0_secinit')
    def story0_secinit(eventrunner):
        load_singlesound('music.story0_sec')
        self.framemanager.hide_all()
        # 播放背景音乐
        eventrunner.Runables[RING1].append(
            TimerRunable(
                func=story0_sec_stage1,
                time=50*5
                )
            )
        # 停止
        eventrunner.Runables[RING1].append(
            TimerRunable(
                func=story0_sec_stage2,
                time=50*(5+12)
                )
            )
        # 加载过场
        eventrunner.Runables[RING1].append(
            TimerRunable(
                func=story0_sec_stage3,
                time=50*(5+2)
                )
            )
        # 启动下一个阶段
        eventrunner.Runables[RING1].append(
            TimerRunable(
                func=story0_text,
                time=50*(5+12+3)
                )
            )
    def story0_sec_stage1(eventrunner):
        mp = MCO_target(resmanager.DefResourceDomain.get_resource('MusicCoreRunableType'))
        mp.play_action('replace play_list',play_list={'start':resmanager.DefResourceDomain.get_resource('realmusic.story0_sec')})
        mp.play_action('playnow name',name='start')
    def story0_sec_stage2(eventrunner):
        DefResourceDomain.get_resource('play_action')('stop')
        self.framemanager.hide_all()
    def story0_sec_stage3(eventrunner):
        ter1 = EntityTerminal(point(window.x*0.25,0)+point(30,50),point(5,22),window*0.5,title='~cat Internet',font=liberationmono,shape=point(100,32),defname='cats')
        ter2 = EntityTerminal(point(-100,window.y*0.05),point(0,0),window*0.9,title='~',font=liberationmono,shape=point(10,32),flags=TER_DONNOTDRAWPANCEL,defname='map')
        ter3 = EntityTerminal(point(0,0),point(0,0),point(window.x*0.4,window.y),title='~',font=liberationmono,shape=point(40,34),flags=TER_DONNOTDRAWPANCEL,defname='text')
        ter4 = EntityTerminal(point(window.x*0.5+100,window.y*0.7),point(5,22),point(186,172),title='figure 8',font=liberationmono,shape=point(10,34),defname='moon')
        textbg = EntityStatImage(point(0,0),point(0,0),resmanager.DefResourceDomain.get_resource('texture.terminal.evilneuroai_2').subsurface(pg.Rect(0,0,window.x*0.4,window.y)),alpha=120)
        cats = EntityStatImage(point(0,20),point(0,0),resmanager.DefResourceDomain.get_resource('texture.terminal.evilneuroai_2'),alpha=255)
        moon = EntityStatImage(point(0,20),point(0,0),resmanager.DefResourceDomain.get_resource('texture.story0.moon'),alpha=255)        
        ter1.add_control(cats)
        ter1.write('16Dfhh=pa1Yxe')
        ter3.add_control(textbg)
        ter4.add_control(moon)
        # 对白底黑子地图进行颜色反转，缩小，锐化
        image = resmanager.DefResourceDomain.get_resource('texture.story0.england_map').convert()
        image = pg.transform.scale(image,(get_world().window*0.9)._intlist())
        
        grey = 1-pg.surfarray.array3d(image).astype('int32').dot((0.3,0.59,0.11))/255
        grey[grey>=0.3] = 1
        grey[grey<0.3] = 0
        image = pg.surfarray.make_surface(grey*(2**8-1))
        image.set_colorkey((0,0,0))
        image.set_alpha(100)
        

        eventrunner.Runables[RING2].append(
            TimerRunable(
                func=add_runables(
                    (TerminalCore(ter3,resmanager.NameResourceDomain.get_resource('terminal.story0.evilfindneuro')),)
                    ,RING1),
                time=0
                )
            )

        resmanager.DefResourceDomain['texture.story0.england_map']=image
        resmanager.DefResourceDomain['texture.story0.cat1']=pg.transform.scale(resmanager.DefResourceDomain['texture.story0.cat1'],(get_world().window*0.5)._intlist())
        map = EntityStatImage(point(0,0),point(0,0),image,alpha=255)
        ter2.add_control(map)

        catsroll=hiyori.StatImageRollRunable(
                {
                    "s":[200,"2","texture.story0.cat1"],
                    "2":[210,"3","texture.story0.cat2"],
                    "3":[200,"s","texture.story0.cat3"]
                },
                cats
                )
        eventrunner.Runables[RING2].append(catsroll)
        self.framemanager.add_control(ter2)
        self.framemanager.add_control(ter1)
        self.framemanager.add_control(ter3)
        self.framemanager.add_control(ter4)
        