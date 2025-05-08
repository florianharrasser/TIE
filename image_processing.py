import numpy as np
from daten import file
from scipy.optimize import curve_fit
from state import FileFormat

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
