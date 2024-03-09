import sys
sys.path.append(sys.path[0] + '/def/saveourvedal')
from worldcore import *
from tool import *
from local import *
import pygame as pg
import pygame.locals as PGKEY
import resmanager,copy,functools,code
from itertools import chain
import traceback as tb


'''
def loadjson(file):
    f = open(dotpath + file,encoding='utf-8')
    load = json.load(f)
    f.close()
    return load

'''
'''
可是没人爱我
'''
sys._stdout = sys.stdout
sys._stderr = sys.stderr

normalfont = pg.font.Font('yahei.ttf', 15)
chinesefont1 = pg.font.Font('qingkongwan.ttf',19)
chinesefont2 =  pg.font.Font('xiaoxiong.ttf',19)
smallchinesefont1 = pg.font.Font('qingkongwan.ttf',15)
bigchinesefont1 = pg.font.Font('qingkongwan.ttf',24)
bigchinesefont2 = pg.font.Font('xiaoxiong.ttf',24)
normalfont3 = pg.font.Font('yahei.ttf', 20)
normalfont2 = pg.font.Font('yahei.ttf', 21)
verybigfont1 = pg.font.Font('Sounso-Undividedad.ttf', 32)
terminalfont1 = pg.font.Font('Liberation Mono.ttf',16)

led1 = pg.font.Font('Digital-Play-St-3.ttf', 40)


for f,name in zip((normalfont,chinesefont1,chinesefont2,normalfont2,normalfont3,bigchinesefont1,led1,verybigfont1,terminalfont1),
                  ('normalfont','chinesefont1','chinesefont2','normalfont2','normalfont3','bigchinesefont1','led1','verybigfont1','terminalfont1')):
    resmanager.DefResourceDomain.add_resource('font.'+name,f)

class effect():
    def __init__(self,pos):
        self.image=None
        self.lasttick=0
        self.alive=True
        self.pos=pos
    def draw(self,scr):
        scr.blit(self.image,self.pos._intlist())
    def set_dead(self):
        self.alive=False

class effect_title(effect):
    def __init__(self,pos,text,fontcolor,lasttime=100,font=None):
        super().__init__(pos)
        self.image = font.render(text, True, fontcolor).convert_alpha()
        self.lasttime=lasttime
    def update(self,tick):
        if self.lasttime > 0:
            self.lasttime-=1
        else:
            return True



class effect_print(effect_title):
    def __init__(self,pos,text,fontcolor,fall_time=20,lasttime=100,font=None):
        super().__init__(pos=pos,text=text,fontcolor=fontcolor,lasttime=lasttime,font=font)
        self.fall_time=fall_time
    def update(self,tick):
        if self.fall_time > 0:
            self.fall_time -= 1
            self.pos.y += 2
        else:
            if self.lasttime > 0:
                self.lasttime -= 1
            else:
                self.set_dead()
                return True

class effect_roll(effect):
    def __init__(self,pos:point,text:str,fontcolor:tuple,font=None,fall_vel=0.05,fall_conv=float,bias=point(0,30)):
        super().__init__(pos=pos)
        self.stat = 0
        self.text = text
        self.bias = bias
        self.fall_vel = fall_vel
        self.fall_conv = fall_conv
        self.process = 1
        self.set_image(text,fontcolor,font)
    def set_dead(self):
        self.stat=2
    def set_image(self,text,fontcolor,font):
        self.image = font.render(text, True, fontcolor).convert_alpha()
        self.text=text
    def update(self,tick):
        if self.stat==0:
            if self.process<=0:
                self.stat=1
            self.process -= self.fall_vel
        elif self.stat==2:
            if self.process>=1:
                self.set_dead()
                return True
            self.process += self.fall_vel
            
    def draw(self,scr):
        scr.blit(self.image,(self.pos+self.bias*self.fall_conv(self.process))._intlist())


class effect_showline(effect):
    def __init__(self,pos,text,fontcolor,font=None,roll_vel=0.02,start_pos=0,lasttime=50,process=0):
        super().__init__(pos=pos)
        self.text=text
        self.fontcolor=fontcolor
        self.font=font
        self.roll_vel = roll_vel
        self.process = process
        self.lasttime=lasttime
        self.start_pos=start_pos
    def update(self,tick):
        if self.process<=1:
            self.image=self.font.render(self.text[:self.start_pos] + self.text[self.start_pos:int((len(self.text)-self.start_pos)*self.process)+ self.start_pos], True, self.fontcolor).convert_alpha()
            self.process+=self.roll_vel
        else:
            if self.process != 2:
                self.process=2
                self.image = self.font.render(self.text, True, self.fontcolor).convert_alpha()
                self.lasttick=tick
            if self.lasttick+self.lasttime <tick:
                self.set_dead()
                return True
