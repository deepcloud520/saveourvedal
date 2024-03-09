import sys, json, os

sys.path.append(sys.path[0] + '/def/saveourship')
from worldcore import *
#from resmanager import resmanager.DefResourceDomain,resmanager.NameResourceDomain,resmanager.SaveResourceDomain
import resmanager
from newcoretiny import *
from local import *
import copy
from evilcore import fast_print

LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
HARDCONNECT = 0
SEPARATOR = 1



class Stage():
    def __init__(self, fathertoward):
        self.left_child = None
        self.right_child = None
        self.up_child = None
        self.down_child = None

        self.fathertoward = fathertoward
        self.name = resmanager.SaveResourceDomain.get_resource('stageCounter').nextid()
        self.parts_stack = [] # [(),]

        self.active=False
        self.clear_info()

    def add_left_child(self, ctype,_stage):
        if not self.fathertoward == LEFT:
            self.left_child = (_stage, ctype)
            return self.left_child

    def add_right_child(self, ctype,_stage):
        if not self.fathertoward == RIGHT:
            self.right_child = (_stage, ctype)
            return self.right_child

    def add_up_child(self, ctype,_stage):
        if not self.fathertoward == UP:
            self.up_child = (_stage, ctype)
            return self.up_child

    def add_down_child(self, ctype,_stage):
        if not self.fathertoward == DOWN:
            self.down_child = (_stage, ctype)
            return self.down_child

    def update_info(self):
        self.clear_info()
        for part in self.parts_stack:
            realpart = resmanager.DefResourceDomain.get_resource(part)
            self.mass += realpart['mass']
            for rename, resnum in realpart['resource'].items():
                self.resource[rename] += resnum
            for powname, pownum in realpart['power'].items():
                self.power[powname] += pownum
            
            if 'Thruster' in realpart['type']:
                self.thrust+=realpart['thrust']

            if 'Pod' in realpart['type']:
                # 还需要检查pod的开机条件，上面也是，不写了
                self.controlable = True
            self.cost+= realpart['cost']
    def clear_info(self):
        self.controlable = False
        self.resource = {'LiquidFuel':0,'SolidFuel': 0, 'Electricity': 0}
        # 除了引擎开机时这么消耗
        self.power = {'SolidFuel':0,'LiquidFuel': 0, 'Electricity': 0}
        self.mass = 0
        # 最大
        self.thrust = 0
        self.resource_consumption = {'SolidFuel':0,'LiquidFuel': 0}
        
        self.cost=0


'''
class EntityLiving_Rocket(EntityLiving):
    def __init__(self, pos, boxpos, boxrect, parts, deep=0, defname=None, showdeep=0):
        super().__init__(pos, boxpos, boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.parts = parts
        self.mass = mass
        self.resource = resource

'''
class EntityLiving_RocketPart_Base(EntityLiving):
    def __init__(self, pos,args, deep=0, defname=None, showdeep=0):
        boxpos,boxrect=map(str2point,args['hitbox'])
        super().__init__(pos, boxpos, boxrect, deep=deep, defname=defname, showdeep=showdeep)
        self.textures=args['image']
        
        self.relpos=pos
        
        self.stat='normal'
        self.play_num=0
        self.image=resmanager.DefResourceDomain.get_resource(self.textures[self.stat][self.play_num][0])
        
        self.power=args['power']
        self.resource=args['resource']
        self.type=args['type']
        self.drymass=args['mass']
        self.mass=self.drymass
        self.cost=args['cost']
        self.pos=point(0,0)
        #self.resource_consumption=args['resource_consumption']
    def update(self,tick,rocket,part,stage):
        temp=self.textures[self.stat]
        if self.lasttick-tick <= temp[self.play_num][1]:
            self.lasttick=tick
            self.play_num = (self.play_num+1) % len(temp)
            self.image = resmanager.DefResourceDomain.get_resource(temp[self.play_num][0])
    def draw(self,scr,bias):
        self.pos=(self.relpos-bias)
        scr.blit(self.image,(self.pos)._intlist())
        
        #pg.draw.rect(scr, (100, 0, 0, 255),
        #             (*(self.pos + self.hitbox.pos)._intlist(), *self.hitbox.rect._intlist()), 1)
