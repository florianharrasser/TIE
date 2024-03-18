from readlif.reader import LifFile
from numpy import ndarray

class Daten():
    def __init__(self, sample: ndarray=[0], hierarchy: ndarray=[[]], file=None, path=None, magnification=60, 
                 camera_increment=104e-9, axial_step=1e-6,
                 idx_background=3, background=None,  idx_sample=1,  idx_focused_image = 0, OPL = None,
                 x1=0, y1=0, x2=0, y2=0, opd_dry_mass=None, image =None, image_copy = None, stack=None):
        
        #ausmisten welche informationen benötigt werden und welche nicht
        self.file = file
        self.path = path
        self.magnification = magnification
        self.camera_increment = camera_increment
        self.axial_step = axial_step
        #self.m = m #change the use of the m
        self.idx_background = idx_background #OK
        self.background = background
        self.idx_sample = idx_sample #OK
        self.sample = sample
        self.idx_focused_image = idx_focused_image
        self.OPL = OPL
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
        self.opd_dry_mass = opd_dry_mass
        self.image = image
        self.image_copy = image_copy
        self.stack = stack


    def loadFile(self, path):
        if(path):
            self.file = LifFile(path)    