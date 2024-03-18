import numpy as np
import cv2
from tie_admm import TIE_ADMM
from scipy.optimize import curve_fit



def find_focused_image(file):
    stack = file.sample/file.background 
    gaussian = lambda x, x0, sigma: np.exp(-(x-x0)**2/(2*sigma**2))
    width = []
    bins = 100

    for m in range(len(stack)):
        H, bin_edges = np.histogram(stack[m], bins = bins)
        popt, _ = curve_fit(gaussian, np.arange(len(H)), H/H.max(), p0 = [np.argmax(H), 10])
        width.append(popt[1])

    focus_idx = np.argmin(width)
    return focus_idx


def calculate_background_sample(file, idx_background, idx_sample):        
    bg_container = file.file.get_image(idx_background) #idx 3 should be the bg images z-stack
    sample_container = file.file.get_image(idx_sample) #idx 1 should be the sample images z-stack

    file.sample = np.asarray([np.asarray(i) for i in sample_container.get_iter_z(t=0, c=0)])
    file.background = np.asarray([np.asarray(i) for i in bg_container.get_iter_z(t=0, c=0)])

def calculate_phase(file):
    file.OPL = None
    file.stack = None

    file.stack = file.sample/file.background 
    stack = file.stack[:,file.x1:file.x2, file.y1:file.y2].copy()

   
    #%% choose images from stack
    m1 = -1
    m2 = 2
    n1 = file.idx_focused_image + m1
    n2 = file.idx_focused_image + m2 

    dz = np.abs(n2-n1) * file.axial_step
    
    rows = slice(0,stack.shape[1])
    cols = slice(0,stack.shape[2])

    row_shift = 1
    col_shift = 0
    I0 = np.roll(np.roll(np.fft.ifftshift(stack[n1][rows, cols]), row_shift, axis=0), col_shift, axis = 1)
    I1 = np.fft.ifftshift(stack[n2][rows, cols])
    Nx,Ny = I0.shape    

    dI = -(I0 - I1)/dz #axial intensity gradient estimate
    kx = 2*np.pi*np.fft.fftfreq(Nx, file.camera_increment)
    ky = 2*np.pi*np.fft.fftfreq(Ny, file.camera_increment)
    Kx, Ky = np.meshgrid(ky,kx)

    eps = 1e-4 #to avoid division by zero
    F_Psi = np.fft.fft2(dI)/(-(Kx**2 + Ky**2) - eps)
    Psi = np.real(np.fft.ifft2(F_Psi))
    gx, gy = np.gradient(Psi)
    tmp = divergence((gx/I0), (gy/I0))/file.camera_increment**2  #divide by ux**2 to account for the units!
    
    #solving the laplace equation via fft:
    F_OPL = np.fft.fft2(tmp)/(-(Kx**2 + Ky**2) - eps)
    OPL = np.real(np.fft.ifft2(F_OPL))
    OPL -= np.min(OPL)
    file.OPL = np.fft.ifftshift(OPL)*1e9
    file.OPL = file.OPL.astype(np.float64)

def divergence(gx,gy):
    return (np.gradient(gx)[0] + np.gradient(gy)[1])


def calculate_drymass(file, alpha):
    outer_slab = 2
    pm = 1
    #pm = 1 #if its the negative instead of posititve set to -1, otherwise to 1
    OPD_dry_mass = pm*file.OPL[:,:].copy() #in nm

    #remove residual offsets by substacting mean of outer pixeles in area of interest
    #outer_slab = 2 #thickness to consider 
    outer_mean = np.mean([OPD_dry_mass[0:outer_slab,:].mean(),OPD_dry_mass[-outer_slab:-1,:].mean(),
                          OPD_dry_mass[:,0:outer_slab].mean(),OPD_dry_mass[:,-outer_slab:-1].mean()])
    print('mean in outer slab of OPD = %.2f'%outer_mean)
    OPD_dry_mass -= outer_mean

    # alpha = 0.190 * 1e-6 #m^3/g  #standard value
    sigma = OPD_dry_mass/alpha
    mass = np.sum(sigma)*file.camera_increment**2 #dry mass in gramm

    print("dry mass = ",  np.round(mass,3), "ng")
    file.opd_dry_mass = OPD_dry_mass

def contour_detection(file):
   
    file.image = cv2.cvtColor(file.image[:, :, :3], cv2.COLOR_RGBA2BGR)
    file.image_copy = file.image.copy()
    img_gray = cv2.cvtColor(file.image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)

    #contour detection
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
    file.contours = contours
    file.hierarchy = hierarchy


def calculate_with_tvnotm(file):
        file.stack = file.sample/file.background
        n_img,nx,ny=file.stack.shape
        n1 = file.idx_focused_image + file.m1
        n2 = file.idx_focused_image + file.m2
        I1 = file.stack[n1]
        I2 = file.stack[n2]
        dI_dz = -(I1 - I2)/np.abs(n2-n1)
        tm = TIE_ADMM(nx,ny)
        lbda_TV = 1e-5
        result = tm.solve_tie(dI_dz, maxiter=1000, lambda_tv=lbda_TV)
        file.OPL = result *file.axial_step/file.camera_increment
        file.OPL = file.OPL.astype(np.float32) #np.float64 not availabe, change to float32 -> should be changed

