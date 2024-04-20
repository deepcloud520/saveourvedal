import pygame as pg
from resmanager import DefResourceDomain
import sys
from tool import *
import typing








class Entity:
    def __init__(self, pos : point, boxpos : point, boxrect : point, deep=0, defname=None, showdeep=0,info=''):
        # defname 是用来方便找对象的
        self.pos = get_posmap()[1](pos, deep)
        self.hitbox = Box(boxpos, boxrect)
        self.lasttick = 0
        self.alive = True
        self.image = None
        self.defname = defname if defname else ''
        self.interfunc = None
        self.showdeep = showdeep
        self.deep = deep
        self.info = info

    def update(self, tick=0):
        pass

    def draw(self, scr: pg.Surface, bias : point):
        if self.image:
            scr.blit(self.image, (self.get_screenpos(bias))._intlist())

    def set_dead(self):
        self.alive = False

    def get_hitbox_pos(self):
        return self.pos + self.hitbox.pos

    def oninteracted(self, fromentity):
        self.interfunc(self, fromentity)

    def replace_interacted(self, func):
        self.interfunc = func

    def onhited(self, target, nhp, wayp, hittype):
        pass

    def get_screenpos(self, bias):
        return get_posmap()[0](self.pos - bias, self.deep)

    def get_brightinfo(self):
        # return point(0,0),0
        return None
    # hit system


class Bullet:
    def __init__(self, textures, damageradius, damage, faction=None):
        self.textures = textures
        self.damageradius = damageradius
        self.damage = damage
        self.faction = faction

    def draw(self, scr, camera_pos, box):
        pg.draw.circle(scr, (10, 100, 250), (box.pos - camera_pos)._intlist(), self.damageradius, 2)

    def damage(self, living, bulletbox, bulletvel, bulletfaction):
        if isinstance(living, EntityPlayerBase) and self.faction != bulletfaction:
            living.livingpoint -= self.damage


class EntityImage(Entity):
    def __init__(self, pos, textures,boxpos=point(0, 0),boxrect=point(0, 0),deep=0, defname=None, showdeep=0,info=''):
        super().__init__(pos, boxpos=boxpos, boxrect=boxrect, deep=deep, defname=defname, showdeep=showdeep,info=info)
        self.textures = textures
        self.frame_counter = 0
        self.stat = textures['i_0'][1]
        self.frame = textures['i_0'][2]
        self.image = DefResourceDomain.get_resource(self.frame)

    def update(self, tick=0):
        if self.lasttick < tick:
            super().update(tick)
            self.frame_counter += 1
            if self.textures[self.stat][0] == self.frame_counter:
                self.stat = self.textures[self.stat][1]
                self.frame = self.textures[self.stat][2]

                self.frame_counter = 0
            self.lasttick = tick


class EntityBlocked(Entity):
    def __init__(self, pos, rect, deep=0, defname=None, showdeep=0):
        super().__init__(pos, point(0, 0), rect, deep=deep, defname=defname, showdeep=showdeep)
        self.isblocked = True

    def draw(self, scr, bias):
        '''
        pg.draw.rect(scr, (100, 0, 0, 255),
                     (*(self.pos - bias + self.hitbox.pos)._intlist(), *self.hitbox.rect._intlist()), 1)
        '''
        #pg.draw.rect(scr, (100, 0, 0, 255),
        #             (*(self.pos - bias + self.hitbox.pos)._intlist(), *self.hitbox.rect._intlist()), 1)


class EntityLiving(Entity):
    def __init__(self, pos, boxpos, boxrect, deep=0, defname=None, showdeep=0,info=''):
        super().__init__(pos, boxpos, boxrect, deep=deep, defname=defname, showdeep=showdeep,info=info)
        self.vel = point(0, 0)
        self.alive = True

    def update(self, tick):
        self.pos += self.vel
        self.vel.x *= 0.96
        #if not hitflag else 0.945
        self.vel.y *= 0.99999
    def draw(self, scr, bias):
        pass
        #pg.draw.rect(scr, (0, 100, 0, 255), (*(self.pos - bias)._intlist(), *self.hitbox.rect._intlist()), 1)
    def onnothitflag(self):
        self.vel.y += 0.02

class EntityPlayerBase(EntityLiving):
    pass

