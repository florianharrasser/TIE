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
from daten import file
import contour_utils as cont_utils


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, mainWindow, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(111)
        self.file=file
        self.main_window=mainWindow
        super(MplCanvas, self).__init__(fig)

    def with_selector(self):
        self.RS = RectangleSelector(self.axes, self.line_select_callback,
                                    useblit=True,
                                    button=[1, 3],
                                    minspanx=5, minspany=5,
                                    spancoords='pixels',
                                    interactive=True)
        plt.connect('key_press_event', self.toggle_selector)

        return self
    
    def with_draw(self):
        self.drawing = False
        self.CS=Cursor(self.axes, useblit=True)
        self.CS.connect_event('button_press_event', self.on_press)
        self.CS.connect_event('button_release_event', self.on_release)
        self.CS.connect_event('motion_notify_event', self.on_motion) 
 
    def on_release(self, event):
        if event.button==1:
            self.drawing=False
            cont_utils.select_contour()
            self.draw_selected_contour_with_colorbar('To get the Mass hit \'Calculate Contour Mass\'', True, enable_colorbar=False)        
                 
    def on_press(self, event):
        if event.button == 1:
            self.drawing = True
            file.draw_x=[]
            file.draw_y=[]
            self.draw_selected_contour_with_colorbar('Draw a contour', False, enable_colorbar=False)
            self.file.draw_x.append(event.xdata)
            self.file.draw_y.append(event.ydata)
    
    def on_motion(self, event):        
        if self.drawing and event.xdata is not None and event.ydata is not None:
            self.file.draw_x.append(event.xdata)
            self.file.draw_y.append(event.ydata)
            self.axes.scatter(self.file.draw_x, self.file.draw_y, color='red', s=3, marker='o')  
            self.draw()

    def line_select_callback(self, eclick, erelease):
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)

        # sets the values for x and y, which is important for the statistic feature
        if x1>x2:
            x1,x2=x2,x1

        if y1>y2:
            y1,y2=y2,y1

        # Assign sorted values to file attributes
        self.file.x1, self.file.y1 = x1, y1
        self.file.x2, self.file.y2 = x2, y2

        self.main_window.btn_calculate_FFT.setEnabled(True)
        self.main_window.btn_calculate_TV.setEnabled(True)
        self.main_window.txt_axial_separation.setEnabled(True)
        self.main_window.txt_axial_separation_high.setEnabled(True)
        self.main_window.btn_calculate_US.setEnabled(True)
        self.main_window.btn_calculate_FFT_mixing.setEnabled(True)
    
    def toggle_selector(self, event):
        if event.key in ['Q', 'q'] and self.RS.active:
            self.RS.set_active(False)
        if event.key in ['A', 'a'] and not self.RS.active:
            self.RS.set_active(True)

    def show_image(self, title, image):
        self.axes.clear()       
        self.axes.imshow(image, cmap=matplotlib.cm.gray, interpolation='nearest')
        self.axes.set_title(title)
        self.axes.set_xlabel(r'Pixel')
        self.axes.set_ylabel(r'Pixel')
        scalebar_lenght=1*file.pixel_size*1e6
        scalebar = ScaleBar(scalebar_lenght, "um", location='lower right', frameon=False, color='white')
        self.axes.add_artist(scalebar)
        self.draw()

    #Draw contours in heatmap
    def draw_default_contour_heatmap(self,contour, contour_index, title, contour_bool, colorbar_bool=True):
        self.axes.clear()
        image_with_contours = file.opd_dry_mass.copy()
        if contour_bool:
            cv2.drawContours(image_with_contours, contours=contour, contourIdx=contour_index, color=np.max(self.file.opd_dry_mass), thickness=2, lineType=cv2.LINE_AA)

        fig=self.axes.imshow(image_with_contours, cmap='viridis')
        self.axes.set_title(title)        

        if colorbar_bool:
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

    def draw_contour_with_colorbar(self, title, contour_bool):
        self.draw_default_contour_heatmap(file.contours,file.selected_contour_index,title, contour_bool)

    def draw_selected_contour_with_colorbar(self, title, contour_bool, enable_colorbar=True):
        self.draw_default_contour_heatmap(file.selected_contour,0,title, contour_bool, enable_colorbar)

    #Draw contours in raw image    
    def draw_default_contour_raw_image(self, contour,contour_idx,title, contour_bool):
        self.axes.clear()
        image_with_contours = file.raw_image.copy()
        if contour_bool:
            cv2.drawContours(image_with_contours, contours=contour, contourIdx=contour_idx, color=200, thickness=2, lineType=cv2.LINE_AA)

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

    def draw_inflated_contour_with_colorbar(self, title, contour_bool):
        self.draw_default_contour_heatmap(file.contour_inflated,0,title, contour_bool)

    def draw_inflated_contour(self, title, contour_bool):
        self.draw_default_contour_raw_image(file.contour_inflated,0,title,contour_bool)
        
    def draw_stored_contour(self, title, contour_bool):
        self.draw_default_contour_raw_image(file.stored_contour,0,title,contour_bool)
        
    def draw_contour(self, title, contour_bool):
        self.draw_default_contour_raw_image(file.contours,file.selected_contour_index,title,contour_bool)

    def save_figure(self, path):
            self.figure.savefig(path+".png")

    def evaluation(self, data, title):
        self.axes.clear()
        x_points = np.arange(len(data))

        self.axes.scatter(x_points, data)

        self.axes.grid(alpha=0.2)
        self.axes.set_xlabel('Cell')
        self.axes.set_ylabel('Mass/Area in ng/um^2')
        self.axes.set_title(title)

        self.draw()