class EntityLiving_RocketPart_UnmanedPod(EntityLiving_RocketPart_Base):
    pass



P_SOLIDFUEL=0.008
P_LIQUIDFUEL=0.010



class EntityLiving_RocketPart_LiquidFuelTank(EntityLiving_RocketPart_Base):
    def update(self,tick,rocket,part,stage):
        super().update(tick,rocket,part,stage)
        self.mass=self.drymass+self.resource['LiquidFuel']*P_LIQUIDFUEL




class EntityLiving_RocketPart_LiquidThruster(EntityLiving_RocketPart_Base):
    def __init__(self, pos,args, deep=0, defname=None, showdeep=0):
        super().__init__(pos,args,deep,defname,showdeep)
        self.thrust=0
        self.active=False
        self.resource_consumption=args['resource_consumption']
        self.max_thrust=args['thrust']
        self.fire_lasttick=0
        self.fire_num=0
        self.fire_width=30#resmanager.DefResourceDomain.get_resource('texture.rocket.ST_fire_0').get_size()[1]/2
    def update(self,tick,rocket,part,stage):
        super().update(tick,rocket,part,stage)
        
        if stage.active:
            resource_consumption=self.resource_consumption*rocket.engine_valve
            if stage.resource['LiquidFuel']>=resource_consumption:
                stage.handle_resource_requirement({'LiquidFuel':resource_consumption})
                self.thrust=self.max_thrust*rocket.engine_valve
                
            else:
                if stage.resource['LiquidFuel']>0:
                    self.thrust = self.max_thrust*(stage.resource['LiquidFuel']/resource_consumption)
                    stage.handle_resource_requirement({'LiquidFuel':stage.resource['LiquidFuel']})
                else:
                    self.thrust=0
            if self.fire_lasttick+1<=tick:
                self.fire_lasttick=tick
                self.fire_num=(self.fire_num + 1) % 3
        else:
            self.thrust = 0
    def draw(self,scr,bias):
        super().draw(scr,bias)
        if self.thrust>0:
            bottom=self.pos.copy()
            bottom.y+=self.hitbox.rect.y
            bottom.x+=(self.hitbox.rect.x-self.fire_width)/2
            scr.blit(resmanager.DefResourceDomain.get_resource('texture.rocket.ST_fire_'+str(self.fire_num)),bottom._intlist())



class EntityLiving_RocketPart_SolidThruster(EntityLiving_RocketPart_Base):
    def __init__(self, pos,args, deep=0, defname=None, showdeep=0):
        super().__init__(pos,args,deep,defname,showdeep)
        self.thrust=0
        self.active=False
        self.resource_consumption=args['resource_consumption']
        self.max_thrust=args['thrust']
        self.fire_lasttick=0
        self.fire_num=0
        self.fire_width=30#resmanager.DefResourceDomain.get_resource('texture.rocket.ST_fire_0').get_size()[1]/2
    def update(self,tick,rocket,part,stage):
        super().update(tick,rocket,part,stage)
        if stage.active:
            self.active=True
        if self.active:
            if self.resource['SolidFuel']>=self.resource_consumption:
                self.resource['SolidFuel']-=self.resource_consumption
                self.thrust=self.max_thrust
                self.mass=self.drymass+self.resource['SolidFuel']*P_SOLIDFUEL
                
            else:
                if self.resource['SolidFuel']>0:
                    self.thrust = self.max_thrust*(self.resource['SolidFuel']/self.resource_consumption)
                    self.resource['SolidFuel']=0
                else:
                    self.thrust=0
            if self.fire_lasttick+1<=tick:
                self.fire_lasttick=tick
                self.fire_num=(self.fire_num + 1) % 3
    def draw(self,scr,bias):
        super().draw(scr,bias)
        if self.thrust>0:
            bottom=self.pos.copy()
            bottom.y+=self.hitbox.rect.y
            bottom.x+=(self.hitbox.rect.x-self.fire_width)/2
            scr.blit(resmanager.DefResourceDomain.get_resource('texture.rocket.ST_fire_'+str(self.fire_num)),bottom._intlist())
         



