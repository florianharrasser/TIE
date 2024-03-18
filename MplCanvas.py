import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
import matplotlib.pyplot as plt
import cv2



class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, file, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.file=file
        super(MplCanvas, self).__init__(fig)

        self.RS = RectangleSelector(self.axes, self.line_select_callback,
                                    useblit=True,
                                    button=[1, 3],
                                    minspanx=5, minspany=5,
                                    spancoords='pixels',
                                    interactive=True)
        plt.connect('key_press_event', self.toggle_selector)
        
    
    def check_z_position_images(self, file, idx_focused_image):
        self.axes.clear()
        if(idx_focused_image >= len(file.sample)): return len(file.sample)        
        self.axes.imshow(file.sample[idx_focused_image], cmap=matplotlib.cm.gray, interpolation='nearest')
        self.draw()
        return idx_focused_image
    
    def show_drymass(self, file):
        self.axes.clear()
        opd_float = file.opd_dry_mass.astype(np.float64)
        self.axes.imshow(opd_float, cmap="hsv")
        figure = self.axes.figure
        figure.canvas.draw()
        file.image = np.array(figure.canvas.renderer.buffer_rgba())
        self.draw()

    def line_select_callback(self, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.file.x1= int(x1)
        self.file.y1= int(y1)
        self.file.x2= int(x2)
        self.file.y2= int(y2)
        print(self.file.x1, self.file.x2, self.file.y1, self.file.y2)

    def toggle_selector(self, event):
        if event.key in ['Q', 'q'] and self.RS.active:
            self.RS.set_active(False)
        if event.key in ['A', 'a'] and not self.RS.active:
            self.RS.set_active(True)
    
    def draw_contours(self, file):
        self.axes.clear()
        image_with_contours = file.image.copy()
        cv2.drawContours(image_with_contours, contours=file.contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
        self.axes.imshow(image_with_contours)  
        self.draw()