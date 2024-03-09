# https://pvigier.github.io/2018/06/13/perlin-noise-numpy.html
# author: prigier
# i have no idea about how to understand the perlin noise
import numpy as np
from local import get_world
from pygame import surfarray
import pygame as pg
from airiscore import EntityScreen
import typing
from tool import *
from newcoretiny import *
import resmanager

def generate_perlin_noise_2d(shape, res):
    def f(t):
        return 6*t**5 - 15*t**4 + 10*t**3

    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0],0:res[1]:delta[1]].transpose(1, 2, 0) % 1
    # Gradients
    angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    g00 = gradients[0:-1,0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g10 = gradients[1:,0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g01 = gradients[0:-1,1:].repeat(d[0], 0).repeat(d[1], 1)
    g11 = gradients[1:,1:].repeat(d[0], 0).repeat(d[1], 1)
    # Ramps
    n00 = np.sum(grid * g00, 2)
    n10 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1])) * g10, 2)
    n01 = np.sum(np.dstack((grid[:,:,0], grid[:,:,1]-1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]-1)) * g11, 2)
    # Interpolation
    t = f(grid)
    n0 = n00*(1-t[:,:,0]) + t[:,:,0]*n10
    n1 = n01*(1-t[:,:,0]) + t[:,:,0]*n11
    return np.sqrt(2)*((1-t[:,:,1])*n0 + t[:,:,1]*n1)

def generate_fractal_noise_2d(shape, res, octaves=1, persistence=0.5):
    noise = np.zeros(shape)
    frequency = 1
    amplitude = 1
    for _ in range(octaves):
        noise += amplitude * generate_perlin_noise_2d(shape, (frequency*res[0], frequency*res[1]))
        frequency *= 2
        amplitude *= persistence
    return noise

def bloom(image):
    import scipy
    start=time.time()
    image_array = surfarray.array3d(image)
    # 获得亮度图
    brightness=(image_array[:,:,0]*G +image_array[:,:,1]*B + image_array[:,:,2] * B) / ((R+G+B)*256)
    # 获得亮区
    brightarea = image_array.copy()
    brightarea[brightness <= L] = (0,0,0)
    '''
    factor = narray((8,), np.int32)
    # 卷积可分解
    last_soften = self.cloud_array.copy()
    for _ in range(ITER):
        soften = np.array(last_soften, np.int32) *factor
        soften[1:,:]  += last_soften[:-1,:] * factor
        soften[:-1,:] += last_soften[1:,:] * factor
        soften[:,1:]  += last_soften[:,:-1] * factor
        soften[:,:-1] += last_soften[:,1:] * factor
        last_soften = soften
    '''
    soften = scipy.ndimage.gaussian_filter(image_array, sigma=ITER)    
    image_array= (soften*0.5 + image_array*0.5)
    image=surfarray.make_surface(image_array)
    print("用时",(time.time()-start),'ms')
    return image



L=0.65
R=0.3
G=0.59
B=0.11
ITER=3
import time
class CloudRollRunable(Runable):
    def __init__(self,cloud : pg.Surface,entityscreen:EntityScreen):
        self.cloud = cloud
        self.entityscreen=entityscreen
    def update(self,tick,master):
        window=get_world().window
        camera=get_world().engine.camera_pos
        size=tuple2point(self.cloud.get_size())
        blit_pos= camera-self.entityscreen.hitbox.pos
        start_pos = point(camera.x*0.2+window.x*0.1,camera.y*0.2)
        self.entityscreen.image.fill((0,0,0))
        hitrect=self.entityscreen.hitbox.rect
        rect=pg.Rect(max(start_pos.x,0),max(start_pos.y,0),min(size.x-start_pos.x,window.x,hitrect.x-start_pos.x),min(size.y-start_pos.y,window.y,hitrect.y-start_pos.y))
        self.entityscreen.image.blit(self.cloud.subsurface(rect),blit_pos._intlist())
class StatImageRollRunable(Runable):
    '''状态机 {"i_0":[1000,"i_0","texture.story0_bedroom"]}'''
    def __init__(self,textures:dict,entityscreen:EntityScreen,trans_vel=0.005):
        super().__init__()
        self.textures = textures
        self.entityscreen=entityscreen
        self.frame='s'
        self.stat = 0
        self.process=0.0
        self.trans_vel=trans_vel
        self.trans_array=None
        self.left=None
        self.right=None
        self.entityscreen.image = resmanager.DefResourceDomain.get_resource(self.get_frame(self.frame)[2])
    def get_frame(self,frame):
        return self.textures[frame]
    def update(self,tick,master):
        # 我 不 是 没 有 试 过 set_alpha
        if self.lasttick == 0:
            self.lasttick=tick
        if self.stat==0:
            nowframe=self.get_frame(self.frame)
            if self.lasttick + nowframe[0] <tick:
                self.stat=1
                left=surfarray.array3d(resmanager.DefResourceDomain.get_resource(nowframe[2]))
                right=surfarray.array3d(resmanager.DefResourceDomain.get_resource(self.get_frame(nowframe[1])[2]))
                max_shape = (max(left.shape[0],right.shape[0]),max(left.shape[1],right.shape[1]),left.shape[2])
                self.left=np.zeros(max_shape)
                self.right=np.zeros(max_shape)
                self.left[:left.shape[0],:left.shape[1],:]+=left
                self.right[:right.shape[0],:right.shape[1],:]+=right
                self.lasttick = tick
        elif self.stat==1:
            if self.process<1:
                self.process+=self.trans_vel
                self.trans_array = self.left * (1-self.process) + self.right * self.process
                self.entityscreen.image = surfarray.make_surface(self.trans_array)
            else:
                self.frame=self.textures[self.frame][1]
                self.stat=0
                self.process = 0
                self.entityscreen.image = resmanager.DefResourceDomain.get_resource(self.get_frame(self.frame)[2])