# 单个part
# RocketpPart->Stage->part(res)
'''
class RocketPart():
    def __init__(self,stages, deep=0,):
        self.stages=stages
        self.clear_info()
    def update_info(self):
        self.clear_info()
        for stage in self.stages:
            stage.update_info()
            if stage.controlable:self.controlable = True
            for n,i in stage.resource.items():
                if n not in self.resource:
                    self.resource.update({n,i})
                else:
                    self.resource[n]+=i
            for n,i in stage.power.items():
                if n not in self.power:
                    self.power.update({n,i})
                else:
                    self.power[n]+=i
            self.cost += stage.cost
            self.mass += stage.mass
            if stage.controlable:
                self.controlable = True
            #还有controlable，mass
            if stage.active:
                # 计算引擎
                if  'SolidThruster' in stage['type']:
                    self.thrust += realpart['thrust']
                    self.resource_consumption['SolidFuel'] += realpart['resource_consumption']
                elif 'LiquidThruster' in stage['type']:
                    # 记得用函数处理曲线
                    self.thrust += realpart['thrust']*self.engine_valve
                    self.resource_consumption['SolidFuel'] += realpart['resource_consumption']*self.engine_valve
            
            #if stage['type']=='SolidThruster':
            #    self.thrust+=stage['type']
            #elif stage['type']=='LiquidThruster'
            
    def clear_info(self):
        self.controlable = False     
        self.engine_valve = 0
        self.resource = {'LiquidFuel':0,'SolidFuel': 0, 'Electricity': 0}
        # 除了引擎开机时这么消耗
        self.power = {'SolidFuel':0,'LiquidFuel': 0, 'Electricity': 0}
        self.resource_consumption = {'SolidFuel':0,'LiquidFuel': 0}
        self.mass = 0
        self.cost = 0
        # 最大
        self.thrust = 0
        
        self.active=False
    def update(self):
        if self.active:
            for powname,pownum in self.power:
                if self.resource[powname] < pownum:
                    self.active = False
                    break
                self.resource[powname] -= pownum
            for fname,fnum in self.resource_consumption:
                if self.resource[fname] < fnum:
                    self.active = False
                    break
                self.resource[fname] -= fnum
        self.update_info()

class Rocket():
    def __init__(self,mainstage):
        #使用mainstage做参数。主控仓只能有一个

    def clear(self):
        # 清算剩余部件
        self.connects={}
        # 开始DFS遍历
        # 这是发射时生成的-可保存对象-
        #另一个是EntityLiving_Rocket，是worldcore的对象，渲染由那边负责，这里是火箭状态的计算
        def stage_warper(nowstage):
            #硬链接为整体，分离器就分开
            # 递归和循环都有
            sep_list=[]
            part_list=[]
            part_stack=[]
            hard_avail=[nowstage]
            while hard_avail:
                nowpart=hard_avail.pop(0)
                part_stack.append(nowpart)
                for _child in (nowpart.left_child,nowpart.right_child,nowpart.up_child,nowpart.down_child):
                    if _child:
                        connecttype=_child[1]
                        if connecttype==HARDCONNECT:
                            hard_avail.append(_child[0])
                        elif connecttype==SEPARATOR:
                            part_list.extend(stage_warper(_child[0]))
                            # 孩子-》父亲 分离用
                            self.connects.update({_child[0].name:nowpart.name})
            part_list.append(RocketPart(part_stack))
            self.stages.extend(part_stack)
            return part_list
        self.parts = stage_warper(self.mainstage)
        self.main_part = self.parts[-1]
    def clear_info(self):
        self.engine_valve = 0
        self.resource = {'LiquidFuel':0,'SolidFuel': 0, 'Electricity': 0}
        # 除了引擎开机时这么消耗
        self.power = {'SolidFuel':0,'LiquidFuel': 0, 'Electricity': 0}
        self.resource_consumption = {'SolidFuel':0,'LiquidFuel': 0}
        self.mass = 0
    def update(self):
        self.clear_info()
        for part in self.parts:
            part.update()
            self.mass+=part.mass
            for item,value in part.resource.items():
                self.resource[item]+=value
            for item,value in part.resource_consumption.items():
                self.resource_consumption[item]+=value
    def update_info(self):
        for part in self.parts:
            part.update_info()
'''