class effect_showline_stand(effect_showline):
    def draw(self,scr):
        scr.blit(self.image,(self.pos-point(self.image.get_size()[0]/2,0))._intlist())
        
def fast_print(info,pos=None,fontcolor=(180,255,220,200),font=resmanager.DefResourceDomain.get_resource('font.bigchinesefont1')):
    if not pos:
        window = get_world().window
        pos = point(window.x*0.4,window.y*0.05)
    get_world().effects.append(effect_print(pos,info,fontcolor,font=font))

def print_dialog(talkname:str,content:list):
    window = get_world().window
    effect = effect_showline_stand(
                        pos=point(window.x*0.5,window.y*0.9-10),
                        text=('[%s]:' % talkname)+''.join(content),
                        fontcolor=(255,235,245,255),
                        roll_vel=0.03,
                        lasttime=len(''.join(content))*3+40,
                        font=resmanager.DefResourceDomain.get_resource('font.bigchinesefont1'),
                        start_pos=len(talkname)+3
                        )
    get_world().effects.append(effect)
    return effect

class EntityButton(Entity):
    def __init__(self, pos, boxpos, boxrect, text, font, bottomcolor, fontcolor, definedfunction, deep=0, defname=None,
                 showdeep=0):
        # boxpos一般取pos对吧
        super().__init__(pos, boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.active = False
        self.definedfunction = definedfunction
        # 预先绘制图像以提高性能
        self.surface = pg.Surface(point2tuple(self.hitbox.rect)).convert_alpha()
        self.surface.fill(bottomcolor)
        printtext(text, font, point(self.hitbox.rect.x // len(text) - 4, self.hitbox.rect.y // 2 - 6), self.surface,
                  fontcolor)
        self.press = pg.Surface(point2tuple(self.hitbox.rect)).convert_alpha()
        self.press.fill(fontcolor)
        printtext(text, font, point(self.hitbox.rect.x // len(text) - 4, self.hitbox.rect.y // 2 - 6), self.press,
                  bottomcolor)

        self.image = self.surface

    def eventupdate(self, evt, bias):
        # 超我之前写的代码

        if evt.type in (PGKEY.MOUSEBUTTONDOWN, PGKEY.MOUSEMOTION) and pointin(tuple2point(evt.dict['pos']),
                                                                              self.get_hitbox_pos() - bias,
                                                                              self.hitbox.rect):
            if evt.type == PGKEY.MOUSEBUTTONDOWN and self.active:

                self.active = False
                self.image = self.surface
                if self.defname:
                    self.definedfunction(self.defname)
                else:
                    self.definedfunction()
            elif (evt.type == PGKEY.MOUSEMOTION):
                self.active = True
                self.image = self.press
        else:
            self.active = False
            self.image = self.surface




class EntityButtonImmerse(Entity):
    def __init__(self, pos, boxpos, boxrect, text, font, bottomcolor, fontcolor, definedfunction, press_speed=0.05,deep=0, defname=None,fill_bottom=True,showdeep=0):
        # boxpos一般取pos对吧
        super().__init__(pos, boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.definedfunction = definedfunction

        self.surface = pg.Surface(point2tuple(self.hitbox.rect)).convert_alpha()
        if fill_bottom:self.surface.fill((0,0,0,0))
        pg.draw.rect(self.surface,bottomcolor,(0,0,*point2tuple(self.hitbox.rect)),5)
        printtext(text, font, point(self.hitbox.rect.x // len(text) - 4, self.hitbox.rect.y // 2 - 6), self.surface,
                  fontcolor)

        self.image = self.surface
        self.press = 0.0
        self.active = True
        self.press_speed = press_speed
        self.fontcolor=fontcolor
    def eventupdate(self, evt, bias):
        pass
    def draw(self,scr,bias):
        # 因为害怕性能问题，没准备根据tick运行的update，只好在draw里更新了QAQ 
        super().draw(scr,bias)
        # 超我之前写的代码
        if pg.mouse.get_pressed()[0] and pointin(tuple2point(pg.mouse.get_pos()),self.get_hitbox_pos() - bias,self.hitbox.rect):
            self.press+=self.press_speed
            if self.press>=1:
                if self.defname:
                    self.definedfunction(self.defname)
                else:
                    self.definedfunction()
                self.press=0
        else:
            self.press=0
        if self.press>0:
            pg.draw.rect(scr,self.fontcolor,
                     (*point2tuple(self.get_hitbox_pos() - bias),self.press*self.hitbox.rect.x,self.hitbox.rect.y),0)




class EntitySwitch(Entity):
    def __init__(self, pos, boxpos, boxrect, font, bottomcolor, fontcolor, stateenum, deep=0, defname=None,
                 showdeep=0):
        # boxpos一般取pos对吧
        super().__init__(pos, boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.active = False
        self.stateenum = stateenum
        self.statenum = -1
        # 预先绘制图像以提高性能
        self.bottomcolor = bottomcolor
        self.font = font
        self.fontcolor = fontcolor
        self.next_state()
        self.image = self.surface
        

    def next_state(self):
        self.statenum = (self.statenum+1) % len(self.stateenum)
        # Reset Image
        text = self.stateenum[self.statenum]
        self.surface = pg.Surface(point2tuple(self.hitbox.rect)).convert_alpha()
        self.surface.fill(self.bottomcolor)
        printtext(text, self.font, point(self.hitbox.rect.x // len(text) - 4, self.hitbox.rect.y // 2 - 6), self.surface,
                  self.fontcolor)
        self.press = pg.Surface(point2tuple(self.hitbox.rect)).convert_alpha()
        self.press.fill(self.fontcolor)
        printtext(text, self.font, point(self.hitbox.rect.x // len(text) - 4, self.hitbox.rect.y // 2 - 6), self.press,
                  self.bottomcolor)
    def eventupdate(self, evt, bias):
        # 超我之前写的代码
        if evt.type in (PGKEY.MOUSEBUTTONDOWN, PGKEY.MOUSEMOTION) and pointin(tuple2point(evt.dict['pos']),
                                                                              self.get_hitbox_pos() - bias,
                                                                              self.hitbox.rect):
            if evt.type == PGKEY.MOUSEBUTTONDOWN and self.active:

                self.active = False
                self.image = self.surface
                self.next_state()
            elif (evt.type == PGKEY.MOUSEMOTION):
                self.active = True
                self.image = self.press
        else:
            self.active = False
            self.image = self.surface



class EntityLabel(Entity):
    def __init__(self, pos, boxpos, text, font, bottomcolor, fontcolor, deep=0, defname=None, showdeep=0):
        super().__init__(pos, boxpos, boxrect=point(0, 0), deep=deep, defname=defname, showdeep=showdeep)
        self.hitbox.rect = tuple2point(self.change_text(text, font, bottomcolor, fontcolor).get_size())

    def change_text(self, text, font, bottomcolor, fontcolor):
        image = font.render(text, True, fontcolor).convert_alpha()
        self.image = pg.Surface(image.get_size()).convert_alpha()
        self.image.fill(bottomcolor)
        self.image.blit(image, (0, 0))
        return self.image

    def eventupdate(self, evt, bias):
        pass



class EntityStatImage(Entity):
    def __init__(self, pos, boxpos, image, alpha=255, deep=0, defname=None, showdeep=0):
        super().__init__(pos, boxpos, boxrect=point(0, 0), deep=deep, defname=defname, showdeep=showdeep)
        self.change_image(image,alpha)
    def change_image(self,image,alpha=255):
        if alpha != 255:
            self.image = image.convert()
            self.image.set_alpha(alpha)
        else:
            self.image=image
        self.hitbox.rect=tuple2point(self.image.get_size())
    def eventupdate(self,se,bias):
        pass



class EntityTextEditer(Entity):
    def __init__(self, pos, boxpos, boxrect, font, bottomcolor, fontcolor, deep=0, defname=None, showdeep=0):
        super().__init__(pos, boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.active=False
        self.font=font
        self.image = pg.Surface(point2tuple(boxrect)).convert_alpha()
        self.image.fill(bottomcolor)
        pg.draw.rect(self.image,fontcolor,(0,0,*point2tuple(self.hitbox.rect)),3)
        self.fontcolor=fontcolor
        self.text=''
        self.change_text()
    def eventupdate(self,evt,bias):
        if evt.type ==PGKEY.MOUSEBUTTONDOWN and pointin(tuple2point(evt.dict['pos']),
                                                                              self.get_hitbox_pos() - bias,
                                                                              self.hitbox.rect):
            if self.active:
                self.active = False
                self.change_text()
            else:
                self.active = True
                self.change_text()
        elif self.active and evt.type in (PGKEY.KEYDOWN,PGKEY.KEYUP):
            if evt.type==PGKEY.KEYDOWN:
                if evt.dict['key']!=PGKEY.K_BACKSPACE:
                    self.text+=evt.dict['unicode']
                else:
                    self.text=self.text[:-1]
                self.change_text()
    def change_text(self):
        self.textimage=self.font.render((self.text if not self.active else self.text+'_'), True, self.fontcolor).convert_alpha()
    def draw(self,scr,bias):
        super().draw(scr,bias)
        scr.blit(self.textimage,point2tuple(self.get_hitbox_pos() - bias+point(3,3)))
        


class EntityFrame(Entity):
    def __init__(self, pos, boxrect, bottomcolor=(20, 40, 50, 50), deep=0, defname='', showdeep=0):
        super().__init__(pos, boxpos=point(0, 0), boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        # sid -> frame id
        self.controllst = []
        self.bottomgcolor = bottomcolor
        self.surface = pg.Surface(point2tuple(boxrect)).convert_alpha()
        self.surface.fill(bottomcolor)

    def draw(self, scr, bias):
        scr.blit(self.surface, point2tuple((self.get_hitbox_pos() - bias)))
        for c in self.controllst:
            c.draw(scr, bias)

    def add_control(self, lastcontrol):
        lastcontrol.pos += self.pos
        self.controllst.append(lastcontrol)
        return lastcontrol

    def eventupdate(self, evt, bias):
        mousepos = pg.mouse.get_pos()
        if pointin(tuple2point(mousepos), self.get_hitbox_pos(), self.hitbox.rect):
        #if True:
            for c in self.controllst:
                c.eventupdate(evt, bias)

    def get_control(self, defname):
        for c in self.controllst:
            if c.defname == defname: return c
    def remove_control(self, defname):
        for c in self.controllst:
            if c.defname == defname:
                self.controllst.remove(c)
                return c
    def update(self,tick):
        super().update(tick)
        #for c in self.controllst:
        #    c.update(tick)



def middle_label_mirror(object_,pos,rect):
    # (partname,resname)
    return EntityLabel(pos,
                        point(0, 0),
                        object_[0], normalfont,
                        (10, 10, 10, 50),(141, 193, 178, 250),
                        deep=0, defname=object_[1], showdeep=0)
def left_button_mirror(object_,pos,rect):
    # (partname,resname,func)
    return EntityButton(pos,
                        point(0, 0), point(rect.x-10,22),
                        object_[0], normalfont,
                        (10, 10, 10, 50),(141, 193, 178, 250), definedfunction=object_[2],
                        deep=0, defname=object_[1], showdeep=0)

def launch_button_mirror(object_,pos,rect):
    # (partname,resname,func)
    return EntityButton(pos,
                        point(0, 0), point(rect.x-10,22),
                        object_[0], normalfont,
                        (160,167,188,30),(250, 250, 250, 100), definedfunction=object_[2],
                        deep=0, defname=object_[1], showdeep=0)
TABLE_WIDTH=10




class EntityTable(EntityFrame):
    def __init__(self, pos, boxrect, mirror, bottomcolor=(20, 40, 50, 50), deep=0, defname='', showdeep=0):
        super().__init__(pos=pos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.bias = point(0,0)
        self.table = []
        self.def_mirror = mirror
        self.next_pos = point(1,2)
        pg.draw.rect(self.surface,bottomcolor,(0,0,*point2tuple(self.hitbox.rect)),4)
    def list_append(self,object_):
        self.table.append(object_)
        ret = self.def_mirror(object_, self.next_pos, self.hitbox.rect)
        self.next_pos.y += (ret.hitbox.rect.y + TABLE_WIDTH)
        self.add_control(ret)
    def list_pop(self,num):
        try:
            self.table.pop(num)
        except IndexError:
            fast_print('已经没有东西了！')
            return
        self.next_pos.y -= (self.controllst.pop(num).hitbox.rect.y + TABLE_WIDTH)
    def list_clear(self):
        self.table = []
        self.controllst = []
        self.next_pos=point(1,2)


DIALOG_WIDTH = 400
def PlayText(debateframe,talker,text,titlefont,textfont,toward):
    def warp(eventrunner):
        add_dialog(debateframe,talker,text,titlefont,textfont,toward)
    return warp
def add_dialog(debateframe,talker,text,titlefont,textfont,toward):
    debateframe.add_control(EntityDialog(debateframe.next_pos,point(DIALOG_WIDTH,100),talker,text,
                                                     resmanager.DefResourceDomain.get_resource(titlefont),resmanager.DefResourceDomain.get_resource(textfont),toward))
    debateframe.next_pos.y+=110


class EntityFrameDebate(EntityFrame):
    def __init__(self, pos, boxrect, bottomcolor=(20, 40, 50, 50), deep=0, defname='', showdeep=0):
        super().__init__(pos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.bias=point(0,0)
        self.bias_target=point(0,boxrect.y*0.8)
        self.next_pos=copy.copy(self.bias_target)
        self.dialog_capacity=boxrect.y//100-1
        self.lasttick=0
        self.left_stall=None
        self.right_stall=None
    def eventupdate(self,se,bias):
        super().eventupdate(se,bias+self.bias)
        if (se.type==PGKEY.MOUSEBUTTONDOWN or se.type==PGKEY.KEYDOWN) and pointin(tuple2point(pg.mouse.get_pos()) - bias, self.get_hitbox_pos(), self.hitbox.rect):
            #下一条
            get_world().eventrunner.trigger('nexttext')
            
    def draw(self,scr,bias):
        scr.blit(self.surface, point2tuple(self.get_hitbox_pos() - bias))
        for c in self.controllst:
            c.draw(scr, bias + self.bias)
        if self.left_stall:scr.blit(self.left_stall,(0,380))
        if self.right_stall:scr.blit(self.right_stall,(600,400))
    def update(self,tick):
        if len(self.controllst) > 0 :
            bias = self.controllst[-1].pos - self.bias_target - self.bias
            speed = 25
            self.bias.y = (self.bias.y+speed if bias.y>=speed else self.bias.y+bias.y)
            if len(self.controllst) >= self.dialog_capacity +1:
                self.controllst.pop(0)
    def add_control(self,ct):
        super().add_control(ct)
        if isinstance(ct,EntityDialog):
            if ct.toward==TOWARDRIGHT:
                self.left_stall=resmanager.DefResourceDomain.get_resource('texture.stall.'+ct.talker)
            elif ct.toward==TOWARDLEFT:
                self.right_stall=resmanager.DefResourceDomain.get_resource('texture.stall.'+ct.talker)
                
    def clear_all(self):
        self.controllst=[]
        self.bias=point(0,0)
        self.next_pos=point(0,0)



# text -> tuple
TOWARDLEFT=1
TOWARDRIGHT=0
class EntityDialog(Entity):
    def __init__(self, pos,boxrect,talker, text, titlefont=normalfont3,textfont=chinesefont1,toward=TOWARDRIGHT,deep=0, defname='', showdeep=0):
        super().__init__(pos, boxpos=point(0, 0), boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.talker = talker
        self.text = text
        self.talkname = resmanager.NameResourceDomain.get_resource('name.talker.'+talker)
        bottomcolor = resmanager.DefResourceDomain.get_resource('color.talker.'+talker)
        talkerhead = resmanager.DefResourceDomain.get_resource('texture.talker.'+talker)
        self.surface=pg.Surface(point2tuple(boxrect)).convert_alpha()
        
        self.surface.fill(bottomcolor)
        # normal: 100*100
        # normal: 100*600
        if toward==TOWARDRIGHT:
            self.surface.blit(titlefont.render(self.talkname, True, (200,200,255,255)).convert_alpha(), (102, 2))
            start_pos=point(102,24)
            self.surface.blit(talkerhead, (0, 0))
        else:
            temp=titlefont.render(self.talkname, True, (200,200,255,255)).convert_alpha()
            self.surface.blit(temp, (380-temp.get_size()[0]-2, 2))
            start_pos=point(2,24)
            self.surface.blit(talkerhead, (380, 0))
        self.toward=toward
        for line in text:
            self.surface.blit(textfont.render(line, True, (200,200,255,255)).convert_alpha(),point2tuple(start_pos))
            start_pos.y+=17
        self.image=self.surface
        
    def eventupdate(sel,se,bias):
        pass



class FrameManager():
    def __init__(self):
        self.mxlst = []
        self.controllst = []
        self.hide = []

    def draw(self, scr, bias):
        for c in sorted(self.controllst, key=deepkey):
            if c.defname not in self.hide: c.draw(scr, bias)

    def get_show_controls(self):
        result = []
        for c in self.controllst:
            if c.defname not in self.hide: result.append(c)
        return result

    def get_control(self, sid):
        for c in self.controllst:
            if c.defname == sid: return c

    def add_control(self, lastcontrol, mux=False):
        if mux:
            # mux -> don't open frame again
            if self.isin(lastcontrol.defname):
                return False
            self.mxlst.append(lastcontrol.defname)
        self.controllst.append(lastcontrol)
        return True

    def eventupdate(self, evt, bias):
        for c in self.controllst:
            if c.defname not in self.hide: c.eventupdate(evt, bias)
    def update(self,tick):
        for c in self.controllst:
            if c.defname not in self.hide: c.update(tick)
    def remove_control(self, defname):
        for c in self.controllst:
            if c.defname == defname:
                self.controllst.remove(c)
                if defname in self.mxlst:
                    self.mxlst.remove(c.defname)
                if defname in self.hide:
                    self.hide.remove(c.defname)
                return

    def isin(self, defname):
        return defname in self.mxlst

    def hide_control(self, defname):
        self.hide.append(defname)

    def show_control(self, defname):
        self.hide.remove(defname)

    def hide_all(self):
        self.hide = ['']
        for control in self.controllst:
            if control.defname:
                self.hide.append(control.defname)



class EntityTouchPad(EntityFrame):
    def __init__(self, pos, boxrect, bottomcolor=(20, 40, 50, 50), deep=0, defname='', showdeep=0):
        super().__init__(pos=pos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.bias = point(0, 0)
        self.press = False

    def eventupdate(self, evt, bias):
        super().eventupdate(evt, bias + self.bias)
        if evt.type == PGKEY.MOUSEBUTTONDOWN and pointin(point(evt.pos[0], evt.pos[1]), self.get_hitbox_pos() - bias,
                                                         self.hitbox.rect):
            self.press = True
        elif evt.type == PGKEY.MOUSEMOTION and self.press:
            self.bias += tuple2point(evt.dict['rel'])
        elif evt.type == PGKEY.MOUSEBUTTONUP:
            self.press = False

    def draw(self, scr, bias):
        scr.blit(self.surface, point2tuple(self.get_hitbox_pos() - bias))
        for c in self.controllst:
            # c可能会到外面去，这是特性，因为做两矩形检测又麻烦又耗时
            c.draw(scr, bias + self.bias)


'''
0 1 TER_DONNOTDRAWPANCEL
0 2 TER_COURSE
0 4 TER_SWITCH_DRAWORDER : SWITCH the order of drawing controls and textlines
0 8
0 16
'''
TER_DONNOTDRAWPANCEL = 1
TER_COURSE = 2
TER_SWITCH_DRAWORDER = 4

def check_flags(bits,flag):
    return bits & flag


class EntityTerminal(EntityFrame):
    def __init__(self, pos, boxpos, boxrect, title, font, bottomcolor=(12, 12, 23, 50), titlefontcolor=(220,220,230,220),titlecolor=(37,151,148,220), shape=point(10,20), flags=0, deep=0, defname='', showdeep=0):
        super().__init__(pos=pos,boxrect=boxrect,bottomcolor=bottomcolor,deep=deep,defname=defname,showdeep=showdeep)
        self.title = title
        self.titlecolor = titlecolor
        self.titlefontcolor = titlefontcolor
        self.screen = []
        self.hash = []
        self.font = font
        self.shape = shape
        self.flags=flags
        self.screencache=[]
        self._boxpos=boxpos
        
        self.flush_title()
        self.flush_transdefault()
        self.flush()
    def flush_title(self):
        cache=self._get_text((self.title,self.titlefontcolor))
        size=cache.get_size()
        self.titlecache=pg.Surface((self.hitbox.rect.x,size[1]+4)).convert_alpha()
        if not check_flags(self.flags,TER_DONNOTDRAWPANCEL):
            self.titlecache.fill(self.titlecolor)
            self.titlecache.blit(cache,(2,2))
    def flush_transdefault(self):
        self.transdefault = self.screen
    def flush(self):
        self.screen = self.screen[max(len(self.screen)-self.shape.y,0):]
        self.hash = self.hash[max(len(self.hash)-self.shape.y,0):]
        
        for i in range(len(self.screen)):
            if i>=len(self.hash):
                #print('E:hash not sync',self.screen[i])
                self.hash.append(hash(self.screen[i]))
            # update cache
            if i>=len(self.screencache):
                self.screencache.append(self._get_text(self.screen[i]))
            if hash(self.screen[i])!=self.hash[i]:
                self.screencache[i]=(self._get_text(self.screen[i]))
                self.hash[i]=hash(self.screen[i])
                #print('hash')
        
        if len(self.hash)>len(self.screen):
            #print('E:hash not sync 2',file=sys._stderr)
            #self.hash=self.hash[max(len(self.hash)-len(self.screen),0):]
            pass
        if len(self.screencache)>len(self.screen):
            pass
            #print('E:sc not sync')
            #self.screencache=self.screencache[max(len(self.screencache)-len(self.screen),0):]
        #self.screencache=[]
        #for screen in self.screen:
        #    self.screencache.append(self._get_text(screen))
        self.flush_transdefault()
    def write_lines(self,lines,source=None,_hash=True):
        source=argstrans(source,self.transdefault)
        newlines=[]
        while len(lines)>0:
            element=lines.pop(0)
            temp=tuple(dividelst(element[0],self.shape.x,replacement=('',)))
            newlines.extend([(x,element[1]) for x in temp])
        source.extend(newlines)
        self.flush()
    def write(self,*args,color=(255,255,255,255),source=None,_hash=True):
        source=argstrans(source,self.transdefault)
        temp = (' '.join(args)).split('\n')
        color = tuple(color)
        if len(source)==0:
            temp=list(chain.from_iterable(map(lambda x:dividelst(x,self.shape.x,replacement=('',)),temp)))
            self.write_lines(list(zip(temp,[color for i in temp])),source=source,_hash=_hash)
        else:
            source[-1] = (source[-1][0]+temp[0],source[-1][1])
            if source[-1][0]:
                newlines=list(map(lambda x:(x,color),dividelst(source[-1][0],self.shape.x,replacement=('',))))
                source.pop(-1)
                source.extend(newlines)
            nextlines=temp[1:]
            self.write_lines(list(zip(chain.from_iterable(map(lambda x:tuple(dividelst(x,self.shape.x,replacement=('',))),nextlines)),[color for i in nextlines]))
                             ,source=source,_hash=_hash)
    def pop(self,linenum):
        self.screen.pop(linenum)
        self.hash.pop(linenum)
        self.screencache.pop(linenum)
    
    @functools.lru_cache(16)
    def _get_text(self,textcolor):
        return self.font.render(textcolor[0], True, textcolor[1]).convert_alpha()
    
    def draw(self,scr,bias):
        temppos=point2tuple(self.pos - bias)
        scr.blit(self.surface, temppos)
        scr.blit(self.titlecache, temppos)
        start_pos=(self.get_hitbox_pos() - bias+self._boxpos)
        if check_flags(self.flags,TER_SWITCH_DRAWORDER):
            for c in self.controllst:
                c.draw(scr, bias)
            for cache in self.screencache:
                scr.blit(cache,start_pos._intlist())
                start_pos.y+=cache.get_size()[1]+1
        else:
            for cache in self.screencache:
                scr.blit(cache,start_pos._intlist())
                start_pos.y+=cache.get_size()[1]+1
            for c in self.controllst:
                c.draw(scr, bias)
            
        
        




PROMPT_COLOR=(220,220,225,230)
class EntityTerminalPrompt(EntityTerminal):
    def __init__(self, pos, boxpos, boxrect, title, font, bottomcolor=(12, 12, 23, 200), titlefontcolor=(220,220,230,220),titlecolor=(37,151,148,220), shape=point(10,20), flags=0, deep=0, defname='', showdeep=0):
        self.history=[]
        super().__init__(pos=pos,boxpos=boxpos,boxrect=boxrect,title=title,font=font,bottomcolor=bottomcolor,titlefontcolor=titlefontcolor,shape=shape,flags=flags,deep=deep,defname=defname,showdeep=showdeep)
        self.prompt=''
        self.active=False
        self.flush_transdefault()
    def flush_transdefault(self):
        self.transdefault = self.history
    def screen_flush(self):
        self.screen = self.history[max(len(self.history)-self.shape.y,0):]
        self.write(self.prompt,color=PROMPT_COLOR,source=self.screen)
        if self.active:
            self.write('_',color=PROMPT_COLOR,source=self.screen)
        self.flush()
    def handle_prompt(self,prompt):
        pass
    def eventupdate(self,evt,bias):
        if evt.type ==PGKEY.MOUSEBUTTONDOWN and pointin(tuple2point(evt.dict['pos']),
                                                                    self.get_hitbox_pos() - bias,
                                                                    self.hitbox.rect):
            if self.active:
                self.active = False
            else:
                self.active = True
            self.screen_flush()
        
        elif self.active and evt.type in (PGKEY.KEYDOWN,PGKEY.KEYUP):
            if evt.type==PGKEY.KEYDOWN:
                if evt.dict['key'] == PGKEY.K_RETURN:
                    self.write(self.prompt+'\n',source=self.history,color=PROMPT_COLOR)
                    self.handle_prompt(self.prompt)
                    self.prompt=''
                elif evt.dict['key']!=PGKEY.K_BACKSPACE:
                    self.prompt+=evt.dict['unicode']
                else:
                    self.prompt = self.prompt[:-1]
            self.screen_flush()

# 能用
ERROR_COLOR=(222,40,72,220)
class Err_mirror:
    def __init__(self,we):
        self.write = we
class EntityTerminalDebug(EntityTerminalPrompt):
    def __init__(self, pos, boxpos, boxrect, title, font, bottomcolor=(20, 40, 50, 200), titlefontcolor=(220,220,230,220),titlecolor=(37,151,148,220), shape=point(10,20), flags=0, deep=0, defname='', showdeep=0):
        super().__init__(pos, boxpos, boxrect, title, font, bottomcolor, titlefontcolor,titlecolor, shape, flags, deep, defname, showdeep)
        self.err_mirror=Err_mirror(self.err_write)
        
        sys._stdout=sys.stdout
        sys.stdout=self
        sys._stderr=sys.stderr
        sys.stderr=self.err_mirror
        
        self.console=code.InteractiveConsole(locals=globals())
        self.console.write=self.err_write
        
        self.ps1='>> '
        self.ps2='.. '
        self.more = 0
        self.banner()
        
        self.prompt_back()
        self.screen_flush()
    def banner(self):
        cprt='Type "help", "copyright", "credits" or "license" for more information.\n\nI love you Neurosama heart heart heart'
        helps= '...Type get_world() to get main.World object...'
        self.write("Python %s on %s\n%s\n\n%s\n\n(console is %s)\n" %
                       (sys.version, sys.platform, cprt,helps,
                        self.__class__.__name__))
    def err_write(self,data):
        self.write(data,color=ERROR_COLOR,source=self.history)
    def prompt_back(self):
        self.write(self.ps2 if self.more else self.ps1,color=PROMPT_COLOR,source=self.history)
    def handle_prompt(self,prompt):
        try:
            self.more = self.console.push(prompt)
        except Exception as e:
            self.write('\n',source=self.history)
            self.console.showtraceback()
        self.prompt_back()
        self.flush()



def create_textlines(frame,textlines,font,start_pos,bias_y,bottomcolor,fontcolor,mode='left'):
    for line in textlines:
        tempLabel=EntityLabel(start_pos,point(0,0),line,font,bottomcolor,fontcolor)
        if mode=='centre':
            tempLabel.pos.x -= tempLabel.hitbox.rect.x//2
        elif mode=='right':
            tempLabel.pos.x -= tempLabel.hitbox.rect.x
        frame.add_control(tempLabel)
        start_pos.y+=bias_y



LASTTIME = 0
BACKIMAGES=['texture.trans','texture.entiy3','texture.entiy4']
BACKIMAGE=resmanager.DefResourceDomain.get_resource(random.choice(BACKIMAGES))
SENTENCE=random.choice(resmanager.NameResourceDomain.get_resource('sentences.normal1'))

def resentence(open_sentence='sentences.normal1'):
    global SENTENCE
    SENTENCE = random.choice(resmanager.NameResourceDomain.get_resource(open_sentence))

def _load_process_(text,bgimageres=None,bottomcolor=(15,16,40,200),open_sentence='sentences.normal1',tick=0):
    global LASTTIME,SENTENCE,BACKIMAGES,BACKIMAGE
    if LASTTIME + 20 < tick:
        BACKIMAGE=resmanager.DefResourceDomain.get_resource(random.choice(BACKIMAGES))
        LASTTIME = tick
        resentence(open_sentence)

    bgimage = resmanager.DefResourceDomain.get_resource(bgimageres) if bgimageres else BACKIMAGE
    if bgimage:get_world().surface.blit(bgimage,(0,0))
    
    text = normalfont.render(text, True, (200,210,200,220)).convert_alpha()
    textsize = text.get_size()
    image = pg.Surface((textsize[0]+80,45)).convert_alpha()
    image.fill(bottomcolor)
    size=tuple2point(image.get_size())
    top=get_centre_u(point(-size.x//2,-size.y//2),get_world().window)
    fonttop=get_centre_u(point(-textsize[0]/2,-textsize[1]//2),size)
    image.blit(text,fonttop._intlist())
    if open_sentence:
        #temp=resmanager.NameResourceDomain.get_resource(open_sentence)
        sentence=normalfont.render(SENTENCE,True, (200,210,200,220)).convert_alpha()
        sentencesize=tuple2point(sentence.get_size())
        sentencebottom=pg.Surface(sentence.get_size()).convert_alpha()
        sentencebottom.fill(bottomcolor)
        sentencetop=get_centre_u(point(-sentencesize.x//2,-sentencesize.y//2),get_world().window)+point(0,45+15)
        sentencebottom.blit(sentence,(0,0))
        get_world().surface.blit(sentencebottom,sentencetop._intlist())
    get_world().surface.blit(image,point2tuple(top))
    pg.display.update()


HISTORY=[]
def _load_process_text(text,textcolor):
    global HISTORY
    HISTORY.append(normalfont.render(text[:100], True, textcolor).convert_alpha())
    get_world().surface.fill((0,0,0,255))
    start_pos = point(2,2)
    bias_y = 18
    HISTORY = HISTORY[max(len(HISTORY)-28,0):]
    for text in HISTORY:
        if text:
            get_world().surface.blit(text,point2tuple(start_pos))
        start_pos.y += bias_y
    pg.display.update()



LOAD_PROCESS = {'GUI':_load_process_,'text':_load_process_text}