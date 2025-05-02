import numpy as np
import cv2
from tie_admm import TIE_ADMM
from scipy.optimize import curve_fit
from daten import file
from state import State, FileFormat
from PIL import Image

def mixing(statistic=False):
    sigma=1
    OPL_lo=calculate_opl_fft(low=True, high=False, statistics=statistic)
    OPL_hi=calculate_opl_fft(low=False, high=True, statistics=statistic)
    gaussian2D = lambda x, y, sigma: np.exp(-((x)**2/(2*sigma**2) + (y)**2/(2*sigma**2)))
    Nx,Ny = OPL_lo.shape
    x = np.arange(Nx) - np.floor(Nx/2)
    y = np.arange(Ny) - np.floor(Ny/2)
    Y,X = np.meshgrid(y,x)
    LP_filt = np.fft.ifftshift(gaussian2D(X,Y,sigma))
       
    F_hi = np.fft.fft2(OPL_hi)
    F_lo = np.fft.fft2(OPL_lo)
    F_mix = LP_filt * F_lo + (1-LP_filt) * F_hi
    
    file.opd = np.real(np.fft.ifft2(F_mix))
    file.calculation_option="mixing"


def find_focused_image(file):    
    gaussian = lambda x, x0, sigma: np.exp(-(x-x0)**2/(2*sigma**2))
    width = []
    bins = 100

    for m in range(len(file.stack)):
        H, bin_edges = np.histogram(file.stack[m], bins = bins)
        popt, _ = curve_fit(gaussian, np.arange(len(H)), H/H.max(), p0 = [np.argmax(H), 10])
        width.append(popt[1])

    file.idx_focused_image_calc = np.argmin(width)
    file.idx_focused_image= file.idx_focused_image_calc

def find_focused_image_FOV(file):    
    gaussian = lambda x, x0, sigma: np.exp(-(x-x0)**2/(2*sigma**2))
    width = []
    bins = 100

    for m in range(len(file.selected_stack)):
        H, bin_edges = np.histogram(file.selected_stack[m], bins = bins)
        popt, _ = curve_fit(gaussian, np.arange(len(H)), H/H.max(), p0 = [np.argmax(H), 10])
        width.append(popt[1])
    print(f'foc. image selected part: {np.argmin(width)}, foc. image total stack: {file.idx_focused_image_calc}')

def calculate_background_sample_stack():
    if file.file_format==FileFormat.LIF:   
        bg_container = file.file.get_image(file.idx_background)
        sample_container = file.file.get_image(file.idx_sample)
        file.sample = np.asarray([np.asarray(i) for i in sample_container.get_iter_z(t=0, c=0)])
        file.background = np.asarray([np.asarray(i) for i in bg_container.get_iter_z(t=0, c=0)])

    file.stack = file.sample/file.background

def calculate_opl_tv(statistics=False):
    if(statistics): pass
    else:  
        file.selected_stack = file.stack[:,file.y1:file.y2,file.x1:file.x2].copy()
        file.raw_image=file.sample[file.idx_focused_image][file.y1:file.y2,file.x1:file.x2].copy()
        find_focused_image_FOV(file)

    n_img,nx,ny=file.selected_stack.shape
    n1 = file.idx_focused_image - file.axial_separation
    n2 = file.idx_focused_image + file.axial_separation
    I1 = file.selected_stack[n1]
    I2 = file.selected_stack[n2]
    dI_dz = -(I1 - I2)/np.abs(n2-n1)
    tm = TIE_ADMM(nx,ny)
    result = tm.solve_tie(dI_dz, maxiter=file.iteration, lambda_tv=file.lbda_TV)
    OPL=result*file.axial_step/file.pixel_size
    file.opd=np.array(OPL, dtype=np.float32)
    file.calculation_option="TvNorm"