class RocketPart:
    # 负责资源管理。that‘s all
    def __init__(self,stages):
        self.stages=stages
        self.clear_info()
    def update_info(self):
        last_resource = self.resource
        
        self.clear_info()
        for stage in self.stages:
            stage.update_info()
            if stage.controlable:self.controlable = True
            for n,i in stage.resource.items():
                if n not in self.resource:
                    self.resource.update({n,i})
                else:
                    self.resource[n]+=i
            for n,i in stage.power.items():
                if n not in self.power:
                    self.power.update({n,i})
                else:
                    self.power[n]+=i
            self.cost += stage.cost
            self.mass += stage.mass
            if stage.controlable:
                self.controlable = True
            self.thrust+=stage.thrust
        self.resource_consumption = get_dictdetla(last_resource,self.resource)

    def clear_info(self):
        self.controlable = False     
        #self.engine_valve = 0
        self.resource = {'LiquidFuel':0,'SolidFuel': 0, 'Electricity': 0}
        # 除了引擎开机时这么消耗
        self.power = {'SolidFuel':0,'LiquidFuel': 0, 'Electricity': 0}
        self.resource_consumption = self.resource.copy()
        self.mass = 0
        self.cost = 0
        # 总共
        self.thrust = 0
        #self.active=False
        
    def update(self,tick,rocket):
        for stage in self.stages:
            stage.update(tick,rocket,self)
def draw_stage(stage):
    ret=[]
    typedict={'UnmanedPod':EntityLiving_RocketPart_UnmanedPod,
              'SolidThruster':EntityLiving_RocketPart_SolidThruster,
              'LiquidThruster':EntityLiving_RocketPart_LiquidThruster,
              'LiquidFuelTank':EntityLiving_RocketPart_LiquidFuelTank
              }
    start_y=0  
    #
    #  以中心对称线为x=0
    #
    x=0
    for partname in stage.parts_stack:
        realpart=copy.deepcopy(resmanager.DefResourceDomain.get_resource(partname))
        boxpos,boxrect=map(str2point,realpart['hitbox'])
        #hitbox=map(str2point,realpart['hitbox'])
        ret.append(
            typedict[realpart['type']](point(-boxrect.x/2,start_y)-boxpos,realpart)
            )
        start_y+=boxrect.y
        x=max(x,boxrect.x)
    return ret,point(x,start_y)
#
# stage.x-max_half_x
#


#
#  #IMPORTANT 渲染的时候要加上hitbox.x/2
#

#
# 这些都是相对坐标
#


#
# 具体逻辑：EntityLiving_RocketPart_...
# 资源管理:RocketPart
# 激活状态管理:EntityStage
#



