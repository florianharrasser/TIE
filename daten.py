from numpy import ndarray

class Daten():
    def __init__(self,  filename:str="", edges=None, sample: ndarray=[], drymass_ent:float = 0, drymass_contour:float=0,
                  magnification:float=60, drymass_outer_mean:float=0, pixel_size:float=104e-9, axial_step:float=1e-6,
                  idx_background:int=3,   idx_sample:int=1, idx_focused_image:int = -1, idx_focused_image_calc=-1, 
                  x1:int=-1, y1:int=-1, x2:int=-1, y2:int=-1, OPL_idx_low:int=1, OPL_idx_high:int=1, alpha:float=0.190 * 1e-6, 
                  iteration:int=500, OPL_mixed = None, opd_dry_mass=None, stack=None, background=None, file=None, contours=[], hierarchy = [],
                  raw_image=None,contour_mask=None, contour_scaled=[], contour_outer_mean=[], selected_stack=None, drymass_ent_mean=0, lbda_TV=1e-5):
        
        
        self.file = file
        self.filename =filename
        self.magnification = magnification
        self.pixel_size = pixel_size
        self.axial_step = axial_step
        self.idx_background = idx_background
        self.idx_sample = idx_sample
        self.background = background        
        self.sample = sample
        self.idx_focused_image = idx_focused_image
        self.idx_focused_image_calc=idx_focused_image_calc  
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
        self.OPL_mixed = OPL_mixed
        self.opd_dry_mass = opd_dry_mass
        self.stack = stack
        self.OPL_idx_low=OPL_idx_low
        self.OPL_idx_high=OPL_idx_high
        self.drymass_ent=drymass_ent
        self.drymass_contour=drymass_contour
        self.drymass_outer_mean=drymass_outer_mean
        self.edges=edges
        self.hierarchy=hierarchy
        self.contours=contours
        self.raw_image=raw_image
        self.contour_mask=contour_mask
        self.contour_scaled=contour_scaled
        self.contour_outer_mean=contour_outer_mean
        self.alpha=alpha
        self.selected_stack=selected_stack
        self.drymass_ent_mean=drymass_ent_mean
        self.lbda_TV=lbda_TV
        self.iteration=iteration