def calculate_opl_US_method(statistics=False):
    def calc_phase(dI, Kx, Ky, I_max):

        k0=2*np.pi/(550*1e-9)
        kernel = np.zeros_like(Kx)
        mask = (Kx**2 + Ky**2) >= 1e-10
        kernel[mask] = -1 / (Kx[mask]**2 + Ky[mask]**2)

        F_psi = -np.fft.fft2(dI)*kernel*k0
        return np.fft.ifft2(F_psi).real/I_max
    
    def calc_dI(psi, Kx, Ky, I0):
    
        k0=2*np.pi/(550*1e-9)
        gx= np.fft.ifft2(1j*Kx*np.fft.fft2(psi)).real*I0
        gy= np.fft.ifft2(1j*Ky*np.fft.fft2(psi)).real*I0
        J=(np.fft.ifft2(1j*Kx*np.fft.fft2(gx))+np.fft.ifft2(1j*Ky*np.fft.fft2(gy))).real/k0

        return -J

    if(statistics): pass
    else:   
        file.selected_stack = file.stack[:,file.y1:file.y2,file.x1:file.x2].copy()
        file.raw_image=file.sample[1][file.y1:file.y2,file.x1:file.x2].copy()
        find_focused_image_FOV(file)

    n1 = file.idx_focused_image - file.axial_separation
    n2 = file.idx_focused_image + file.axial_separation 

    dz = np.abs(n2-n1) * file.axial_step

    I_max=np.max(file.selected_stack[file.idx_focused_image])
    I0=np.fft.ifftshift(file.selected_stack[n1])
    I1=np.fft.ifftshift(file.selected_stack[n2])
    dI=(I0-I1)/dz

    Nx,Ny = I0.shape
    kx = 2*np.pi*np.fft.fftfreq(Nx, file.pixel_size)
    ky = 2*np.pi*np.fft.fftfreq(Ny, file.pixel_size)
    Kx, Ky = np.meshgrid(ky,kx)

    dI0=dI.copy()
    psi0=0

    for i in range(50):
        psi1=calc_phase(dI0, Kx, Ky, I_max)
        dI1=calc_dI(psi1,Kx,Ky,I0)
        dI0=dI0-dI1
        psi0=psi0+psi1

    OPL=np.real(psi0)
    OPL= np.fft.ifftshift(OPL)

    file.opd=OPL*100
    file.calculation_option="US_method"


def calculate_opl_fft(low=True, high =False, statistics=False): 
    if(statistics): pass
    else:   
        file.selected_stack = file.stack[:,file.y1:file.y2,file.x1:file.x2].copy()
        file.raw_image=file.sample[1][file.y1:file.y2,file.x1:file.x2].copy()
        find_focused_image_FOV(file)

    if low:
        n1 = file.idx_focused_image - file.axial_separation
        n2 = file.idx_focused_image + file.axial_separation 

    if high:
        n1 = file.idx_focused_image-file.axial_separation_high
        n2=file.idx_focused_image+file.axial_separation_high

    dz = np.abs(n2-n1) * file.axial_step    
    rows = slice(0,file.selected_stack.shape[1])
    cols = slice(0,file.selected_stack.shape[2])

    row_shift = 1
    col_shift = 0
    I0 = np.roll(np.roll(np.fft.ifftshift(file.selected_stack[n1][rows, cols]), row_shift, axis=0), col_shift, axis = 1)
    I1 = np.fft.ifftshift(file.selected_stack[n2][rows, cols])
    Nx,Ny = I0.shape    

    dI = -(I0 - I1)/dz #axial intensity gradient estimate
    kx = 2*np.pi*np.fft.fftfreq(Nx, file.pixel_size)
    ky = 2*np.pi*np.fft.fftfreq(Ny, file.pixel_size)
    Kx, Ky = np.meshgrid(ky,kx)

    # eps = 1e-4 #to avoid division by zero

    kernel = np.zeros_like(Kx)
    mask = (Kx**2 + Ky**2) >= 1e-10
    kernel[mask] = -1 / (Kx[mask]**2 + Ky[mask]**2)
    
    F_Psi = np.fft.fft2(dI)*kernel #/(-(Kx**2 + Ky**2) - eps)
    Psi = np.real(np.fft.ifft2(F_Psi))
    gx, gy = np.gradient(Psi)
    tmp = divergence((gx/I0), (gy/I0))/file.pixel_size**2  #divide by ux**2 to account for the units!
    
    #solving the laplace equation via fft:
    F_OPL = np.fft.fft2(tmp)*kernel #/(-(Kx**2 + Ky**2) - eps)
    OPL = np.real(np.fft.ifft2(F_OPL))
    OPL -= np.min(OPL)
    OPL= np.fft.ifftshift(OPL)*1e9

    file.opd=OPL
    file.calculation_option="FFT"
    return OPL

def divergence(gx,gy):
    return (np.gradient(gx)[0] + np.gradient(gy)[1])