class EntityPlayerBase_(EntityLiving):
    def __init__(self, pos, boxpos, boxrect, name, textures, deep=0, defname=None, showdeep=0, maxlivingpoint=100,
                 faction=None):
        super().__init__(pos, boxpos, boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.name = name
        self.textures = textures
        self.stat = textures['e_0'][1]
        self.frame = textures['e_0'][2]
        self.lasttick = 0
        self.frame_counter = 0
        self.maxlivingpoint = maxlivingpoint
        self.livingpoint = maxlivingpoint
        self.faction = faction

    def update(self, tick):
        if self.lasttick < tick:

            super().update(tick)
            if self.vel.x > 0 and ('w_' not in self.stat or 'ew_' in self.stat):
                self.stat = 'w_0'
                self.frame_counter = 0
                # return
            elif self.vel.x < 0 and ('w_' not in self.stat or 'ew_' not in self.stat):
                self.stat = 'ew_0'
                self.frame_counter = 0
                # return
            '''
            elif (self.vel.x==0 and 'w_' in self.stat):
                self.stat='e_0'
                self.frame_counter=0
                #return
            '''
            if not ((('w_' in self.stat or 'ew_' in self.stat) and self.vel.y != 0) or (
                    'w_' in self.stat and self.vel.x == 0)): self.frame_counter += 1
            if self.textures[self.stat][0] == self.frame_counter:
                self.stat = self.textures[self.stat][1]
                self.frame = self.textures[self.stat][2]
                self.frame_counter = 0
                # print(self.stat)
                # time.sleep(0.8)

            self.lasttick = tick

    def draw(self, scr, bias):
        super().draw(scr, bias)
        self.image = DefResourceDomain.get_resource(self.frame)
        Entity.draw(self, scr, bias)


class EntityPlayer(EntityPlayerBase_):
    def __init__(self, pos, boxpos, boxrect, name, textures, deep=0, defname=None, showdeep=0):
        super().__init__(pos, boxpos, boxrect, name=name, textures=textures, deep=deep, defname=defname,
                         showdeep=showdeep)
        self.reset_jumpcount()
        self.canmove = 0

    def reset_jumpcount(self):
        self.jumpcount = 1

    def jump(self, force=5):
        if self.jumpcount > 0:
            self.vel.y -= force
            self.jumpcount -= 1

    def move(self, way, force=0.08):
        if way == 'left' and self.canmove != -1:
            self.vel.x -= force
        elif way == 'right' and self.canmove != 1:
            self.vel.x += force
        elif way == None and 'w_' in self.stat:
            self.stat = 'e_0'
            self.frame_counter = 0

    def onhited(self, target, nhp, wayp, hittype):
        # 用来防止粘在墙上的补丁
        # 应该在update里重设canmove=2 没试过
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
                # p1,p3 好像是上下面碰撞
                self.reset_jumpcount()

        # print(hittype)


class WorldEngine:
    def __init__(self):
        # self.frontimages_line=[]
        self.clear_all()
        self.camera_pos = point(0, 0)
        self.brightness = []

    def get_blockeds_line(self):
        return self.blockeds_line

    def get_livings_line(self):
        return self.livings_line

    def get_images_line(self):
        return self.images_line

    def clear_all(self):
        self.blockeds_line = []
        self.livings_line = []
        self.images_line = []
        # (box,vel,father,faction)
        self.bullets_line = []

    # def get_frontimages_line(self):return self.frontimages_line
    def draw(self, scr):
        for entity in sorted(self.images_line + self.blockeds_line + self.livings_line, key=deepkey):
            entity.draw(scr, self.camera_pos)
        for b_pos, b_vel, b_father, b_faction in self.bullets_line:
            b_father.draw(scr, self.camera_pos, b_pos)

    def get_brightness(self, pos):
        if not self.brightness: return 0
        brightsum = 0
        for bpos, strength in self.brightness:
            brightsum += (1 - min(get_d_square(pos, bpos), 80000) / 80000)
        return brightsum

    def update(self, tick=0):
        brightness = []
        for image in self.images_line:
            bi = image.get_brightinfo()
            if bi: brightness.append(bi)
            image.update(tick)
        for blocked in self.blockeds_line:
            bi = blocked.get_brightinfo()
            if bi: brightness.append(bi)
            blocked.update(tick)
        rmtemp = []
        for living in self.livings_line:
            bi = living.get_brightinfo()
            if bi: brightness.append(bi)
            living.update(tick)
            if not living.alive:
                rmtemp.append(living)
        for r in rmtemp:
            self.livings_line.remove(r)
        for b_box, b_vel, b_father, b_faction in self.bullets_line:
            b_box.pos += b_vel
            for living in self.livings_line:
                hit = uncom_segment_oneforone_part(*get4pos_bybox(b_box), living)
                if hit:
                    b_father.damage(living)

            rmtemp = []
            for blocked in self.blockeds_line:
                hit = uncom_segment_oneforone_part(*get4pos_bybox(b_box), blocked)
                if hit:
                    rmtemp.append((b_box, b_vel, b_father, b_faction))

        for rm in rmtemp:
            self.bullets_line.remove(rm)
            print(rmtemp)
        self.brightness = brightness
        # for frontimage in self.frontimages_line:
        #    frontimage.update(tick)
        
        #
        # 这是我 2022年暑假写的代码
        # 没有一行注释
        # 现在这里是未知领域了
        # 前面的区域，以后再来探索吧
        #

        for living in self.livings_line:
            hits = segment_oneforall(living, self.blockeds_line)

            hitflag = False
            # detlax= if living.vel.x>0 else
            # detlay= if living.vel.y>0 else
            for hit in hits:

                blockedcentre = get_centre(hit)
                livingcentre = get_centre(living)
                hitboxpos = living.get_hitbox_pos()
                blockedboxpos = hit.get_hitbox_pos()
                if living.vel.x > 0:
                    detlax = abs(hitboxpos.x + living.hitbox.rect.x - blockedboxpos.x)
                elif living.vel.x < 0:
                    detlax = abs(blockedboxpos.x + hit.hitbox.rect.x - hitboxpos.x)
                else:
                    detlax = 0
                if living.vel.y > 0:
                    detlay = abs(hitboxpos.y + living.hitbox.rect.y - blockedboxpos.y)
                elif living.vel.y < 0:
                    detlay = abs(blockedboxpos.y + hit.hitbox.rect.y - hitboxpos.y)
                else:
                    detlay = 0

                nhx = round((hit.hitbox.rect.x / 2 + living.hitbox.rect.x / 2) - abs(blockedcentre.x - livingcentre.x),
                            5)
                nhy = round((hit.hitbox.rect.y / 2 + living.hitbox.rect.y / 2) - abs(blockedcentre.y - livingcentre.y),
                            5)
                timex = abs(detlax / living.vel.x) if living.vel.x != 0 else 0
                timey = abs(detlay / living.vel.y) if living.vel.y != 0 else 0

                if living.vel.x > 0:
                    wayx = -1
                elif living.vel.x < 0:
                    wayx = 1
                else:
                    wayx = 0
                if living.vel.y > 0:
                    wayy = -1
                elif living.vel.y < 0:
                    wayy = 1
                else:
                    wayy = 0
                # time.sleep(1)
                # printtext('{%f,%f},{%f,%f}' % (hitboxpos.x,hitboxpos.y,living.vel.x,living.vel.y),middle_chinese,point(100,55),scr)
                # printtext(str(hits),middle_chinese,point(10,10),scr)
                # printtext('hitinfo {%f %f %f %f}' % (detlax,detlay,timex,timey),middle_chinese,point(10,25),scr)
                # printtext('NH',middle_chinese,point(10,85),scr)
                # print(blockedboxpos.y,hitboxpos.y,living.vel.y)
                # print('x',timex,timey,wayy*living.vel.y)
                # print('y',timex,timey,wayx*living.vel.x)
                # printtext('P5',middle_chinese,point(10,100),scr)
                # print('dy',detlax,detlay,wayx*living.vel.x)
                # print('dx',detlay,wayy )
                # printtext(str(hits),middle_chinese,point(10,10),scr)
                # printtext('hitinfo {%f %f %f %f}' % (detlax,detlay,timex,timey),middle_chinese,point(10,25),scr)
                # time.sleep(0.03)

                if (nhx == 0 and living.vel.x == 0) or (nhy == 0 and living.vel.y == 0):
                    if (nhy == 0 and living.vel.y == 0 and (hitboxpos.y < blockedboxpos.y)):
                        hitflag = True
                        nhp = point(nhx, nhy)
                        wayp = point(wayx, wayy)
                        living.onhited(hit, nhp, wayp, hittype='nh')
                        hit.onhited(living, nhp, wayp, hittype='nh')
                        # printtext('NH',middle_chinese,point(10,85),scr)
                    hittype = 'nh'
                    continue
                # Hit

                # if len(hits)==2:
                #    print(blockedboxpos.x,detlax,detlay,living.vel.x,living.vel.y,timex,timey,hitboxpos.x,hitboxpos.y)
                # print('/',living.vel.x,living.vel.y)
                if living.vel.x == 0:
                    hittype = 'p1'
                    if hit.isblocked:
                        # print('1')
                        living.pos.y += wayy * detlay
                        if wayy * living.vel.y < 0: living.vel.y = 0
                        hitflag = True


                elif living.vel.y == 0:
                    hittype = 'p2'
                    if hit.isblocked:
                        # print('2',wayx,detlax,living.pos.x,timex,nhx,nhy)
                        living.pos.x += wayx * detlax
                        if wayx * living.vel.x < 0: living.vel.x = 0
                        hitflag = True

                elif timex > timey:
                    hittype = 'p3'
                    if hit.isblocked:
                        # print('3',wayx,detlax,detlay,living.pos.x,living.pos.y,timex,timey,nhx,nhy)
                        living.pos.y += wayy * abs(living.vel.y * timey)
                        # hitboxpos.x+=wayx*abs(living.vel.x*timey)
                        if wayx * living.vel.x < 0: living.vel.x = 0
                        # if nhy*living.vel.y>0:living.vel.y=0
                        living.vel.y = 0
                        hitflag = True

                elif timex < timey:
                    hittype = 'p4'
                    if hit.isblocked:
                        # print('4')
                        # hitboxpos.y+=wayy*abs(living.vel.y*timex)
                        living.pos.x += wayx * abs(living.vel.x * timex)
                        if wayy * living.vel.y < 0: living.vel.y = 0
                        # if nhx*living.vel.x>0:living.vel.x=0
                        living.vel.x = 0
                        hitflag = True

                else:
                    # print('p5')
                    print('Fatel')
                    input()
                nhp = point(nhx, nhy)
                wayp = point(wayx, wayy)
                living.onhited(hit, nhp, wayp, hittype=hittype)
                hit.onhited(living, nhp, wayp, hittype=hittype)
                # print('-',blockedboxpos.x,detlax,detlay,timex,timey,hitboxpos.x,hitboxpos.y)
                # print(wayy)
            if not hitflag:
                living.onnothitflag()
                

            if abs(living.vel.x) < 0.0001: living.vel.x = 0
            if abs(living.vel.y) < 0.0001: living.vel.y = 0
        # print()


# Example
if __name__ == '__main__':
    pg.init()
    WINDOW = point(600, 480)
    middle_chinese = pg.font.Font(None, 16)
    from pygame.locals import QUIT, KEYDOWN, K_j, K_a, K_d

    scr = pg.display.set_mode(WINDOW._list())
    set_posmap(WINDOW)
    ew = WorldEngine()
    ew.get_blockeds_line().extend(
        [EntityBlocked(point(250, 0), point(100, 30)), EntityBlocked(point(100, 100), point(100, 30)),
         EntityBlocked(point(100, 200), point(400, 10)), EntityBlocked(point(200, 150), point(40, 250)),
         EntityBlocked(point(150, 150), point(40, 50))])
    p = EntityLiving(point(150, 50), point(0, 0), point(25, 60))
    ew.get_livings_line().extend([p])

    while True:
        scr.fill((0, 0, 0))
        ew.update()
        for evt in pg.event.get():
            if evt.type == QUIT:
                sys.exit()
            if evt.type == KEYDOWN:
                key = evt.dict['key']
                if key == K_j:
                    p.vel.y -= 1.5
        keys = pg.key.get_pressed()
        if keys[K_a]: p.vel.x -= 0.08
        if keys[K_d]: p.vel.x += 0.08
        ew.camera_pos = get_centre_u(p.pos, point(0, 0) - WINDOW)
        
        ew.draw(scr)
        printtext('{%f,%f},{%f,%f}' % (p.pos.x, p.pos.y, p.vel.x, p.vel.y), middle_chinese, point(100, 55), scr)
        pg.display.update()
