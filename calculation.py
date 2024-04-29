import numpy as np
import cv2
from tie_admm import TIE_ADMM
from scipy.optimize import curve_fit
import blur_image

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

def mixing(file):
    sigma=1
    OPL_lo=calculate_phase(file, file.OPL_idx_low, True)
    OPL_hi=calculate_phase(file, file.OPL_idx_high, False)

    gaussian2D = lambda x, y, sigma: np.exp(-((x)**2/(2*sigma**2) + (y)**2/(2*sigma**2)))

    Nx,Ny = OPL_lo.shape
    x = np.arange(Nx) - np.floor(Nx/2)
    y = np.arange(Ny) - np.floor(Ny/2)
    Y,X = np.meshgrid(y,x)

    LP_filt = np.fft.ifftshift(gaussian2D(X,Y,sigma))
       
    F_hi = np.fft.fft2(OPL_hi)
    F_lo = np.fft.fft2(OPL_lo)

    F_mix = LP_filt * F_lo + (1-LP_filt) * F_hi
    
    file.OPL_mixed = np.real(np.fft.ifft2(F_mix))

def calculate_background_sample_stack(file):        
    bg_container = file.file.get_image(file.idx_background) #idx 3 should be the bg images z-stack
    sample_container = file.file.get_image(file.idx_sample) #idx 1 should be the sample images z-stack

    file.sample = np.asarray([np.asarray(i) for i in sample_container.get_iter_z(t=0, c=0)])
    file.background = np.asarray([np.asarray(i) for i in bg_container.get_iter_z(t=0, c=0)])
    file.stack = file.sample/file.background
    find_focused_image(file)

def calculate_phase(file, m:int, bool):
    if bool:
        file.selected_stack = file.stack[:,file.y1:file.y2,file.x1:file.x2].copy()
        file.raw_image=file.sample[1][file.y1:file.y2,file.x1:file.x2].copy()

    n1 = file.idx_focused_image - m
    n2 = file.idx_focused_image + m 

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

    eps = 1e-4 #to avoid division by zero
    F_Psi = np.fft.fft2(dI)/(-(Kx**2 + Ky**2) - eps)
    Psi = np.real(np.fft.ifft2(F_Psi))
    gx, gy = np.gradient(Psi)
    tmp = divergence((gx/I0), (gy/I0))/file.pixel_size**2  #divide by ux**2 to account for the units!
    
    #solving the laplace equation via fft:
    F_OPL = np.fft.fft2(tmp)/(-(Kx**2 + Ky**2) - eps)
    OPL = np.real(np.fft.ifft2(F_OPL))
    OPL -= np.min(OPL)
    OPL= np.fft.ifftshift(OPL)*1e9
    return OPL

def divergence(gx,gy):
    return (np.gradient(gx)[0] + np.gradient(gy)[1])

def calculate_drymass_entire(file):
    outer_slab = 2
    pm = 1
    OPD_dry_mass = pm*file.OPL_mixed[:,:].copy()

    #remove residual offsets by substacting mean of outer pixeles in area of interest
    outer_slab = 2 #thickness to consider 
    outer_mean = np.mean([OPD_dry_mass[0:outer_slab,:].mean(),OPD_dry_mass[-outer_slab:-1,:].mean(),
                          OPD_dry_mass[:,0:outer_slab].mean(),OPD_dry_mass[:,-outer_slab:-1].mean()])

    OPD_dry_mass -= outer_mean

    sigma = OPD_dry_mass/file.alpha
    mass = np.sum(sigma)*file.pixel_size**2 #dry mass in gramm


    file.drymass_ent= np.round(mass,5)
    file.drymass_ent_mean=np.round((outer_mean/file.alpha)*file.pixel_size**2 ,5)
    file.opd_dry_mass = OPD_dry_mass.astype(np.float64)

def contour_detection(image, treshhold):
    img_gray = image.astype(np.uint8).copy()
    ret, thresh = cv2.threshold(img_gray, treshhold, maxval=np.amax(image), type=cv2.THRESH_BINARY_INV)
    contour, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    file_contour = []
    file_hierarchy = []
    # return contour, hierarchy

    for i, cont in enumerate(contour):
        area=cv2.contourArea(cont) 
        if (area> 3000):
            file_contour.append(cont)
            file_hierarchy.append(hierarchy[0][i])

    return file_contour, file_hierarchy