class EntityStage(Stage):
    # 继承Stage 方便RocketPart计算，这里的数据不重要
    def __init__(self,pos,hitbox,parts_stack,left_child,right_child,up_child,down_child,name):
        self.left_child = left_child
        self.right_child = right_child
        self.up_child = up_child
        self.down_child = down_child
        #Traceback (most recent call last):
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/main.py", line 77, in <module>
        #     world.eventupdate(evt)
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/main.py", line 44, in eventupdate
        #     return self.boot.get_scriptattr('eventupdate')(singlevent)
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/def/saveourship/__init__.py", line 52, in eventupdate
        #     get_MCO().eventupdate(se)
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/def/saveourship/neurocore.py", line 1159, in eventupdate
        #     self.framemanager.eventupdate(se, point(0, 0))
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/def/saveourship/neurocore.py", line 416, in eventupdate
        #     if c.defname not in self.hide: c.eventupdate(evt, bias)
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/def/saveourship/neurocore.py", line 241, in eventupdate
        #     c.eventupdate(evt, bias)
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/def/saveourship/neurocore.py", line 241, in eventupdate
        #     c.eventupdate(evt, bias)
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/def/saveourship/neurocore.py", line 63, in eventupdate
        #     self.definedfunction(self.defname)
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/def/saveourship/neurocore.py", line 1069, in launch
        #     warp_(rocket.mainstage) # 递归添加到控制版上
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/def/saveourship/neurocore.py", line 1046, in warp_
        #     controlpad.add_left_child(*wstage.left_child[::-1])
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/def/saveourship/neurocore.py", line 562, in add_left_child
        #     temp = self.focus.add_left_child(ctype,_stage)
        #   File "/home/pi/Desktop/各种项目/python/pyacimth/RPG2/def/saveourship/rocketcore.py", line 47, in add_left_child
        #     if not self.fathertoward == LEFT:
        # AttributeError: 'EntityStage' object has no attribute 'fathertoward'
        #  兄啊 都是程序控制的 怎么可能会让stage把父亲变成儿子呢(悲) 2023.8.11
        self.fathertoward = -1
        # motherstage.fathertoward
        
        self.name = name

        self.clear_info()
        
        
        self.pos=pos
        self.hitbox=hitbox
        self.parts_stack=parts_stack
        self.quick_bias=point(self.hitbox.x/2,0)
        self.active=False
    def update_info(self):
        self.clear_info()
        for part in self.parts_stack:
            for rename, resnum in part.resource.items():
                self.resource[rename] += resnum
            for powname, pownum in part.power.items():
                self.power[powname] += pownum
            
            if 'Thruster' in part.type:
                self.thrust+=part.thrust

            if 'Pod' in part.type:
                # 还需要检查pod的开机条件，上面也是，不写了
                self.controlable = True
            self.mass += part.mass
            self.cost += part.cost
    def draw(self,scr,bias):
        for lpart in self.parts_stack:
            lpart.draw(scr,bias-self.quick_bias-self.pos)
    
    def handle_resource_requirement(self,reqments):
        ''' 注意 应该在检查资源总量后再操作 不然可能会白白减去资源'''
        for part in self.parts_stack:
            for name,value in reqments.items():
                if value<=0 or name not in part.resource:
                    continue
                if part.resource[name]<=0:
                    continue
                if part.resource[name]<=value:
                    reqments[name]-=part.resource[name]
                    part.resource[name]=0
                    self.resource[name]-=part.resource[name]
                else:
                    part.resource[name]-=reqments[name]
                    reqments[name]=0
                    self.resource[name]-=reqments[name]
        return reqments
    def update(self,tick,rocket,part):
        for lpart in self.parts_stack:
            lpart.update(tick,rocket,part,self)



class Space:
    def __init__(self):
        pass
    def get_atmosphere(self,height):
        pass
    def get_grativy_vel(self,height):
        pass
    def draw(self,scr,bias):
        pass
    
    

# 10m/s2 10m/2500tick2 0.004m/tick2 0.04 gameunit/tick2
class Earthspace(Space):
    def check_recored(self,rocket):
        #print(resmanager.SaveResourceDomain)
        for medal in resmanager.DefResourceDomain.get_resource('medal.earthspace'):
            if medal['type']=='height':
                if not resmanager.SaveResourceDomain.get_resource('medals').get(medal['name'],False) and abs(rocket.pos.y)>=medal['height']:
                    resmanager.SaveResourceDomain.get_resource('medals').update({medal['name']:medal})
                    resmanager.SaveResourceDomain.resource['science_points_total']+=medal['science_points']
                    fast_print(resmanager.NameResourceDomain.get_resource(medal['info']))
        # 
        if abs(rocket.pos.y)>=699900:
            get_world().eventrunner.trigger('finale')
    def get_atmosphere(self,height):
        if height<=200000: #20000m
            return 1-3e-6*height
        elif height<=700000:
            return 0.48-4e-7*height
        else:
            return 0
    def get_grativy_vel(self,height):
        return 0.04*((500000/(500000+height))**2)
    def draw(self,scr,bias):
        try:
            scr.blit(resmanager.DefResourceDomain.get_resource('texture.space.earth_space').subsurface(pg.Rect((0,5400-abs(bias.y)/700000*5400),(800,600))),(0,0))
        except:
            get_world().eventrunner.trigger('finale')




