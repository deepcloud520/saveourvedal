'''
    音频管理
    
    先草pygame.mixer（惩罚），然后草concurrent.futures（奖励）
    
'''

import concurrent.futures
import resmanager
from local import *
import os,logging,random,shutil,time,pathlib
from newcoretiny import Runable
import pygame as pg
from tool import dividelst


_DEBUG_CONTINUE_RECORD=True
MAX_WORKERS=1


pg.mixer.init(frequency=44100,buffer=65536)


def start_record(lst):
    for file in lst:
        try:
            file_path = file
            
            if _DEBUG_CONTINUE_RECORD and os.path.exists(trans_wav(file_path)):
                print('continue:',file_path)
                continue
            print('handling:',file_path)
            data, samplerate = sf.read(trans_ogg(file_path))
            sf.write(trans_wav(file_path), data, samplerate,format='wav')
        except Exception as e:
            print(e)



def start_mulitprocess(max_workers=2):
    handlelst=[resmanager.DefResourceDomain.get_resource("music.entiy"),resmanager.DefResourceDomain.get_resource("music.saveload"),resmanager.DefResourceDomain.get_resource("music.story0_sec")] + list(resmanager.DefResourceDomain.get_resource("music.bd").values())
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        div=len(handlelst)//max_workers
        workers=[]
        for content in dividelst(handlelst,div):
            workers.append(executor.submit(start_record,content))
        for i,w in enumerate(workers):
            get_loadprocesser()(resmanager.NameResourceDomain.get_resource('info.transogg_2').format(worker_info=i),tick=0)
            w.result()



# 用pygame.mixer播放NeuroV3的歌曲明显变慢,还有其他问题，所以我用simpleaudio播放wav
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
    def eventupdate(self,se):
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
    def draw(self,bs):
        pass

class MusicCoreRunable_Simpleaudio(MusicCoreRunable_Base):
    def __init__(self):
        super().__init__()
        #self.play_list=tuple(map(lambda x:AudioSegment(x),DefResourceDomain.get_resource('musiclist')))
        self.process=None
        self.allow_next=True
        start_time = time.time()
        get_loadprocesser()(resmanager.NameResourceDomain.get_resource('info.transogg').replace('[max_workers]',str(MAX_WORKERS)),tick=0)
        start_mulitprocess(max_workers=MAX_WORKERS)
    def _play(self,source):
        self._stop()
        if isinstance(source,str):
            source = SA.WaveObject.from_wave_file(trans_wav(source))
        self.process = source.play()
        self.timer = get_duringtick(source) + self.detla*(12+random.random()*12)
        return True
    def _stop(self):
        if self.process:
            self.process.stop()
    def get_musictype(self):
        return lambda x:SA.WaveObject.from_wave_file(trans_wav(x))



class MusicCoreRunable_Pygame_Mixer(MusicCoreRunable_Base):
    def __init__(self):
        super().__init__()
        self.channel=pg.mixer.find_channel(True)
        pg.mixer.music.set_endevent(pg.locals.USEREVENT)
        self.active=True
    def eventhandle(self,event):
        if event.type==pg.locals.USEREVENT and self.active:
            # 启动计时器
            self.timer=self.detla*(0.5+random.random())
            self.allow_next=True
    def _play(self,source):
        self._stop()
        loclogger.error(source)
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

soundpath=dotpath+'resource/sound/'

def load_singlesound(respath:str):
    '''加载单首歌，转换至”real“+respath上'''
    mcr = MCO_target(resmanager.DefResourceDomain.get_resource('MusicCoreRunableType'))
    dtype=mcr.get_musictype()
    loclogger.debug(f'dtype:{dtype} {soundpath+resmanager.DefResourceDomain.get_resource(respath)}')
    resmanager.DefResourceDomain.add_resource('real'+respath,dtype(resmanager.DefResourceDomain.get_resource(respath)))
def load_mutlisound(respath:str):
    mcr = MCO_target(resmanager.DefResourceDomain.get_resource('MusicCoreRunableType'))
    dtype=mcr.get_musictype()
    loclogger.debug(f'dtype:{dtype} {resmanager.DefResourceDomain.get_resource(respath)}')
    resmanager.DefResourceDomain.add_resource('real'+respath,list(map(lambda x:x,resmanager.DefResourceDomain.get_resource(respath))))

def trans_wav(source):
    return get_mainname(source)+'.wav'
def trans_ogg(source):
    return get_mainname(source)+'.ogg'
def get_mainname(source):
    return ''.join(source.split('.')[:-1])

def check_modules(mutype):
    if mutype=='Simpleaudio':
        if not sf:
            raise ModuleNotFoundError(resmanager.NameResourceDomain.get_resource('error.needmodule').replace('[module]','pysoundfile(import soundfile as sf)'))
        if not SA:
            raise ModuleNotFoundError(resmanager.NameResourceDomain.get_resource('error.needmodule').replace('[module]','Simpleaudio(import Simpleaudio as SA)'))
    if not numpy:
        raise ModuleNotFoundError(resmanager.NameResourceDomain.get_resource('error.needmoudle').replace('[moudle]','numpy(import numpy)'))
    if not psutil:
        raise ModuleNotFoundError(resmanager.NameResourceDomain.get_resource('error.needmoudle').replace('[moudle]','psutil(import psutil)'))


ALL={'Pygame_Mixer':MusicCoreRunable_Pygame_Mixer,'Simpleaudio':MusicCoreRunable_Simpleaudio,'Base':MusicCoreRunable_Base}
TRANS={'Pygame_Mixer':trans_ogg,'Simpleaudio':trans_wav,'Base':trans_wav}