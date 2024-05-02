import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector, Cursor
import matplotlib.pyplot as plt
import cv2
from matplotlib_scalebar.scalebar import ScaleBar


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, file, mainWindow, bool_selector, bool_draw,  width=5, height=4, dpi=100):
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

        if(bool_draw):
            self.drawing = False
            self.CS=Cursor(self.axes, useblit=True)
            self.CS.connect_event('button_press_event', self.on_press)
            self.CS.connect_event('button_release_event', self.on_release)
            self.CS.connect_event('motion_notify_event', self.on_motion) 

    def on_release(self, event):
        if event.button==1:
            self.drawing=False
            
    def on_press(self, event):
        if event.button == 1:
            self.drawing = True
            self.file.draw_x.append(event.xdata)
            self.file.draw_y.append(event.ydata)
        # if event.button==3:            
        #     self.file.draw_x=[]
        #     self.file.draw_y=[]
        #     self.axes.clear()
        #     self.draw()
        #     self.drawing=False 
    
    def on_motion(self, event):        
        if self.drawing and event.xdata is not None and event.ydata is not None:
            self.file.draw_x.append(event.xdata)
            self.file.draw_y.append(event.ydata)
            self.axes.scatter(self.file.draw_x, self.file.draw_y, color='red', s=3, marker='o')  
            self.draw()

    def show_focused_image(self, title, pixel_size, image):
        self.axes.clear()       
        self.axes.imshow(image, cmap=matplotlib.cm.gray, interpolation='nearest')
        self.axes.set_title(title)
        self.axes.set_xlabel(r'Pixel')
        self.axes.set_ylabel(r'Pixel')
        scalebar_lenght=1*pixel_size*1e6
        scalebar = ScaleBar(scalebar_lenght, "um", location='lower right', frameon=False, color='white')
        self.axes.add_artist(scalebar)
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
        self.main_window.btn_calculate_OPL.setEnabled(True)
        self.main_window.btn_calculate_with_tvnorm.setEnabled(True)

    def toggle_selector(self, event):
        if event.key in ['Q', 'q'] and self.RS.active:
            self.RS.set_active(False)
        if event.key in ['A', 'a'] and not self.RS.active:
            self.RS.set_active(True)

    def draw_contours_with_colorbar(self,title, image, contours, contourIdx, contour_bool):
        self.axes.clear()
        image_with_contours = image.copy()
        if contour_bool:
            cv2.drawContours(image_with_contours, contours=contours, contourIdx=contourIdx, color=np.max(self.file.opd_dry_mass), thickness=2, lineType=cv2.LINE_AA)

        fig=self.axes.imshow(image_with_contours, cmap='viridis')
        self.axes.set_title(title)
        

        cbar=self.axes.figure.colorbar(fig, ax=self.axes)
        cbar.set_label("nm")
    
        xticks = np.round(np.array(self.axes.get_xticks()) * self.file.pixel_size*1e6,1)
        yticks = np.round(np.array(self.axes.get_yticks()) * self.file.pixel_size*1e6,1)
        self.axes.xaxis.set_major_locator(plt.FixedLocator(self.axes.get_xticks()))
        self.axes.yaxis.set_major_locator(plt.FixedLocator(self.axes.get_yticks()))
        self.axes.set_xticklabels(xticks)
        self.axes.set_yticklabels(yticks)
        self.axes.set_xlabel(r'$\mu m$')
        self.axes.set_ylabel(r'$\mu m$')

        scalebar_lenght=0.1
        scalebar = ScaleBar(scalebar_lenght, "um", location='lower right', frameon=False, color='white')
        
        self.axes.add_artist(scalebar)
        self.draw()
    
    def draw_contour(self, title, image, contour, idx, contour_bool):
        self.axes.clear()
        image_with_contours = image.copy()
        if contour_bool:
            cv2.drawContours(image_with_contours, contours=contour, contourIdx=idx, color=200, thickness=2, lineType=cv2.LINE_AA)
        self.axes.imshow(image_with_contours)
        self.axes.set_title(title)

        xticks = (np.array(self.axes.get_xticks()) + self.file.x1).astype(int)
        yticks = (np.array(self.axes.get_yticks()) + self.file.y1).astype(int)
        self.axes.xaxis.set_major_locator(plt.FixedLocator(self.axes.get_xticks()))
        self.axes.yaxis.set_major_locator(plt.FixedLocator(self.axes.get_yticks()))
        self.axes.set_xticklabels(xticks)
        self.axes.set_yticklabels(yticks)
        self.axes.set_xlabel(r'Pixel')
        self.axes.set_ylabel(r'Pixel')
        scalebar_lenght=1*self.file.pixel_size*1e6
        scalebar = ScaleBar(scalebar_lenght, "um", location='lower right', frameon=False, color='white')
        self.axes.add_artist(scalebar)
        self.draw()

    def show_mask_for_sum(self):
        self.axes.clear()
        self.axes.imshow(self.file.contour_mask)
        self.axes.set_title('mask')
        self.draw()
    
    def evaluation(self, data, title):
        self.axes.clear()
        x_points = np.arange(len(data))

        self.axes.scatter(x_points, data)

        self.axes.grid(alpha=0.2)
        self.axes.set_xlabel('Cell')
        self.axes.set_ylabel('Mass/Area in ng/um^2')
        self.axes.set_title(title)

        self.draw()

    def plot_watershed(self,image):
        self.axes.clear()
        self.axes.imshow(image)
        self.axes.set_title('watershed')
        self.draw()
