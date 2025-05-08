from numpy.fft import fftfreq
import numpy as np
from daten import file

def extract_roi():
    # Extract the region of interest (ROI) from the image
    x1 = file.x1
    x2 = file.x2
    y1 = file.y1
    y2 = file.y2

    file.selected_stack = file.stack[:, y1:y2, x1:x2].copy()
    file.raw_image = file.sample[1][y1:y2, x1:x2].copy()


def compute_intensity_derivative():
    if file.mixing_high:
        n1 = file.idx_focused_image - file.axial_separation_high
        n2 = file.idx_focused_image + file.axial_separation_high
    else:
        n1 = file.idx_focused_image - file.axial_separation
        n2 = file.idx_focused_image + file.axial_separation

    I1 = file.selected_stack[n1]
    I2 = file.selected_stack[n2]
    dz = abs(n2-n1) * file.axial_step
    dI = (I1 - I2)/dz
    
    return I1 , dI

def compute_fft_meshgrid():
    _, ny, nx = file.selected_stack.shape 
    kx = 2*np.pi*fftfreq(nx, file.pixel_size)
    ky = 2*np.pi*fftfreq(ny, file.pixel_size)
    Kx, Ky = np.meshgrid(kx,ky)

    kernel = np.zeros_like(Kx)
    mask = (Kx**2 + Ky**2) >= 1e-10
    kernel[mask] = -1 / (Kx[mask]**2 + Ky[mask]**2)

    return Kx, Ky, kernel