sgn=lambda x:0 if x==0 else (1 if x>0 else -1)
CRASH=22



class EntityLiving_Rocket(EntityLiving):
    def __init__(self,pos,mainstage,space=Earthspace()):
        self.pos=pos
        self.stages={}
        self.parts=[]
        self.connects={}

        self.mainstage = mainstage
        self.clear()
        self.part_clear()
        self.clear_info()
        
        self.engine_valve = 1
        self.space=space
        # build ghost entiy
        temp=Entity(pos=point(0,0), boxpos=point(0,0), boxrect=point(0,0), deep=0, defname=None, showdeep=0)
        temp.draw=space.draw
        get_world().engine.images_line.append(temp)
        super().__init__(pos, boxpos=point(0,0), boxrect=point(30,120), deep=0, defname='', showdeep=0)
    def clear(self):
        
        def how_stupid_i_am(stage,RT):
            return (
                (None if not stage.left_child else (RT[stage.left_child[0].name],stage.left_child[1])),
                (None if not stage.right_child else (RT[stage.right_child[0].name],stage.right_child[1])),
                (None if not stage.up_child else (RT[stage.up_child[0].name],stage.up_child[1])),
                (None if not stage.down_child else (RT[stage.down_child[0].name],stage.down_child[1]))
                )
        def stage_warper(nowstage,last_hitbox,start_pos=point(0,0)):
            ret_dict={}
            #lparts,hitbox=draw_stage(nowstage)
            #ret_dict.append(EntityStage(start_pos,hitbox,lparts))
            if nowstage.left_child:
                temp = nowstage.left_child[0]
                lparts,hitbox = draw_stage(temp)
                new_pos = start_pos - point(hitbox.x,0)
                
                rettemp=stage_warper(temp,hitbox,new_pos)
                ret_dict.update(rettemp)
                ret_dict.update({temp.name:EntityStage(new_pos,hitbox,lparts,
                                                       *how_stupid_i_am(temp,rettemp),temp.name)})
            
            if nowstage.right_child:
                temp = nowstage.right_child[0]
                lparts,hitbox=draw_stage(temp)
                new_pos=start_pos+point(last_hitbox.x,0)
                
                rettemp=stage_warper(temp,hitbox,new_pos)
                ret_dict.update(rettemp)
                ret_dict.update({temp.name:EntityStage(new_pos,hitbox,lparts,
                                                       *how_stupid_i_am(temp,rettemp),temp.name)})
            
            if nowstage.up_child:
                temp = nowstage.up_child[0]
                lparts,hitbox = draw_stage(nowstage.up_child[0])
                new_pos=start_pos-point(0,hitbox.y)
                
                rettemp=stage_warper(temp,hitbox,new_pos)
                ret_dict.update(rettemp)
                ret_dict.update({temp.name:EntityStage(new_pos,hitbox,lparts,
                                                       *how_stupid_i_am(temp,rettemp),temp.name)})
            
            if nowstage.down_child:
                temp = nowstage.down_child[0]
                lparts,hitbox = draw_stage(temp)
                new_pos = start_pos + point(0,last_hitbox.y)
                
                rettemp=stage_warper(temp,hitbox,new_pos)
                ret_dict.update(rettemp)
                ret_dict.update({temp.name:EntityStage(new_pos,hitbox,lparts,
                                                       *how_stupid_i_am(temp,rettemp),temp.name)})

            return ret_dict
        self.living_parts=[]
        if not self.stages:
            mlparts,mhitbox=draw_stage(self.mainstage)
            self.stages.update(stage_warper(self.mainstage,mhitbox,point(0,0)))
            self.stages.update({self.mainstage.name:EntityStage(point(0,0),mhitbox,mlparts,*how_stupid_i_am(self.mainstage,self.stages),self.mainstage.name)})
        else:
            pass
    def part_clear(self):
        # 清算剩余部件
        self.connects={}
        # 开始DFS遍历
        def stage_warper(nowstage):
            #硬链接为整体，分离器就分开
            # 递归和循环都有
            sep_list=[]
            part_list=[]
            part_stack=[]
            hard_avail=[nowstage]
            temp_stages={}
            while hard_avail:
                nowpart=hard_avail.pop(0)
                part_stack.append(nowpart)
                temp_stages.update({nowpart.name:nowpart})
                for _child in (nowpart.left_child,nowpart.right_child,nowpart.up_child,nowpart.down_child):
                    if _child:
                        connecttype=_child[1]
                        if connecttype==HARDCONNECT:
                            hard_avail.append(_child[0])
                        elif connecttype==SEPARATOR:
                            temp,temp2=stage_warper(_child[0])
                            part_list.extend(temp)
                            # 孩子-》父亲 分离用
                            temp_stages.update(temp2)
                            self.connects.update({_child[0].name:nowpart.name})
            part_list.append(RocketPart(part_stack))
            
            return part_list,temp_stages
        self.parts,TS = stage_warper(self.stages[self.mainstage.name])
        self.main_part = self.parts[-1]
        return TS
    def clear_info(self):
        
        self.resource = {'LiquidFuel':0,'SolidFuel': 0, 'Electricity': 0}
        # 除了引擎开机时这么消耗
        self.power = {'SolidFuel':0,'LiquidFuel': 0, 'Electricity': 0}
        self.resource_consumption = self.resource.copy()
        # #上面的东西都没有用
        self.mass = 0
        self.thrust = 0
    def update_info(self):
        # 正常情况下不应该用这个函数
        for part in self.parts:
            part.update_info()

    def update(self,tick):
        for part in self.parts:
            part.update(tick,self)
            
        
        # 计算vel
        world=get_world()
        world.engine.camera_pos+=smoothmove(world.engine.camera_pos,get_centre_u(self.pos-point(0,140),point(0,0)-world.window),1)
        # 下面用来看资源总量
        self.clear_info()
        for part in self.parts:
            part.update_info()
            self.mass+=part.mass
            for item,value in part.resource.items():
                self.resource[item]+=value
            for item,value in part.power.items():
                self.power[item]+=value
            for item,value in part.resource_consumption.items():
                self.resource_consumption[item] += value
            self.thrust+=part.thrust
        self.vel.y-=(self.thrust/self.mass)
        #if self.lasttick+150<=tick:
            #self.lasttick=tick
            #fast_print(' '.join((str(round(self.pos.y/10,1))+'m',str(abs(round(self.vel.y*2,2)))+'m/s')))
        self.pos+=self.vel
        self.space.check_recored(self)
    def draw(self,scr,bias):
        #self.space.draw(scr,bias)
        for name,living in self.stages.items():
            living.draw(scr,bias-self.pos)
    def onnothitflag(self):
        #print(self.space.get_grativy_vel(self.pos.y))
        self.vel.y+=self.space.get_grativy_vel(abs(self.pos.y))
        self.vel.y-=(self.space.get_atmosphere(self.pos.y)*0.0007*self.vel.y**2)*sgn(self.vel.y)/self.mass
    def onhited(self,hit,nhp,wayp,hittype):
        if -self.vel.y>=CRASH:
            pass
    def get_attitude(self):
        return self.pos.y/10
    def get_realvel(self):
        # 注意 单位是m/s 不是m/tick FPS=50
        return -(self.vel.y/10*50)