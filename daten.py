from numpy import ndarray
from state import State
from state import FileFormat
    
class Daten():

    def __init__(self):
        
        self.reset()
    
    def reset(self):
        """saving data information"""
        self.file=None
        self.file_format:FileFormat=None
        self.filename:str="" # file.name+ name of the sample
        self.name:str="" # name of the imported .lif file
        self.calculation_option:str="" # saves the option used for calculation
        self.uploaded_files=[] #displayes the files which are into one .lif file
        self.state:State=State.DEFAULT # is for checking which contour is displayed (important for store&calculate contour)
        self.cell_index:int=0 # saves which cell is evaluated with statistic tool, part of the filename 
        self.lifProperties=['No File Uploaded']

        """Parameters for opd calculations"""
        self.magnification=60
        self.pixel_size:float=104e-9
        self.axial_step:float=1e-6
        self.alpha=0.190*1e-6
        self.lbda_TV:float=1e-5
        self.iteration:int=10
        self.idx_focused_image:int=-1
        self.idx_focused_image_calc=-1
        self.axial_separation:int=1 #Index for calculating the axial distance for opd calculations
        self.mixing_high:bool=False 

        """Parameters for selecting the right part for calculations"""
        self.idx_background=0
        self.background:ndarray=[]
        self.idx_sample=0              
        self.sample:ndarray=[]
        self.stack=None
        self.x1:int=-1 # start coordinate x for selected_stack
        self.y1:int=-1 # start coordinate y for selected_stack
        self.x2:int=-1 # end coordinate x for selected_stack
        self.y2:int=-1 # end coordinate x for selected_stack
        self.dx1=0 # shift in x direction
        self.dx2=0 # shift in x direction
        self.dy1=0 # shift in y direction
        self.dy2=0 # shift in y direction
        self.selected_stack=None # stack for calculation
        self.raw_image=None # sample image for selecting FOV for further calculations

        """Calculated masses"""
        self.opd:ndarray=None #Image as optical path delay as np.float32 array 
        self.opd_dry_mass=None #Image as optical path delay with substracted outer mean as np.float32 array
        self.entire_mass:float=0 #mass of the whole selected area/Image
        self.entire_mass_mean:float=0 # mean mass of the whole selected area/Image
        self.contour_inside_mass:float=0 # =cell mass
        self.contourline_mean_mass:float=0 # mass directly on the contour line
        self.outside_max_mass=0
        self.outside_min_mass=0
        self.outside_std=0
        self.outside_mean_mass=0

        """ Parameters for contour"""
        self.threshold:int=0 # treshold for cv2.findcontour
        self.hierarchy=[] # Hierarchy of contours
        self.contours=[] # Detected Contours with a minimum area        
        self.contour_mask=None # mask for mass calculations, array outside the cell is 0
        self.contour_inflated=[]
        self.selected_contour:ndarray=None
        self.selected_contour_index:int=0
        self.contour_area=0
        self.stored_contour=None
        self.draw_x=[] # x-values of the drawn contour
        self.draw_y=[] # x-values of the drawn contour        
        self.inflatefactor:int=1        

        """ Parameter for mixing """
        self.axial_separation_high:int=1       


    @property
    def csv_dict(self):
        return {
            "name": self.filename,
            "calculation option": self.calculation_option,
            "indexing": self.cell_index,

            "magnification": self.magnification,
            "pixel Size in m": self.pixel_size,
            "axial stepin m": self.axial_step,
            "alpha": self.alpha,
            "lbda_TV": self.lbda_TV,
            "iteration": self.iteration,
            "index infocus image": self.idx_focused_image,
            "index infocus image calculated": self.idx_focused_image_calc,
            "axial seperation": self.axial_separation,
            "axial seperation": self.axial_separation_high,
    
            "index background": self.idx_background,
            "index sample": self.idx_sample,
            "x1": self.x1,
            "x2": self.x2,
            "y1": self.y1,
            "y2": self.y2,
            "dx1":self.dx1,
            "dx2":self.dx2,
            "dy1":self.dy1,
            "dy2":self.dy2,

            "total mass image in ng": self.entire_mass,
            "mean mass image in ng": self.entire_mass_mean,
            "mass inside contour in ng": self.contour_inside_mass,
            "mean mass on contourline in ng": self.contourline_mean_mass,                        
            "mass outside max": self.outside_max_mass,
            "mass outside min":self.outside_min_mass,
            "mass outside std":self.outside_std,  
            "mass outside mean": self.outside_mean_mass, 

            "threshold": self.threshold,
            "index of contour": self.selected_contour_index,
            "area of contour in um^2": self.contour_area,
            "inflate factor": self.inflatefactor, 
        }

    def write_csv(self, csv_writer):
        
        for key, value in self.csv_dict.items():
            csv_writer.writerow([key, value])

global file
file: Daten = Daten()