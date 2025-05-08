from daten import file
import numpy as np
import cv2


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