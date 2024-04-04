import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
import matplotlib.pyplot as plt
import cv2
import inspect



class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, file, mainWindow, bool_selector,  width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.file=file
        self.main_window=mainWindow
        super(MplCanvas, self).__init__(fig)

        if (bool_selector):
            self.RS = RectangleSelector(self.axes, self.line_select_callback,
                                        useblit=True,
                                        button=[1, 3],
                                        minspanx=5, minspany=5,
                                        spancoords='pixels',
                                        interactive=True)
            plt.connect('key_press_event', self.toggle_selector)
        
    def show_focused_image(self, title, file, idx_focused_image):
        self.axes.clear()       
        self.axes.imshow(file.sample[idx_focused_image], cmap=matplotlib.cm.gray, interpolation='nearest')
        self.axes.set_title(title)
        self.draw()
    
    def show_drymass(self, title, file):
        self.axes.clear()
        self.figure = self.axes.figure
        image = self.axes.imshow(file.OPL_mixed, cmap="hsv")
        self.axes.set_title(title)
        self.axes.figure.colorbar(image, ax=self.axes)
        self.draw()

    def save_figure(self, path):
        self.figure.savefig(path+".png")

    def line_select_callback(self, eclick, erelease):
        self.file.x1, self.file.y1= int(eclick.xdata), int(eclick.ydata)        
        self.file.x2, self.file.y2= int(erelease.xdata), int(erelease.ydata)


    def toggle_selector(self, event):
        if event.key in ['Q', 'q'] and self.RS.active:
            self.RS.set_active(False)
        if event.key in ['A', 'a'] and not self.RS.active:
            self.RS.set_active(True)

    def draw_contours_with_colorbar(self,title, image, contours, contourIdx):
        self.axes.clear()
        image_with_contours = image.copy()
        cv2.drawContours(image_with_contours, contours=contours, contourIdx=contourIdx, color=np.max(self.file.opd_dry_mass), thickness=5, lineType=cv2.LINE_AA)
        fig=self.axes.imshow(image_with_contours, cmap="hsv")
        self.axes.set_title(title)
        self.axes.figure.colorbar(fig, ax=self.axes) 
        self.draw()
    
    def draw_contour(self, title, image, contour, idx):
        self.axes.clear()
        image_with_contours = image.copy()
        cv2.drawContours(image_with_contours, contours=contour, contourIdx=idx, color=200, thickness=2, lineType=cv2.LINE_AA)
        self.axes.imshow(image_with_contours)
        self.axes.set_title(title)
        self.draw()

    def show_mask_for_sum(self):
        self.axes.clear()
        self.axes.imshow(self.file.contour_mask)
        self.axes.set_title('mask')
        self.draw()
