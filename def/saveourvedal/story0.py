from storyteller import *
import airiscore as airis
from airiscore import MyTrigger,MyTriggerPlus
import hiyoricore as hiyori
import time,multiprocessing,os,threading,pygame
from annycore import ALL,TRANS

def close_storybook():
    pass
def open_storybook(self):
    window = get_world().window
    dbf = self.framemanager.get_control('debate')
    STT = resmanager.DefResourceDomain.get_resource('story')

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
    
    def loadmusic(eventrunner):
        DefResourceDomain.get_resource('play_action')('replace play_list',play_list=resmanager.DefResourceDomain.get_resource('realmusic.bd'))
        

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
        fast_print(STT.complete_story('ACT0')['name'])
        fast_print('按任意健或点击鼠标继续')
        self.framemanager.hide_all()
        self.framemanager.show_control('debate')
        eventrunner.put_event(MyTrigger(story0_realgamestart,'nexttext'))
        for i in range(11,-1,-1):
            eventrunner.put_event(MyTrigger(PlayText(dbf,*resmanager.NameResourceDomain.get_resource('story0.'+str(i))),'nexttext'))
        
        
    @add_trigger(MyTrigger,'story0_home')
    def story_home_loading(eventrunner):
        self.framemanager.hide_all()
        # 加载 rooms
        airis.clear_rooms()
        get_world().engine.clear_all()
        # 启动一大堆效果
        window = get_world().window

        ter2=EntityTerminal(point(window.x//2-200,window.y//2-100),point(5,22),point(window.x//2+130,window.y//2),title='V2T',font=chinesefont1,shape=point(35,15),defname='ter2',titlecolor=(98,75,28,250),showdeep=2,flags=TER_SWITCH_DRAWORDER)
        ter2.add_control(EntityStatImage(point(0,22),point(0,0),resmanager.DefResourceDomain.get_resource('texture.terminal.neurosamaai_1'),alpha=150))
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
                    font=verybigfont1),)
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
                    font=chinesefont1),)
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
                    font=chinesefont1),)
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
                    font=chinesefont1),)
                             ),
                time=50*21))
        
        eventrunner.Runables[RING2].append(TimerRunable(
            func=story0_show_all_infomation,
                time=50*11))
            
    def story0_show_all_infomation(eventrunner):
        ter1=EntityTerminal(point(0,-22),point(5,22),window.copy()+point(0,22),title='terminal1',font=terminalfont1,shape=point(100,30),defname='ter1')
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
            
        ter1.add_control(EntityStatImage(point(5,22),point(0,0),resmanager.DefResourceDomain.get_resource('texture.terminal.evilneuroai_2'),alpha=50))
            
    @add_trigger(MyTrigger,'debug')
    def story0_home_awake(eventrunner):
        airis.get_rooms().update(airis.makerooms(dotpath+'rooms/'+resmanager.DefResourceDomain.get_resource('rooms.story0')['resource']))
        room=airis.get_rooms()[resmanager.DefResourceDomain.get_resource('rooms.story0')['start_room']]
        # 装载房间
        room.build(get_world().engine)
        # 初始化Evil Neuro 控制器
        player = get_entity_bydefname(get_world().engine.livings_line,defname='evilneuroai')[0]
        acr = AirisCoreRunable(player)
        get_MCO().append(acr)
        eventrunner.Runables[RING0].append(acr)
        self.framemanager.hide_all()
            
        eventrunner.Runables[RING2].append(
            hiyori.CloudRollRunable(
                resmanager.DefResourceDomain.get_resource('texture.r_cloud'),
                get_entity_bydefname(get_world().engine.images_line,defname='screen')[0]
                )
                )
            
        eventrunner.Runables[RING2].append(
            hiyori.StatImageRollRunable(
                {
                    "s":[100,"tarot1","texture.story0_cookie"],
                    "tarot1":[1350,"tarot2","texture.story0_15_tarot"],
                    "tarot2":[1350,"tarot3","texture.story0_16_tarot"],
                    "tarot3":[2350,"tarot4","texture.story0_17_tarot"],
                    "tarot4":[2850,"tarot1","texture.story0_18_tarot"]
                    },
                get_entity_bydefname(get_world().engine.images_line,defname='cookie')[0]
                )
                )
    @add_trigger(MyTrigger,'NeuroSingDuvet')
    def NeuroSingDuvet(eventrunner):
        #在所有最开始游戏开始播放
        MPT = resmanager.ConfigResourceDomain.get_resource('musicplaytype')
        musicplayertype = ALL[MPT]
        mp = get_world().eventrunner.get_runable(RING2, _class=musicplayertype)
        mp.play_action('playnow name',name=TRANS[MPT]('mus_n_duvet'))
        
    @add_trigger(MyTrigger,'story0_quithome')
    def story0_quithome(eventrunner):
        # evil的defname要改成evilneuroai
        time.sleep(2.5)
        evilneuro=get_entity_bydefname(get_world().engine.livings_line,'evilneuroai')[0]
        get_world().engine.images_line=[evilneuro]
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
        os.system('python3 ' + 'main.py ' + '--trigger debug --startmode text')
        sys.exit()
        