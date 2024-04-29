import sys
import csv
from daten import Daten
from setting_window import SettingWindow
from select_window import SelectWindow
from evaluation_window import EvaluationWindow
import calculation as calc
from readlif.reader import LifFile
import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QFileDialog,
    QLabel, QGridLayout, QToolBar, QLineEdit, QSlider, QMessageBox, QFrame
    )
from PyQt6.QtGui import QAction
from  MplCanvas import MplCanvas
from PyQt6.QtCore import Qt


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIE Calculation")
        self.setGeometry(100, 100, 600, 400)
        self.showMaximized()
        self.toolBar=QToolBar()
        self.addToolBar(self.toolBar)
        self.page_layout = QGridLayout()
        self.parameter_layout=QGridLayout()

        self.page_layout.addLayout(self.parameter_layout,0,0)

        self.file = Daten()

        self.mc1=MplCanvas(self.file, self, False, False, width=5, height=4, dpi=100)
        self.mc2=MplCanvas(self.file, self, False, False, width=5, height=4, dpi=100)
        self.mc3=MplCanvas(self.file, self, False, False, width=5, height=4, dpi=100)

        self.btn_open_dialog = QAction("Upload file")
        self.btn_open_dialog.triggered.connect(self.open_dialog)
        self.toolBar.addAction(self.btn_open_dialog)

        self.btn_save_file =QAction("Save file")
        self.btn_save_file.setDisabled(True)
        self.btn_save_file.triggered.connect(self.save_file)
        self.toolBar.addAction(self.btn_save_file)

        self.btn_show_select_window = QAction("Image stack")
        self.btn_show_select_window.setDisabled(True)
        self.btn_show_select_window.triggered.connect(self.show_select_window)
        self.toolBar.addAction(self.btn_show_select_window)

        self.btn_show_setting_window = QAction("Settings")
        self.btn_show_setting_window.triggered.connect(self.show_setting_window)
        self.toolBar.addAction(self.btn_show_setting_window)


        self.btn_show_evaluation_window=QAction("Evaluation")
        self.btn_show_evaluation_window.triggered.connect(self.show_evaluation_window)
        self.toolBar.addAction(self.btn_show_evaluation_window)


        self.lbl_filename=QLabel("Current File: None")
        self.lbl_filename.setToolTip("This is the name of the selected image")
        self.lbl_focused_image=QLabel("Index focused image: 0")
        self.lbl_focused_image.setToolTip("This is the index of the focused image")
        self.lbl_OPL_low=QLabel("Index OPL low:")
        self.txt_OPL_low=QLineEdit()
        self.txt_OPL_low.setToolTip("Enter the index value for calculation using the OPL method")
        self.txt_OPL_low.setFixedSize(30,30)
        self.txt_OPL_low.setText(str(self.file.OPL_idx_low))
        self.lbl_OPL_high=QLabel("Index OPL high:")
        self.txt_OPL_high=QLineEdit()
        self.txt_OPL_high.setToolTip("Enter the index value for calculation using the OPL method")
        self.txt_OPL_high.setFixedSize(30,30)
        self.txt_OPL_high.setText(str(self.file.OPL_idx_high))
        self.lbl_mass_total=QLabel("Mass total in ng: 0")
        self.lbl_mass_total.setToolTip("This is the mass calculated for the whole image")
        self.lbl_mass_inside=QLabel("Mass inside contour in ng: 0")
        self.lbl_mass_inside.setToolTip("This is the mass calculated inside the selected contour")
        self.lbl_mass_contour_mean=QLabel("Contour mean in ng: 0")
        self.lbl_mass_contour_mean.setToolTip("This is the mean mass directly on the contour")
        self.lbl_mass_contour_effective=QLabel("<b>Contour effective in ng: 0</b>")
        self.lbl_mass_contour_effective.setToolTip("This is the effective mass inside the contour normalised")

        self.btn_calculate_OPL=QPushButton("Calculate OPL")
        self.btn_calculate_OPL.setToolTip("Use calculation option with FFT")
        self.btn_calculate_OPL.setDisabled(True)
        self.btn_calculate_OPL.clicked.connect(self.show_OPL_plot)

        self.btn_calculate_with_tvnorm=QPushButton("Calculate with TV Norm ")
        self.btn_calculate_with_tvnorm.setToolTip("Use calculation option with regularisation")
        self.btn_calculate_with_tvnorm.setDisabled(True)
        self.btn_calculate_with_tvnorm.clicked.connect(self.show_OPL_plot_tv)

        frame1=QFrame()
        frame1.setStyleSheet("QFrame { background-color: lightgray; border: 2px lightgray; border-radius: 10px;}")
        frame1_layout=QGridLayout(frame1)
        frame1_layout.addWidget(self.lbl_filename,0,0)
        frame1_layout.addWidget(self.lbl_focused_image,1,0)
        frame1_layout.addWidget(self.lbl_mass_total,0,1, alignment=Qt.AlignmentFlag.AlignLeft)
        frame1_layout.addWidget(self.lbl_mass_inside,0,1,alignment=Qt.AlignmentFlag.AlignRight)
        frame1_layout.addWidget(self.lbl_mass_contour_mean, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        frame1_layout.addWidget(self.lbl_mass_contour_effective, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.parameter_layout.addWidget(frame1,0,0,2,3)

        frame2=QFrame()
        frame2.setStyleSheet("QFrame { background-color: lightgray; border: 2px lightgray; border-radius: 10px;}")
        frame2_layout=QGridLayout(frame2)
        frame2_layout.addWidget(self.lbl_OPL_low, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        frame2_layout.addWidget(self.txt_OPL_low, 0, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        frame2_layout.addWidget(self.lbl_OPL_high, 1, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        frame2_layout.addWidget(self.txt_OPL_high, 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        frame2_layout.addWidget(self.btn_calculate_OPL, 0, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        frame2_layout.addWidget(self.btn_calculate_with_tvnorm, 1, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.parameter_layout.addWidget(frame2, 2, 0, 2, 3)

        self.page_layout.addWidget(self.mc1,0,1)
        self.page_layout.addWidget(self.mc2,1,0)
        self.page_layout.addWidget(self.mc3,1,1)

        frame3=QFrame()
        frame3.setStyleSheet("QFrame { background-color: lightgray; border: 2px lightgray; border-radius: 10px;}")
        frame3_layout=QGridLayout(frame3)

        self.sld_find_contour_tresh = QSlider()
        self.sld_find_contour_tresh.setOrientation(Qt.Orientation.Horizontal)
        self.sld_find_contour_tresh.setMinimum(1)
        self.sld_find_contour_tresh.setMaximum(250)
        self.sld_find_contour_tresh.setDisabled(True)
        self.sld_find_contour_tresh.valueChanged.connect(self.treshhold_detection)
        self.sld_find_contour_tresh.setFixedSize(500,30)
        self.sld_find_contour_tresh.setToolTip("Refine the threshold to precisely identify contours in your image")
        self.lbl_find_contour_tresh=QLabel("Treshhold: 0")
        frame3_layout.addWidget(self.lbl_find_contour_tresh,0,0,1,3,alignment=Qt.AlignmentFlag.AlignHCenter)
        frame3_layout.addWidget(self.sld_find_contour_tresh,1,1,1,1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.btn_find_contour_tresh_down=QPushButton("<")
        self.btn_find_contour_tresh_down.setFixedSize(30,30)
        self.btn_find_contour_tresh_down.setDisabled(True)
        self.btn_find_contour_tresh_down.clicked.connect(self.find_contour_tresh_down)
        frame3_layout.addWidget(self.btn_find_contour_tresh_down,1,0)
        self.btn_find_contour_tresh_up=QPushButton(">")
        self.btn_find_contour_tresh_up.setFixedSize(30,30)
        self.btn_find_contour_tresh_up.setDisabled(True)
        self.btn_find_contour_tresh_up.clicked.connect(self.find_contour_tresh_up)
        frame3_layout.addWidget(self.btn_find_contour_tresh_up,1,2)


        self.sld_find_contour = QSlider()
        self.sld_find_contour.setOrientation(Qt.Orientation.Horizontal)
        self.sld_find_contour.setMinimum(-1)
        self.sld_find_contour.setMaximum(10)
        self.sld_find_contour.setValue(-1)
        self.sld_find_contour.setDisabled(True)
        self.sld_find_contour.valueChanged.connect(self.contour_detection)
        self.sld_find_contour.setFixedSize(500,30)
        self.sld_find_contour.setToolTip("Use this slider to choose the right contour")
        self.lbl_find_contour=QLabel("Contour Nr.: 0")
        frame3_layout.addWidget(self.lbl_find_contour,2,0,1,3,alignment=Qt.AlignmentFlag.AlignHCenter)
        frame3_layout.addWidget(self.sld_find_contour,3,1,1,1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.btn_find_contour_down=QPushButton("<")
        self.btn_find_contour_down.setFixedSize(30,30)
        self.btn_find_contour_down.setDisabled(True)
        self.btn_find_contour_down.clicked.connect(self.find_contour_down)
        frame3_layout.addWidget(self.btn_find_contour_down,3,0)
        self.btn_find_contour_up=QPushButton(">")
        self.btn_find_contour_up.setFixedSize(30,30)
        self.btn_find_contour_up.setDisabled(True)
        self.btn_find_contour_up.clicked.connect(self.find_contour_up)
        frame3_layout.addWidget(self.btn_find_contour_up,3,2)

        self.sld_scale = QSlider()
        self.sld_scale.setOrientation(Qt.Orientation.Horizontal)
        self.sld_scale.setMinimum(50)
        self.sld_scale.setMaximum(150)
        self.sld_scale.setDisabled(True)
        self.sld_scale.setValue(100)
        self.sld_scale.setFixedSize(500,30)
        self.sld_scale.setToolTip("Use this slider to adjust the scale of the contour")
        self.sld_scale.valueChanged.connect(self.show_scaled_contours)
        self.lbl_scale=QLabel("Scale: 1")
        frame3_layout.addWidget(self.lbl_scale,4,0,1,3,alignment=Qt.AlignmentFlag.AlignHCenter)
        frame3_layout.addWidget(self.sld_scale,5,1,1,1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.btn_scale_down=QPushButton("<")
        self.btn_scale_down.setFixedSize(30,30)
        self.btn_scale_down.setDisabled(True)
        self.btn_scale_down.clicked.connect(self.scale_down)
        frame3_layout.addWidget(self.btn_scale_down,5,0)
        self.btn_scale_up=QPushButton(">")
        self.btn_scale_up.setFixedSize(30,30)
        self.btn_scale_up.setDisabled(True)
        self.btn_scale_up.clicked.connect(self.scale_up)
        frame3_layout.addWidget(self.btn_scale_up,5,2)
        self.parameter_layout.addWidget(frame3,4,0,3,3)

        self.btn_show_background=QPushButton("BG")
        self.btn_show_background.setToolTip("Show the Background")
        self.btn_show_background.setFixedSize(30,30)
        self.btn_show_background.setDisabled(True)
        self.btn_show_background.clicked.connect(self.show_background)
        self.page_layout.addWidget(self.btn_show_background, 0,2, alignment=Qt.AlignmentFlag.AlignTop)

        self.btn_show_raw_image=QPushButton("IM")
        self.btn_show_raw_image.setToolTip("Show the Image")
        self.btn_show_raw_image.setFixedSize(30,30)
        self.btn_show_raw_image.setDisabled(True)
        self.btn_show_raw_image.clicked.connect(self.show_raw_image)
        self.page_layout.addWidget(self.btn_show_raw_image, 0,2, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_show_stack=QPushButton("ST")
        self.btn_show_stack.setToolTip("Show the Stack")
        self.btn_show_stack.setFixedSize(30,30)
        self.btn_show_stack.setDisabled(True)
        self.btn_show_stack.clicked.connect(self.show_stack)
        self.page_layout.addWidget(self.btn_show_stack, 0,2, alignment=Qt.AlignmentFlag.AlignBottom)

        self.btn_draw_contour_yourself=QPushButton("Draw Contour by hand")
        self.btn_draw_contour_yourself.setToolTip("Hit this button to draw the contour by yourself")
        self.btn_draw_contour_yourself.setDisabled(True)
        self.btn_draw_contour_yourself.clicked.connect(self.draw_contour_yourself)
        self.page_layout.addWidget(self.btn_draw_contour_yourself, 3,0, alignment=Qt.AlignmentFlag.AlignLeft)

        self.btn_select_contour=QPushButton("Select Contour")
        self.btn_select_contour.setToolTip("Hit this button to choose the drawn points as contour")
        self.btn_select_contour.setDisabled(True)
        self.btn_select_contour.clicked.connect(self.select_contour)
        self.page_layout.addWidget(self.btn_select_contour, 3,0,alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_delete_contour=QPushButton("Delete drawn Contour")
        self.btn_delete_contour.setToolTip("Delete the drawn contourpoints")
        self.btn_delete_contour.setDisabled(True)
        self.btn_delete_contour.clicked.connect(self.delete_contour)
        self.page_layout.addWidget(self.btn_delete_contour, 3,0,alignment=Qt.AlignmentFlag.AlignRight)

      
        widget = QWidget()
        widget.setLayout(self.page_layout)
        self.setCentralWidget(widget)

    def open_dialog(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "LIF Files (*.lif)")
            
            if path: self.file.file=LifFile(path)            
            if self.file.file==None: raise Exception('Invalid input: No file selected. Please select a file.')
            
            #Settings for 'Setting_Window' and display it
            self.setting_window = SettingWindow(self)
            lifProperties = []    
            self.file.uploaded_files=[]        

            for idx, entry in enumerate(self.file.file.image_list):
                lifProperties.append(f"Index: {idx:<5}Name:{entry['name']:<60}Dimensions: {str(entry['dims']):<40}")
                self.file.uploaded_files.append(entry['name'])
                self.setting_window.lbl_status.setText("\n".join(lifProperties))

            self.setting_window.show()
            # self.file.filename=""
            # #extracting the filename from path
            # for i in range (len(path)-5, -1, -1):
            #     if(path[i] == '/'): 
            #         break                
            #     self.file.filename=self.file.filename+path[i]     

            # self.file.filename = self.file.filename[::-1] #reversing the filename
            # self.lbl_filename.setText("Current file: "+self.file.filename)
            self.lbl_mass_total.setText("Mass total in ng: 0")
            self.lbl_mass_inside.setText("Mass inside cont. in ng: 0")
            self.lbl_mass_contour_mean.setText("Contour mean in ng: 0")
            self.lbl_mass_contour_effective.setText("<b>Contour effective in ng: 0</b>")
        except Exception as e:
            self.error_message(e)

    def save_file(self):
        try:
            if self.file.filename=="": raise Exception ('Error: No file to save! Please ensure that there is a file to save before proceeding.')
            file_name = file_name = self.file.filename.replace('/', '-')
            path, _ = QFileDialog.getSaveFileName(self, "Save File",file_name, " csv Files (*.csv) ;; Text Files (*.txt)") #str(self.file.filename)
            if path:
                self.mc1.save_figure(path[:-4]+'(rawfile)')
                self.mc2.save_figure(path[:-4]+'(drymass)')
                self.mc3.save_figure(path[:-4]+'(selectedpart)')
                        
                with open(path, 'w') as file:
                    csv_writer = csv.writer(file)
                    csv_writer.writerow(["magnification",self.file.magnification])
                    csv_writer.writerow(["pixel Size in m",self.file.pixel_size])
                    csv_writer.writerow(["axial stepin m",self.file.axial_step])
                    csv_writer.writerow(["alpha",self.file.alpha])
                    csv_writer.writerow(["lbda_TV",self.file.lbda_TV])
                    csv_writer.writerow(["calculation option", self.file.calulation])
                    csv_writer.writerow(["index infocus image",self.file.idx_focused_image])
                    csv_writer.writerow(["index low OPL",self.file.OPL_idx_low])       
                    csv_writer.writerow(["index high OPL",self.file.OPL_idx_high])
                    csv_writer.writerow(["index background", self.file.idx_background])
                    csv_writer.writerow(["index sample", self.file.idx_sample])
                    csv_writer.writerow(["mass total image in ng",self.file.drymass_ent])
                    csv_writer.writerow(["mass inside contour in ng",self.file.drymass_contour])
                    csv_writer.writerow(["mass on contour in ng", self.file.contour_outer_mean])
                    csv_writer.writerow(["mass effective in ng", (self.file.drymass_contour-self.file.contour_outer_mean)])
                    csv_writer.writerow(["Area of contour in um^2", self.file.contour_area])
                    csv_writer.writerow(["contour area", self.file.area])
                    csv_writer.writerow(["number contour", self.file.contour_nr])
                    csv_writer.writerow(["treshhold", self.file.treshhold])
                    csv_writer.writerow(["scalefactor", self.file.scalefactor])                    
                    csv_writer.writerow(["x1",self.file.x1])
                    csv_writer.writerow(["x2",self.file.x2])
                    csv_writer.writerow(["y1",self.file.y1])
                    csv_writer.writerow(["y2",self.file.y2])

            else: raise Exception('Error: Wrong path. Please provide a valid path.')
        except Exception as e:
            self.error_message(e)

    def show_setting_window(self):
        self.setting_window = SettingWindow(self)            
        lifProperties = []

        if(self.file.file==None): 
            self.setting_window.lbl_status.setText("No file uploaded")
        else:
            for idx, entry in enumerate(self.file.file.image_list):
                lifProperties.append(f"Index: {idx:<5}Name:{entry['name']:<60}Dimensions: {str(entry['dims']):<40}")

            self.setting_window.lbl_status.setText("\n".join(lifProperties))
        
        self.setting_window.show()

    def show_select_window(self):
        self.select_window = SelectWindow(self.file, self, len(self.file.sample))
        self.select_window.value_changed(self.file.idx_focused_image)
        self.select_window.show()

    def show_evaluation_window (self):
        self.evaluation_window=EvaluationWindow()
        self.evaluation_window.show()

    def show_background(self):
            self.layout().removeWidget(self.mc1)
            self.mc1=MplCanvas(self.file, self, True, False, width=5, height=4, dpi=100)
            self.page_layout.addWidget(self.mc1,0,1)   
            self.mc1.show_focused_image('Background Idx 1', self.file.pixel_size, self.file.background[1])

    def show_raw_image(self):
        self.layout().removeWidget(self.mc1)
        self.mc1=MplCanvas(self.file, self, True, False,  width=5, height=4, dpi=100)
        self.page_layout.addWidget(self.mc1,0,1)   
        self.mc1.show_focused_image('Sample Idx 1', self.file.pixel_size, self.file.sample[1])

    def show_stack(self):
        self.layout().removeWidget(self.mc1)
        self.mc1=MplCanvas(self.file, self, True, False, width=5, height=4, dpi=100)
        self.page_layout.addWidget(self.mc1,0,1)   
        self.mc1.show_focused_image('Stack Idx 1', self.file.pixel_size, self.file.stack[1])

    def _show_OPL_plot_default(self, mixing_OPL):
        try:
            self.file.draw_x=[]
            self.file.draw_y=[]
            self.lbl_mass_total.setText("Mass total in ng: 0")
            self.lbl_mass_inside.setText("Mass inside cont. in ng: 0")
            self.lbl_mass_contour_mean.setText("Contour mean in ng: 0")
            self.lbl_mass_contour_effective.setText("<b>Contour effective in ng: 0</b>")

            if(int(self.txt_OPL_low.text())>int(self.txt_OPL_high.text())): 
                raise Exception('Invalid input: The value of OPL-low cannot be greater than OPL-high. Please ensure that OPL-low is less than or equal to OPL-high.')
            if(int(self.txt_OPL_low.text())==0 or int(self.txt_OPL_high.text())==0 or self.file.alpha==0): 
                raise Exception('Invalid input: The index (IDX) of OPL cannot be zero. Please provide a non-zero value for the index of OPL.')
            
            self.file.OPL_idx_low, self.file.OPL_idx_high = int(self.txt_OPL_low.text()), int(self.txt_OPL_high.text())
            mixing_OPL()
            calc.calculate_drymass_entire(self.file)
            
            self.contour_detection()

            self.enable_all_buttons()
            self.enable_all_slider()
            self.btn_save_file.setEnabled(True)
        except Exception as e:
            self.error_message(e)

    def show_OPL_plot(self):
        self._show_OPL_plot_default(lambda: calc.mixing(self.file))
        self.file.calulation="FFT"
    
    def show_OPL_plot_tv(self):
        self._show_OPL_plot_default(lambda: calc.mixing_tv(self.file))
        self.file.calulation="Tv Norm"        

    def validate_input_for_calculation_drymass(self):
        return (self.txt_OPL_low.text()=='' or
            self.txt_OPL_high.text() =='' or
            int(self.txt_OPL_low.text())<0 or
            int(self.txt_OPL_low.text())+self.file.idx_focused_image>=len(self.file.sample) or
            int(self.txt_OPL_high.text())<0 or
            int(self.txt_OPL_high.text())+self.file.idx_focused_image>=len(self.file.sample))

    def treshhold_detection(self):
        self.file.treshhold=self.sld_find_contour_tresh.value()
        self.lbl_find_contour_tresh.setText("Treshhold: "+str(self.file.treshhold))
        self.file.contours, self.file.hierarchy = calc.contour_detection(self.file.opd_dry_mass, treshhold=self.sld_find_contour_tresh.value())
        self.contour_detection()

    def contour_detection(self):
        self.file.contours, self.file.hierarchy = calc.contour_detection(self.file.opd_dry_mass, treshhold=self.sld_find_contour_tresh.value())
        self.file.contour_nr=self.sld_find_contour.value()
        self.lbl_find_contour.setText("Contour Nr.: "+str(self.file.contour_nr))
        self.lbl_find_contour_tresh.setText("Treshhold: "+str(self.file.treshhold))
        self.sld_find_contour.setMaximum(len(self.file.hierarchy)-1)        

        self.sld_scale.setValue(100)
        if self.sld_find_contour.value()!=-1:
            self.sld_scale.setEnabled(True)
        else:
            self.sld_scale.setDisabled(True)
        self.plot_contours()
 
    def plot_contours(self):
        self.layout().removeWidget(self.mc2)
        self.mc2=MplCanvas(self.file, self, False, False, width=5, height=4, dpi=100)
        self.page_layout.addWidget(self.mc2,1,0)
        title='Mass:'+str(round(self.file.drymass_contour,3))+' ng'
        self.mc2.draw_contours_with_colorbar( title,self.file.opd_dry_mass, self.file.contours, self.sld_find_contour.value(), True)

        self.layout().removeWidget(self.mc3)
        self.mc3=MplCanvas(self.file, self,False, False, width=5, height=4, dpi=100)
        self.page_layout.addWidget(self.mc3,1,1)
        self.mc3.draw_contour('selected Part',self.file.raw_image, self.file.contours, self.sld_find_contour.value(), True)

    def error_message(self, message):
        QMessageBox.critical(self, "Error!", str(message), buttons=QMessageBox.StandardButton.Close,)

    def draw_contour_yourself(self):
        self.layout().removeWidget(self.mc2)
        self.mc2=MplCanvas(self.file, self, False, True, width=5, height=4, dpi=100)
        self.page_layout.addWidget(self.mc2,1,0)
        title='Mass:'+str(round(self.file.drymass_contour,3))+' ng'
        self.mc2.draw_contours_with_colorbar( title,self.file.opd_dry_mass, self.file.contours, self.sld_find_contour.value(), False)
        
        self.layout().removeWidget(self.mc3)
        self.mc3=MplCanvas(self.file, self,False, True, width=5, height=4, dpi=100)
        self.page_layout.addWidget(self.mc3,1,1)
        self.mc3.draw_contour('selected Part',self.file.raw_image, self.file.contours, self.sld_find_contour.value(), False)

    def select_contour(self):
        try:
            self.file.contours=calc.select_contour(self.file.draw_x, self.file.draw_y, self.file.contours)
   
            if self.file.draw_x!=[]:
                self.sld_find_contour.valueChanged.disconnect()
                self.sld_find_contour.setValue(0)
                self.sld_find_contour.valueChanged.connect(self.contour_detection)


                #self.plot_contours()
                self.file.contour_nr=0
                self.btn_find_contour_down.setDisabled(True)
                self.btn_find_contour_up.setDisabled(True)
                self.sld_find_contour.setDisabled(True)
                self.btn_find_contour_tresh_down.setDisabled(True)
                self.btn_find_contour_tresh_up.setDisabled(True)
                self.sld_find_contour_tresh.setDisabled(True)
            
            self.show_scaled_contours()

        except Exception as e:
            self.error_message(e)
    
    def delete_contour (self):
        self.contour_detection()
        self.enable_all_slider()
        self.enable_all_buttons()
        self.file.draw_x=[]
        self.file.draw_y=[]
        
        # self.layout().removeWidget(self.mc2)
        # self.mc2=MplCanvas(self.file, self, False, True, width=5, height=4, dpi=100)
        # self.page_layout.addWidget(self.mc2,1,0)
        # title='Mass:'+str(round(self.file.drymass_contour,3))+' ng'
        # self.mc2.draw_contours_with_colorbar( title,self.file.opd_dry_mass, self.file.contours, self.sld_find_contour.value(), False)
        
        # self.layout().removeWidget(self.mc3)
        # self.mc3=MplCanvas(self.file, self,False, True,width=5, height=4, dpi=100)
        # self.page_layout.addWidget(self.mc3,1,1)
        # self.mc3.draw_contour('selected Part',self.file.raw_image, self.file.contours, self.sld_find_contour.value(), False)

    def display_mass(self):            
        self.file.scalefactor=self.sld_find_contour.value()/100
        self.file.contour_scaled=[]
        self.file.contour_scaled.append(calc.scale_contour(self.file.contours[self.sld_find_contour.value()], self.sld_scale.value()/100))
        print(self.file.contour_scaled)
        self.file.drymass_contour, outside = calc.contour_mass(self.file, self.file.contour_scaled[0])
        self.file.contour_outer_mean=calc.contour_mean(self.file, self.file.contour_scaled[0])
        self.lbl_scale.setText("Scale: "+str(self.sld_scale.value()/100))
        self.lbl_mass_total.setText("Mass total in ng: "+str(self.file.drymass_ent))
        self.lbl_mass_inside.setText("Mass inside cont. in ng: "+str(self.file.drymass_contour))
        self.lbl_mass_contour_mean.setText("Contour mean in ng: "+str(self.file.contour_outer_mean))
        effective_mass =self.file.drymass_contour-self.file.contour_outer_mean
        calc.calculate_contour_area(self.file, self.file.contours[self.file.contour_nr])
        self.lbl_mass_contour_effective.setText("<b>Contour effective in ng: </b>"+str(round(effective_mass,5)))

    def show_scaled_contours(self):
        self.display_mass()
        effective_mass =self.file.drymass_contour-self.file.contour_outer_mean
        self.layout().removeWidget(self.mc2)
        self.mc2=MplCanvas(self.file, self, False, False, width=5, height=4, dpi=100)
        self.page_layout.addWidget(self.mc2,1,0)
        title='Mass:'+str(round(effective_mass,4))+' ng'
        self.mc2.draw_contours_with_colorbar(title ,self.file.opd_dry_mass, self.file.contour_scaled, 0, True)

        self.layout().removeWidget(self.mc3)
        self.mc3=MplCanvas(self.file, self, False, False, width=5, height=4, dpi=100)
        self.page_layout.addWidget(self.mc3,1,1)
        self.mc3.draw_contour('Selected Part',self.file.raw_image, self.file.contour_scaled, 0, True)

    def find_contour_tresh_up(self):
        self.sld_find_contour_tresh.setValue(self.sld_find_contour_tresh.value()+1)
    
    def find_contour_tresh_down(self):
        self.sld_find_contour_tresh.setValue(self.sld_find_contour_tresh.value()-1)

    def find_contour_up(self):
        self.sld_find_contour.setValue(self.sld_find_contour.value()+1)
    
    def find_contour_down(self):
        self.sld_find_contour.setValue(self.sld_find_contour.value()-1)
    
    def scale_down(self):
        self.sld_scale.setValue(self.sld_scale.value()-1)

    def scale_up(self):
        self.sld_scale.setValue(self.sld_scale.value()+1)
    
    def enable_all_buttons(self):
        for button in self.findChildren(QPushButton):
            button.setEnabled(True)
    
    def disable_all_buttons(self):
        for button in self.findChildren(QPushButton):
            button.setDisabled(True)
    
    def enable_all_slider(self):
        for sld in self.findChildren(QSlider):
            if(sld==self.sld_scale): continue
            sld.setEnabled(True)

    def disable_all_slider(self):
        for sld in self.findChildren(QSlider):
            sld.setDisabled(True)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = Main()
    main_gui.show()
    sys.exit(app.exec())