def opl_dry_mass():
    outer_slab = 2 #thickness to consider
    OPD_dry_mass = file.opd[:,:].copy()

    #remove residual offsets by substacting mean of outer pixeles in area of interest
    outer_mean = np.mean([OPD_dry_mass[0:outer_slab,:].mean(),OPD_dry_mass[-outer_slab:-1,:].mean(),
                          OPD_dry_mass[:,0:outer_slab].mean(),OPD_dry_mass[:,-outer_slab:-1].mean()])

    OPD_dry_mass -= outer_mean
    sigma = OPD_dry_mass/file.alpha
    mass = np.sum(sigma)*file.pixel_size**2 #dry mass in gramm

    file.opd_dry_mass = OPD_dry_mass.astype(np.float64)
    file.entire_mass_mean=np.round((outer_mean/file.alpha)*file.pixel_size**2 ,5)
    file.entire_mass= np.round(mass,5)

def contour_detection():
    img_gray = file.opd_dry_mass.astype(np.uint8).copy()
    ret, thresh = cv2.threshold(img_gray, file.threshold, maxval=np.amax(file.opd_dry_mass), type=cv2.THRESH_BINARY_INV)
    contour, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    file_contour = []
    file_hierarchy = []

    for i, cont in enumerate(contour):
        area=cv2.contourArea(cont) 
        if (area> 3000):
            file_contour.append(cont)
            file_hierarchy.append(hierarchy[0][i])

    file.contours, file.hierarchy = file_contour, file_hierarchy

def scale_contour():
    file.contour_inflated=file.contours[file.selected_contour_index]    
    M = cv2.moments(file.contour_inflated)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    contour_norm = file.contour_inflated - [cx, cy]
    contour_scaled = contour_norm * file.inflatefactor
    contour_scaled = contour_scaled + [cx, cy]
    
    file.contour_inflated=[]
    file.contour_inflated.append(contour_scaled.astype(np.int32)) 

def contour_mass():
    mass_inside=0
    mass_outside=[]
    # contours=[]    
    # contours=(file.selected_contour)

    #creating a mask
    mask=np.zeros(file.opd_dry_mass.shape, np.uint8)
    file.contour_mask = np.zeros(file.opd_dry_mass.shape, np.float64)
    mask.fill(255)

    #filling the mask
    cv2.drawContours(mask, file.selected_contour, 0, (0,30,0), thickness=5)
    cv2.floodFill(mask, None, (0,0), 80)
    cv2.floodFill(mask, None, (len(mask[0])-1,0), 80)
    cv2.floodFill(mask, None, (0,len(mask)-1), 80)
    cv2.floodFill(mask, None, (len(mask[0])-1, len(mask)-1), 80)

    #calculating the mass inside the mask
    for i in range(len(file.opd_dry_mass[0])):
        for j in range(len(file.opd_dry_mass)):
            if mask[j][i]==255:
                file.contour_mask[j][i]=file.opd_dry_mass[j][i]
                mass_inside= mass_inside+(file.opd_dry_mass[j][i])
            else:
                mass_outside.append(file.opd_dry_mass[j][i])

    file.outside_max_mass=np.max(mass_outside)
    file.outside_min_mass=np.min(mass_outside)
    file.outside_std=np.std(mass_outside)
    file.outside_mean_mass=np.mean(mass_outside)
    file.contour_inside_mass=np.round((mass_inside/file.alpha)*file.pixel_size**2, 10)

def contourline_mean_mass():
    contourline_mass=0
    
    #drawing the contour as 'mask' to iterate over it
    mask=file.opd_dry_mass.copy()
    cv2.drawContours(mask, file.selected_contour, 0, 255)        

    #calculating the mass of the contourline
    for i in range(len(file.opd_dry_mass[0])):
        for j in range(len(file.opd_dry_mass)):
            if mask[j][i]==255:
                contourline_mass += file.opd_dry_mass[j][i]

    outer_mean=contourline_mass/len(mask)#not sure about this? is it correct to calc the mean like this?

    file.contourline_mean_mass=np.round((outer_mean/file.alpha)*file.pixel_size**2,5)

#Selection of the contour based on whether the contour is drawn, scaled or predefined
def select_contour():
    if(file.state==State.DEFAULT):
        file.selected_contour=[]
        file.selected_contour.append(file.contours[file.selected_contour_index])
    elif (file.state==State.SCALED):
        file.selected_contour=[]
        file.selected_contour=file.contour_inflated
    elif file.state==State.STORED:
        file.selected_contour=file.stored_contour    
    else:
        file.selected_contour=[np.column_stack((file.draw_x, file.draw_y)).reshape((-1, 1, 2)).astype(np.int32)]
    calculate_contour_area()

def calculate_contour_area():
    contour_area=cv2.contourArea(file.selected_contour[0])
    file.contour_area=contour_area*(file.pixel_size*1e6)**2
