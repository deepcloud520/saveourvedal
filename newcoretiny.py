from tool import argstrans
from simplelogger import mainlogger
RING0=0
RING1=1
RING2=2
RING3=3


class Trigger:
    def __init__(self,func):
        self.func=func
    def run(self,event,world):
        '''(bool -> remove the trigger,bool -> break from the trigger for-each)'''
        return (False,False)


class ImmTrigger(Trigger):
    def run(self,key,world):
        self.func(world)
        return (True,True)


class Runable:
    def __init__(self):
        self.lasttick=0
    def update(self,tick,world):
        pass


class EventRunner:
    def __init__(self,name,master):
        self.triggers=[]
        self.master=master
        self.Runables={RING0:[],RING1:[],RING2:[],RING3:[]}
        self.lasttick=0
    def clear_triggers(self):self.triggers=[]
    def remove_runable(self,ring,_class):
        for instance in self.Runables[ring]:
            if isinstance(instance,_class):
                self.Runables[ring].remove(instance)
                return instance
    def get_runable(self,ring,_class):
        for instance in self.Runables[ring]:
            if isinstance(instance,_class):
                return instance
    def get_trigger(self,_class):
        for instance in self.triggers:
            if isinstance(instance,_class):
                return instance
    def update(self,tick):
        if self.lasttick+0<tick:
            temp_removed=[]
            for ring,runables in self.Runables.items():
                for runable in runables:
                    if runable.update(tick,self):
                        temp_removed.append((ring,runable))
            for ring,T in temp_removed:
                self.Runables[ring].remove(T)
            self.lasttick=tick
    def trigger(self,event):
        mainlogger.debug('Eventrunner trigger ',event)
        temp_removed=[]
        if self.triggers:
            for trigger in self.triggers[::-1]:
                result=argstrans(trigger.run(event,self),(False,False))
                if result[0]:
                    temp_removed.append(trigger)
                if result[1]:
                    break
        for T in temp_removed:
            self.triggers.remove(T)
    def put_event(self,event):
        self.triggers.append(event)
    def add_trigger(self,event):
        self.put_event(event)
    def get_master(self):return self.master
    def reverse(self):
        self.triggers.reverse()

'''
class PlayText(Runable):
    def __init__(self,talker,text,color=(100,100,200,250)):
        super().__init__()
        self.text=text
        self.talker=talker
        self.num=0
        self.color=color if color else (100,100,200,250)
    def update(self,tick,display):
        if self.lasttick==0:
            display.master.textdisplay.first_textcolor=self.color
            display.master.textdisplay.first_textbuffer=self.talker
            display.master.textdisplay.nextline()
        if self.num>=len(self.text):
            display.master.textdisplay.nextline()
            return True
        if self.lasttick+2<tick:
            display.master.textdisplay.first_textbuffer+=self.text[self.num]
            self.num+=1
            self.lasttick=tick

class PlayAction(Runable):
    def __init__(self,target,):
        super().__init__()
        self.text=text
        self.talker=talker
        self.num=0
    def update(self,tick,display):
        if self.lasttick==0:
            display.master.textdisplay.first_textcolor=self.color
            display.master.textdisplay.first_textbuffer=self.talker
            display.master.textdisplay.nextline()
        if self.num>=len(self.text):
            display.master.textdisplay.nextline()
            return True
        if self.lasttick+1<tick:
            display.master.textdisplay.first_textbuffer+=self.text[self.num]
            self.num+=1
            self.lasttick=tick

class Display:
    def __init__(self,name,pos,rect):
        self.name=name
        self.lasttick=0
        self.pos=pos
        self.rect=rect
    def draw(self,scr):
        pass
    def update(self,tick):
        pass

class DisplayManager:
    def __init__(self):
        
        self.displays=[]
        self.active_names=set()
    def add_display(self,d):
        self.displays.append(d)
    def draw(self):
        for d in self.displays:
            if d.name in self.active_names:
                d.draw()
    def update(self,tick):
        for d in self.displays:
            if d.name in self.active_names:
                d.update(tick)
    def show(self,name):
        self.active_names.add(name)
    def hide(self,name):
        self.active_names.pop(name)
    def hide_all(self):
        self.active_names=set()
    def get_display(self,name):
        for d in self.displays:
            if d.name==name:return d
class TextDisplay(Display):
    def __init__(self,name,pos,rect,auto=False,font=None):
        super().__init__(name,pos,rect)
        self.auto=auto
        self.triggers=[]
        self.texts=[]
        self.first_textbuffer=''
        self.font=font
        self.Runable=None
        self.textcolors=[]
        self.first_textcolor=(100,100,200,250)
    def update(self,tick):
        if self.lasttick+0<tick:
            if len(self.first_textbuffer)>=self.rect.x-1:
                self.nextline()
            self.lasttick=tick
    def nextline(self):
        self.texts.append(self.first_textbuffer)
        self.textcolors.append(self.first_textcolor)
        self.first_textbuffer=''
        self.first_textcolor=(100,100,200,250)

    def draw(self,scr):
        tempy=0
        windowwidth=self.rect.y-1
        atthigh=0 if len(self.texts)<windowwidth else len(self.texts)-windowwidth
        for text,color in zip(self.texts[atthigh:atthigh+windowwidth],self.textcolors[atthigh:atthigh+windowwidth]):
            printtext(text,self.font,point(0,tempy*16)+self.pos,scr,self.first_textcolor)
            tempy+=1
        printtext(self.first_textbuffer,self.font,point(0,tempy*16)+self.pos,scr,self.first_textcolor)
'''