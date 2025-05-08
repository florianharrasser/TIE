
from daten import file
import cv2
import numpy as np
from state import State


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