def canny_edge_detection(image, low_treshhold, high_treshhold, sigma, low_treshhold_e, high_treshhold_e):
    img=image.copy()
    blurred_image = blur_image.GaussianBlur(img, sigma)
    edges = cv2.Canny(blurred_image.astype(np.uint8),low_treshhold, high_treshhold)
    (thresh, blackEdges) = cv2.threshold(edges, low_treshhold_e, high_treshhold_e, cv2.THRESH_BINARY_INV)
    return edges, blackEdges

def scale_contour(contour, scale):
    
    M = cv2.moments(contour)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    contour_norm = contour - [cx, cy]
    contour_scaled = contour_norm * scale
    contour_scaled = contour_scaled + [cx, cy]

    return contour_scaled.astype(np.int32) 

def contour_mass(file, contour):
    contours=[]
    contours.append(contour)
    #creating a mask
    mask=np.zeros(file.OPL_mixed.shape, np.uint8)
    file.contour_mask = np.zeros(file.raw_image.shape, np.float64)
    mask.fill(255)

    cv2.drawContours(mask, contours, 0, (0,30,0), thickness=5)
    cv2.floodFill(mask, None, (0,0), 80)
    cv2.floodFill(mask, None, (len(mask[0])-1,0), 80)
    cv2.floodFill(mask, None, (0,len(mask)-1), 80)
    cv2.floodFill(mask, None, (len(mask[0])-1, len(mask)-1), 80)

    mass_inside=0
    mass_outside=0

    for i in range(len(file.OPL_mixed[0])):
        for j in range(len(file.OPL_mixed)):
            if mask[j][i]==255:
                file.contour_mask[j][i]=file.opd_dry_mass[j][i]
                mass_inside= mass_inside+(file.opd_dry_mass[j][i])
            else:
                mass_outside=mass_outside+(file.opd_dry_mass[j][i])

    mass_inside=np.round((mass_inside/file.alpha)*file.pixel_size**2, 5)
    mass_outside=np.round((mass_outside/file.alpha)*file.pixel_size**2, 5)
    return mass_inside, mass_outside

def contour_mean(file, contour):
        contours=[]
        contours.append(contour)
        mask=file.raw_image.copy()
        cv2.drawContours(mask, contours, 0, 255)

        outer_mean=0

        for i in range(len(file.raw_image[0])):
            for j in range(len(file.raw_image)):
                if mask[j][i]==255:
                    outer_mean = outer_mean+file.OPL_mixed[j][i]
        
        return np.round(outer_mean/file.alpha*file.pixel_size**2,5)

def calculate_with_tvnotm(file, m:int, bool):
        if bool:
            file.selected_stack = file.stack[:,file.y1:file.y2,file.x1:file.x2].copy()
            file.raw_image=file.sample[file.idx_focused_image][file.y1:file.y2,file.x1:file.x2].copy()

        n_img,nx,ny=file.selected_stack.shape
        n1 = file.idx_focused_image - m
        n2 = file.idx_focused_image + m
        I1 = file.selected_stack[n1]
        I2 = file.selected_stack[n2]
        dI_dz = -(I1 - I2)/np.abs(n2-n1)
        tm = TIE_ADMM(nx,ny)
        result = tm.solve_tie(dI_dz, maxiter=file.iteration, lambda_tv=file.lbda_TV)
        return result*file.axial_step/file.pixel_size

def select_contour(x, y, input_contour):
    if(x ==[] or y==[]): return input_contour
    select_contour = [np.column_stack((x, y)).reshape((-1, 1, 2)).astype(np.int32)]
    return select_contour
    # for i in range(len(file.draw_x)):
    #     file.contours.append([file.draw_x[i], file.draw_y[i]])

def calculate_contour_area(file, cont):
    contour_area=cv2.contourArea(cont)
    file.contour_area=contour_area*(file.pixel_size*1e6)**2


def mixing_tv(file):
    sigma=1
    OPL_lo=calculate_with_tvnotm(file, file.OPL_idx_low, True)
    OPL_hi=calculate_with_tvnotm(file, file.OPL_idx_high, False)

    gaussian2D = lambda x, y, sigma: np.exp(-((x)**2/(2*sigma**2) + (y)**2/(2*sigma**2)))

    Nx,Ny = OPL_lo.shape
    x = np.arange(Nx) - np.floor(Nx/2)
    y = np.arange(Ny) - np.floor(Ny/2)
    Y,X = np.meshgrid(y,x)

    LP_filt = np.fft.ifftshift(gaussian2D(X,Y,sigma))
       
    F_hi = np.fft.fft2(OPL_hi)
    F_lo = np.fft.fft2(OPL_lo)

    F_mix = LP_filt * F_lo + (1-LP_filt) * F_hi
    
    file.OPL_mixed = np.real(np.fft.ifft2(F_mix))
