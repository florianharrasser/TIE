from numpy import ndarray
from state import State
    
class Daten():

    def __init__(self):
        
        #self = file #file=None
        self.reset()
    
    def reset(self):
        self.file=None
        self.filename:str=""
        self.magnification=60
        self.pixel_size:float=104e-9
        self.axial_step:float=1e-6
        self.idx_background=3
        self.idx_sample=1
        self.background=None        
        self.sample:ndarray=[]
        self.idx_focused_image:int=-1
        self.idx_focused_image_calc=-1  
        self.x1:int=-1
        self.y1:int=-1
        self.x2:int=-1
        self.y2:int=-1
        self.opd:ndarray=None
        self.opd_dry_mass=None
        self.stack=None
        self.axial_separation:int=1
        self.OPL_idx_high:int=1
        self.entire_mass:float=0
        self.entire_mass_mean:float=0
        self.contour_inside_mass:float=0
        self.contourline_mean_mass:float=0
        self.edges=None
        self.hierarchy=[]
        self.contours=[]
        self.raw_image=None
        self.contour_mask=None
        self.contour_scaled=[]
        #self.contour_outer_mean:float=0
        self.alpha=0.190*1e-6
        self.selected_stack=None
        self.selected_contour=None        
        self.lbda_TV:float=1e-5
        self.iteration:int=50
        self.contour_index:int=0
        self.threshold:int=0
        self.scalefactor:int=1
        self.calculation_option:str=""
        self.draw_x=[]
        self.draw_y=[]
        self.contour_area=0
        self.uploaded_files=[]
        self.stored_contour=None
        self.recall_bool=False
        self.state:State=State.DEFAULT
    


    @property
    def csv_dict(self):
        return {
            "magnification": self.magnification,
            "pixel Size in m": self.pixel_size,
            "axial stepin m": self.axial_step,
            "alpha": self.alpha,
            "lbda_TV": self.lbda_TV,
            "calculation option": self.calculation_option,
            "index infocus image": self.idx_focused_image,
            "index low OPL": self.axial_separation,
            "index high OPL": self.OPL_idx_high,
            "index background": self.idx_background,
            "index sample": self.idx_sample,
            "mass total image in ng": self.entire_mass,
            "mass inside contour in ng": self.contour_inside_mass,
            "mass on contour in ng": self.contourline_mean_mass,
            "mass effective in ng": (self.contour_inside_mass-self.contourline_mean_mass),
            "Area of contour in um^2": self.contour_area,
            "contour index": self.contour_index,
            "threshold": self.threshold,
            "scalefactor": self.scalefactor,                    
            "x1": self.x1,
            "x2": self.x2,
            "y1": self.y1,
            "y2": self.y2
        }

    def write_csv(self, csv_writer):
        
        for key, value in self.csv_dict.items():
            csv_writer.writerow([key, value])

global file
file: Daten = Daten()