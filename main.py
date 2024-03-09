import worldcore
import scriptcore, sys,logging
from resmanager import *
from tool import *
from newcoretiny import *
import pygame as pg
from pygame.locals import *

pg.init()

FORMAT = '[%(name)s/%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(format=FORMAT)



class World:
    def __init__(self, name, window, sur, bs):
        self.name = name
        
        self.engine = worldcore.WorldEngine()
        self.eventrunner = EventRunner('world', self)
        self.window = window
        self.surface = sur
        self.buffersurface = bs
        self.effects=[]
        self.fps=0
        
        self.boot = scriptcore.create_scriptRunner(name, 'python', self)()
        self.version = self.boot.script.VERSION
    
    def postinit(self):
        self.boot.get_scriptattr('postinit')()

    def get_engine(self): return self.engine

    def update(self, tick):
        self.eventrunner.update(tick)
        self.engine.update(tick)
        # self.textdisplay.update(tick)
        self.boot.get_scriptattr('gameupdate')(tick)
        
        rmlst=[]
        for effect in self.effects:
            if effect.update(tick):
                rmlst.append(effect)
        for r in rmlst:
            self.effects.remove(r)
    def draw(self, bs):
        self.engine.draw(bs)
        self.boot.get_scriptattr('gamedraw')(bs)
        for effect in self.effects:
            effect.draw(bs)
    def get_centre(self, pos):
        return get_centre_u(pos, point(0, 0) - WINDOW)

    def eventupdate(self, singlevent):
        return self.boot.get_scriptattr('eventupdate')(singlevent)

WINDOW = point(800, 600)
middle_chinese = pg.font.Font('yahei.ttf', 13)
big_chinese = pg.font.Font('yahei.ttf', 14)
FPS=50
if __name__ == '__main__':
    scr = pg.display.set_mode(point2tuple(WINDOW))
    OPEN_ALPHA = False
    if OPEN_ALPHA:
        bs = scr.convert_alpha()
    else:
        bs = scr.convert()
    
    bs.set_alpha(255)
    set_posmap(WINDOW)
    scr.set_alpha(255)
    
    world = World('saveourvedal', WINDOW, scr, bs)
    pg.display.set_caption(world.boot.script.FORMALNAME)
    world.postinit()
    
    nowtick = 0
    runtick = 0
    lasttick = 0
    detlatick = 0
    def debug_save():
        world.boot.script.save()
    
    while True:
        scr.blit(bs, (0, 0))
        
        for evt in pg.event.get():
            if evt.type == QUIT:
                world.boot.script.whenexit()
                sys.exit()
            world.eventupdate(evt)

        lasttick = nowtick
        nowtick = pg.time.get_ticks()
        detlatick += nowtick - lasttick
        if detlatick >= (1000 // FPS):
            world.fps = 1000 // (nowtick - lasttick)
            detlatick -= (1000 // FPS)
            runtick += 1
            
            bs.fill((0, 0, 0, 255))
            world.update(runtick)
            world.draw(bs)
            pg.display.update()
