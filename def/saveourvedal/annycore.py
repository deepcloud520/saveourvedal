'''
    音频管理
    
    先草pygame.mixer（惩罚），然后草concurrent.futures（奖励）
    
'''

import concurrent.futures
import resmanager
from local import *
import os,logging,random
from newcoretiny import Runable
import pygame as pg
from tool import dividelst

soundpath='resource/sound/'

_DEBUG_CONTINUE_RECORD=True

pg.mixer.init(frequency=44100,buffer=4096)



def start_record(lst):
    for file in lst:
        try:
            file_path = dotpath+soundpath+file
            
            if _DEBUG_CONTINUE_RECORD and os.path.exists(file_path):
                print('continue:',file_path)
                continue
        
            mainname=file.split('.')[0]
            print('handling:',file_path)
            data, samplerate = sf.read(dotpath+soundpath+mainname+'.ogg')
            sf.write(dotpath+soundpath+mainname+'.wav', data, samplerate,format='wav')
        except Exception as e:
            print(e)



def start_mulitprocess(max_workers=2):
    handlelst=[resmanager.DefResourceDomain.get_resource("music.entiy"),resmanager.DefResourceDomain.get_resource("music.saveload")] + resmanager.DefResourceDomain.get_resource("music.bd")
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        div=len(handlelst)//max_workers
        workers=[]
        for content in dividelst(handlelst,div):
            workers.append(executor.submit(start_record,content))
        for w in workers:
            w.result()



# 用pygame.mixer播放NeuroV3的歌曲明显变慢,还有其他问题，比如播放AliceInCradle的Saveorload有杂音，所以我用simpleaudio播放wav
def get_duringtick(source):
    return int(len(source.audio_data)/(source.bytes_per_sample*source.num_channels*source.sample_rate)*50)
class MusicCoreRunable_Base(Runable):
    def __init__(self):
        super().__init__()
        #self.play_list=tuple(map(lambda x:AudioSegment(x),DefResourceDomain.get_resource('musiclist')))
        self.play_list = dict()
        self.detla = 10*50
        self.timer = self.detla
        #self.play_num = 0
        self.allow_next=True
    def update(self, tick, world):
        if self.lasttick+self.timer<=tick and self.play_list and self.allow_next:
            self._play(
                source=self.play_list[random.choice(tuple(self.play_list.keys()))]
                )
            #self.play_num = (self.play_num + 1) % len(self.play_list)
            self.lasttick=tick
            #if self.play_num==0:
            #    random.shuffle(self.play_list)
    def eventupdate(se):
        pass
    def _play(self,source):
        pass
    def _stop(self):
        pass
    def get_musictype(self):
        def null(*args,**kwargs):
            return None
        return null
    def play_action(self,action='stop',**kwargs):
        if action=='stop':
            self._stop()
            self.allow_next=False
        elif action=='resume':
            self.allow_next=True
            self.timer=100
        elif action=='replace play_list':
            #random.shuffle(self.play_list)
            self.play_list = dict(kwargs['play_list'])
        elif action=='replace detla':
            self.detla = kwargs['detla']
        elif action=='playnow source':
            self._play(source=kwargs['source'])
        elif action=='get musictype':
            return self.get_musictype()
        elif action=='playnow name':
            return self._play(self.play_list[kwargs['name']])



class MusicCoreRunable_Simplesudio(MusicCoreRunable_Base):
    def __init__(self):
        super().__init__()
        #self.play_list=tuple(map(lambda x:AudioSegment(x),DefResourceDomain.get_resource('musiclist')))
        self.process=None
        self.allow_next=True

    def _play(self,source):
        self._stop()
        if isinstance(source,str):
            source = SA.WaveObject.from_wave_file(source)
        self.process = source.play()
        self.timer = get_duringtick(source) + self.detla*(12+random.random()*12)
        return True
    def _stop(self):
        if self.process:
            self.process.stop()
    def get_musictype(self):
        return SA.WaveObject.from_wave_file



class MusicCoreRunable_Pygame_Mixer(MusicCoreRunable_Base):
    def __init__(self):
        super().__init__()
        self.channel=pg.mixer.find_channel(True)
        pg.mixer.music.set_endevent(pg.locals.USEREVENT)
        self.active=True
    def eventhandle(self,event):
        if event.type==USEREVENT and self.active:
            # 启动计时器
            self.timer=self.detla*(0.5+random.random())
            self.allow_next=True
    def _play(self,source):
        self._stop()
        if isinstance(source,str):
            pg.mixer.music.load(source)
            pg.mixer.music.play()
            self.allow_next=False
        else:
            self.channel.play(source)
    def _stop(self):
        self.allow_next=False
        self.channel.fadeout(4500)
        pg.mixer.music.stop()
    def get_musictype(self):
        return pg.mixer.Sound





def trans_wav(source):
    return source+'.wav'
def trans_ogg(source):
    return source+'.ogg'
def check_modules(mutype):
    if mutype=='Simpleaudio':
        if not sf:
            raise ModuleNotFoundError(resmanager.NameResourceDomain.get_resource('error.needmodule').replace('[module]','pysoundfile(import soundfile)'))
        if not SA:
            raise ModuleNotFoundError(resmanager.NameResourceDomain.get_resource('error.needmodule').replace('[module]','Simpleaudio(import Simpleaudio as SA)'))
    if not numpy:
        raise ModuleNotFoundError(resmanager.NameResourceDomain.get_resource('error.needmoudle').replace('[moudle]','numpy(import numpy)'))


ALL={'Pygame_Mixer':MusicCoreRunable_Pygame_Mixer,'Simpleaudio':MusicCoreRunable_Simplesudio,'Base':MusicCoreRunable_Base}
TRANS={'Pygame_Mixer':trans_wav,'Simpleaudio':trans_wav,'Base':trans_wav}