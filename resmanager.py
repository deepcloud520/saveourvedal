import pathlib,tool,typing
import pygame as pg



def safe_pathlike(path):
    return pathlib.Path(path)



class ResourceDomain:
    def __init__(self,name=None):
        self.resource={}
        self.name=name
        self.null=None
    def add_resource(self,domain : str,res):
        self.resource.update({domain:res})
    def get_resource(self,domain : str):
        if domain not in self.resource:
            print(self.name + ': "'+domain+'" is not existed')
        return self.resource.get(domain,self.null)
    def get_resource_extra(self,domain : str):
        ass = len(domain)
        ret = {}
        for k,i in self.resource.items():
            if domain ==k[:ass]:
                ret.update({k[ass:]:i})
        return ret
    def load_resource_byfile(self,path):
        path = safe_pathlike(path)
        resource = tool.loadjson(path)
        for key,item in resource.items():
            self.add_resource(key,item)
    def load_resource_byfolder(self,path):
        path = safe_pathlike(path)
        for file in path.iterdir():
            self.load_resource_byfile(file)
    def load_resource(self,path):
        path = safe_pathlike(path)
        if path.is_file():
            self.load_resource_byfile(path)
        elif path.is_dir():
            self.load_resource_byfolder(path)
class NameResourceDomain_(ResourceDomain):
    def get_resource(self,domain : str):
        if domain not in self.resource:
            print(self.name + ': "'+domain+'" is not existed')
            return domain
        return self.resource.get(domain,self.null)
class DefResourceDomain_(ResourceDomain):
    def load_resource_byfile(self,path):
        path = safe_pathlike(path)
        loadconfig = tool.loadjson(path)
        for key,item in loadconfig[0].items():
            if len(item)==4:
                mode = item[3]
            else:
                mode=''
            
            temppath = str(pathlib.Path(path).parent / ('resource/'+item[0]))
            tempdomain = 'cache.resource.'+str(hash(temppath))
            if  tempdomain in self.resource:
                ordimage = self.get_resource(tempdomain)
            else:
                ordimage = pg.image.load(temppath).convert_alpha()
                self.add_resource(tempdomain,ordimage)
            ordimage = ordimage.subsurface(pg.Rect(*tool.point2tuple(tool.str2point(item[1])),*tool.point2tuple(tool.str2point(item[2]))))
            if '2' in mode:
                num = mode.count('2')
                for _ in range(num):
                    ordimage = pg.transform.scale2x(ordimage)

            self.add_resource(key,ordimage)
            if 'r' in mode:
                
                self.add_resource(key+'r',pg.transform.flip(ordimage,True,False).convert_alpha())
        for key,item in loadconfig[1].items():
            self.add_resource(key,item)

DefResourceDomain = DefResourceDomain_('DefResourceDomain')
NameResourceDomain = NameResourceDomain_('NameResourceDomain')
SaveResourceDomain = ResourceDomain('SaveResourceDomain')
ConfigResourceDomain = ResourceDomain('ConfigResourceDomain')
NameResourceDomain.null='illgeal domain'