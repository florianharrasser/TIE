import sys
import csv
from daten import Daten
from setting_window import SettingWindow
from select_window import SelectWindow
import calculation as calc
from readlif.reader import LifFile
import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QFileDialog,
    QVBoxLayout, QLabel, QGridLayout, QToolBar, QLineEdit, QSlider, QMessageBox
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
        self.box_layout=QVBoxLayout()

        self.file = Daten()

        self.mc1=MplCanvas(self.file, self, False, width=5, height=4, dpi=100)
        self.mc2=MplCanvas(self.file, self, False, width=5, height=4, dpi=100)
        self.mc3=MplCanvas(self.file, self, False, width=5, height=4, dpi=100)
        self.mc4=MplCanvas(self.file, self, False, width=5, height=4, dpi=100)

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

        self.btn_calculate_mass=QPushButton("Calculate mass")
        self.btn_calculate_mass.setDisabled(True)
        self.btn_calculate_mass.clicked.connect(self.show_scaled_contours)

        self.lbl_OPL_low=QLabel("Index OPL low:")
        self.txt_OPL_low=QLineEdit()
        self.txt_OPL_low.setText(str(self.file.OPL_idx_low))
        self.lbl_OPL_high=QLabel("Index OPL high:")
        self.txt_OPL_high=QLineEdit()
        self.txt_OPL_high.setText(str(self.file.OPL_idx_high))
        self.lbl_filename=QLabel("Current File: None")
        self.lbl_focused_image=QLabel("Index focused image: 0")
        self.txt_OPL_high.setFixedWidth(30)
        self.txt_OPL_low.setFixedWidth(30)
        self.lbl_mass_total=QLabel("Mass total [ng]: 0")
        self.lbl_mass_inside=QLabel("Mass inside [ng]: 0")
        self.lbl_mass_outside=QLabel("Mass outside [ng]: 0")

        self.page_layout.addWidget(self.lbl_OPL_low,2,0,1,1)
        self.page_layout.addWidget(self.txt_OPL_low,2,1,1,1)
        self.page_layout.addWidget(self.lbl_OPL_high,3,0,1,1)               
        self.page_layout.addWidget(self.txt_OPL_high,3,1,1,1)

        self.page_layout.addWidget(self.lbl_filename,0,0,1,2, alignment=Qt.AlignmentFlag.AlignTop)
        self.page_layout.addWidget(self.lbl_focused_image,1,0,1,1, alignment=Qt.AlignmentFlag.AlignTop)
        self.page_layout.addWidget(self.btn_calculate_mass,5,0,1,2)
        self.page_layout.addWidget(self.lbl_mass_total,6,0,1,2)#, alignment=Qt.AlignmentFlag.AlignTop)
        self.page_layout.addWidget(self.lbl_mass_inside,7,0,1,2)#, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.page_layout.addWidget(self.lbl_mass_outside,8,0,1,2)#, alignment=Qt.AlignmentFlag.AlignBottom)



        self.btn_calculate_OPL=QPushButton("Calculate OPL")
        self.btn_calculate_OPL.setDisabled(True)
        self.btn_calculate_OPL.clicked.connect(self.show_OPL_plot)
        self.page_layout.addWidget(self.btn_calculate_OPL,4,1,1,1)#, alignment=Qt.AlignmentFlag.AlignRight)

        self.btn_calculate_with_tvnorm=QPushButton("Calculate with TV Norm ")
        self.btn_calculate_with_tvnorm.setFixedWidth(160)
        self.btn_calculate_with_tvnorm.setDisabled(True)
        self.btn_calculate_with_tvnorm.clicked.connect(self.show_OPL_plot_tv)
        self.page_layout.addWidget(self.btn_calculate_with_tvnorm,4,0,1,1)#, alignment=Qt.AlignmentFlag.AlignLeft)

        self.page_layout.addWidget(self.mc1,0,2,7,1)
        self.page_layout.addWidget(self.mc2,0,3,7,1)
        self.page_layout.addWidget(self.mc3,10,2,7,1)
        self.page_layout.addWidget(self.mc4,10,3,7,1)

        self.page_layout.setRowStretch(0, 1)  # Row with mc1 and mc2
        self.page_layout.setRowStretch(7, 1)  # Row with mc3 and mc4


        self.sld_find_contour_tresh = QSlider()
        self.sld_find_contour_tresh.setOrientation(Qt.Orientation.Vertical)
        self.sld_find_contour_tresh.setMinimum(1)
        self.sld_find_contour_tresh.setMaximum(250)
        self.sld_find_contour_tresh.setDisabled(True)
        self.sld_find_contour_tresh.valueChanged.connect(self.contour_detection)
        self.lbl_find_contour_tresh=QLabel("T: 0")
        self.page_layout.addWidget(self.sld_find_contour_tresh,1,4,5,1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.page_layout.addWidget(self.lbl_find_contour_tresh,7,4,alignment=Qt.AlignmentFlag.AlignLeft)
        self.btn_find_contour_tresh_up=QPushButton("^")
        self.btn_find_contour_tresh_up.setFixedSize(20,20)
        self.btn_find_contour_tresh_up.setDisabled(True)
        self.btn_find_contour_tresh_up.clicked.connect(self.find_contour_tresh_up)
        self.page_layout.addWidget(self.btn_find_contour_tresh_up,0,4,alignment=Qt.AlignmentFlag.AlignLeft)
        self.btn_find_contour_tresh_down=QPushButton("v")
        self.btn_find_contour_tresh_down.setFixedSize(20,20)
        self.btn_find_contour_tresh_down.setDisabled(True)
        self.btn_find_contour_tresh_down.clicked.connect(self.find_contour_tresh_down)
        self.page_layout.addWidget(self.btn_find_contour_tresh_down,6,4,alignment=Qt.AlignmentFlag.AlignLeft)


        self.sld_find_contour = QSlider()
        self.sld_find_contour.setOrientation(Qt.Orientation.Vertical)
        self.sld_find_contour.setMinimum(-1)
        self.sld_find_contour.setMaximum(10)
        self.sld_find_contour.setValue(-1)
        self.sld_find_contour.setDisabled(True)
        self.sld_find_contour.valueChanged.connect(self.contour_detection)
        self.lbl_find_contour=QLabel("C: 0")
        self.page_layout.addWidget(self.sld_find_contour,1,4,5,1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.page_layout.addWidget(self.lbl_find_contour,7,4,alignment=Qt.AlignmentFlag.AlignCenter)
        self.btn_find_contour_up=QPushButton("^")
        self.btn_find_contour_up.setFixedSize(20,20)
        self.btn_find_contour_up.setDisabled(True)
        self.btn_find_contour_up.clicked.connect(self.find_contour_up)
        self.page_layout.addWidget(self.btn_find_contour_up,0,4,alignment=Qt.AlignmentFlag.AlignCenter)
        self.btn_find_contour_down=QPushButton("v")
        self.btn_find_contour_down.setFixedSize(20,20)
        self.btn_find_contour_down.setDisabled(True)
        self.btn_find_contour_down.clicked.connect(self.find_contour_down)
        self.page_layout.addWidget(self.btn_find_contour_down,6,4,alignment=Qt.AlignmentFlag.AlignCenter)

        self.sld_scale = QSlider()
        self.sld_scale.setOrientation(Qt.Orientation.Vertical)
        self.sld_scale.setMinimum(0)
        self.sld_scale.setMaximum(300)
        self.sld_scale.setDisabled(True)
        self.sld_scale.setValue(100)
        self.sld_scale.valueChanged.connect(self.show_scaled_contours)
        self.lbl_scale=QLabel("Sc: 1")
        self.page_layout.addWidget(self.sld_scale,1,4,5,1, alignment=Qt.AlignmentFlag.AlignRight)
        self.page_layout.addWidget(self.lbl_scale,7,4,alignment=Qt.AlignmentFlag.AlignRight)
        self.btn_scale_up=QPushButton("^")
        self.btn_scale_up.setFixedSize(20,20)
        self.btn_scale_up.setDisabled(True)
        self.btn_scale_up.clicked.connect(self.scale_up)
        self.page_layout.addWidget(self.btn_scale_up,0,4,alignment=Qt.AlignmentFlag.AlignRight)
        self.btn_scale_down=QPushButton("v")
        self.btn_scale_down.setFixedSize(20,20)
        self.btn_scale_down.setDisabled(True)
        self.btn_scale_down.clicked.connect(self.scale_down)
        self.page_layout.addWidget(self.btn_scale_down,6,4,alignment=Qt.AlignmentFlag.AlignRight)
       
       
        self.sld_low_treshhold = QSlider()
        self.sld_low_treshhold.setOrientation(Qt.Orientation.Vertical)
        self.sld_low_treshhold.setMinimum(0)
        self.sld_low_treshhold.setMaximum(255)
        self.sld_low_treshhold.setDisabled(True)
        self.sld_low_treshhold.valueChanged.connect(self.canny_edge_detection)
        self.lbl_low_treshhold=QLabel("L:0")
        self.page_layout.addWidget(self.sld_low_treshhold,10,4,5,1,alignment=Qt.AlignmentFlag.AlignLeft)
        self.page_layout.addWidget(self.lbl_low_treshhold,16,4,alignment=Qt.AlignmentFlag.AlignLeft)
        self.btn_low_treshhold_up=QPushButton("^")
        self.btn_low_treshhold_up.setFixedSize(20,20)
        self.btn_low_treshhold_up.setDisabled(True)
        self.btn_low_treshhold_up.clicked.connect(self.low_treshhold_up)
        self.page_layout.addWidget(self.btn_low_treshhold_up,9,4,alignment=Qt.AlignmentFlag.AlignLeft )
        self.btn_low_treshhold_down=QPushButton("v")
        self.btn_low_treshhold_down.setFixedSize(20,20)
        self.btn_low_treshhold_down.setDisabled(True)
        self.btn_low_treshhold_down.clicked.connect(self.low_treshhold_down)
        self.page_layout.addWidget(self.btn_low_treshhold_down,15,4,alignment=Qt.AlignmentFlag.AlignLeft )
        

        self.sld_high_treshhold = QSlider()
        self.sld_high_treshhold.setOrientation(Qt.Orientation.Vertical)
        self.sld_high_treshhold.setMinimum(1)
        self.sld_high_treshhold.setMaximum(255)
        self.sld_high_treshhold.setDisabled(True)
        self.sld_high_treshhold.valueChanged.connect(self.canny_edge_detection)
        self.lbl_high_treshhold=QLabel("H: 0")
        self.page_layout.addWidget(self.sld_high_treshhold,10,4,5,1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.page_layout.addWidget(self.lbl_high_treshhold,16,4, alignment=Qt.AlignmentFlag.AlignCenter)
        self.btn_high_treshhold_up=QPushButton("^")
        self.btn_high_treshhold_up.setFixedSize(20,20)
        self.btn_high_treshhold_up.setDisabled(True)
        self.btn_high_treshhold_up.clicked.connect(self.high_treshhold_up)
        self.page_layout.addWidget(self.btn_high_treshhold_up,9,4,alignment=Qt.AlignmentFlag.AlignCenter )
        self.btn_high_treshhold_down=QPushButton("v")
        self.btn_high_treshhold_down.setFixedSize(20,20)
        self.btn_high_treshhold_down.setDisabled(True)
        self.btn_high_treshhold_down.clicked.connect(self.high_treshhold_down)
        self.page_layout.addWidget(self.btn_high_treshhold_down,15,4,alignment=Qt.AlignmentFlag.AlignCenter )
        

        self.sld_sigma = QSlider()
        self.sld_sigma.setOrientation(Qt.Orientation.Vertical)
        self.sld_sigma.setMinimum(1)
        self.sld_sigma.setMaximum(500)
        self.sld_sigma.setValue(100)
        self.sld_sigma.setDisabled(True)
        self.sld_sigma.valueChanged.connect(self.canny_edge_detection)
        self.lbl_sigma=QLabel("S: 0")
        self.page_layout.addWidget(self.sld_sigma,10,4,5,1, alignment=Qt.AlignmentFlag.AlignRight)
        self.page_layout.addWidget(self.lbl_sigma,16,4, alignment=Qt.AlignmentFlag.AlignRight)
        self.btn_sigma_up=QPushButton("^")
        self.btn_sigma_up.setFixedSize(20,20)
        self.btn_sigma_up.setDisabled(True)
        self.btn_sigma_up.clicked.connect(self.sigma_up)
        self.page_layout.addWidget(self.btn_sigma_up,9,4,alignment=Qt.AlignmentFlag.AlignRight )
        self.btn_sigma_down=QPushButton("v")
        self.btn_sigma_down.setFixedSize(20,20)
        self.btn_sigma_down.setDisabled(True)
        self.btn_sigma_down.clicked.connect(self.sigma_down)
        self.page_layout.addWidget(self.btn_sigma_down,15,4,alignment=Qt.AlignmentFlag.AlignRight )


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

            for idx, entry in enumerate(self.file.file.image_list):
                lifProperties.append(f"Index: {idx:<5}Name:{entry['name']:<60}Dimensions: {str(entry['dims']):<40}")
                self.setting_window.lbl_status.setText("\n".join(lifProperties))

            self.setting_window.show()
            #self.file.filename=""
            #extracting the filename from path
            for i in range (len(path)-5, -1, -1):
                if(path[i] == '/'): 
                    break
                
                self.file.filename=self.file.filename+path[i]        
            self.file.filename = self.file.filename[::-1] #reversing the filename
            self.lbl_filename.setText("Current file: "+self.file.filename)
        except Exception as e:
            self.error_message(e)

    def save_file(self):
        try:
            if self.file.filename=="": raise Exception ('Error: No file to save! Please ensure that there is a file to save before proceeding.')
            path, _ = QFileDialog.getSaveFileName(self, "Save File",str(self.file.filename), "Text Files (*.txt);; csv Files (*.csv)")
            if path:
                self.mc2.save_figure(path[:-4])
                        
                with open(path, 'w') as file:
                    csv_writer = csv.writer(file)
                    csv_writer.writerow(["magnification",self.file.magnification])
                    csv_writer.writerow(["camera increment",self.file.pixel_size])
                    csv_writer.writerow(["axial step",self.file.axial_step])
                    csv_writer.writerow(["alpha",self.file.alpha])
                    csv_writer.writerow(["index of infocus image",self.file.idx_focused_image])
                    csv_writer.writerow(["Low index for OPL calculation",self.file.OPL_idx_low])       
                    csv_writer.writerow(["High index for OPL calculation",self.file.OPL_idx_high])
                    csv_writer.writerow(["total Mass",self.file.drymass_ent])
                    csv_writer.writerow(["mass inside contour",self.file.drymass_contour])
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

    def show_raw_image(self):
            self.layout().removeWidget(self.mc1)
            self.mc1=MplCanvas(self.file, self, True, width=5, height=4, dpi=100)
            self.page_layout.addWidget(self.mc1,0,2,7,1)   
            self.mc1.show_focused_image('Raw file',self.file, 1)

    def _show_OPL_plot_default(self, mixing):
        try:
            self.set_to_startvalue()
            if(int(self.txt_OPL_low.text())>int(self.txt_OPL_high.text())): 
                raise Exception('Invalid input: The value of OPL-low cannot be greater than OPL-high. Please ensure that OPL-low is less than or equal to OPL-high.')
            if(int(self.txt_OPL_low.text())==0 or int(self.txt_OPL_high.text())==0 or self.file.alpha==0): 
                raise Exception('Invalid input: The index (IDX) of OPL cannot be zero. Please provide a non-zero value for the index of OPL.')
            self.file.OPL_idx_low, self.file.OPL_idx_high = int(self.txt_OPL_low.text()), int(self.txt_OPL_high.text())
            mixing()
            calc.calculate_drymass_entire(self.file)
            self.canny_edge_detection()
            self.contour_detection()

            self.enable_all_buttons()
            self.enable_all_slider()
            self.btn_save_file.setEnabled(True)
        except Exception as e:
            self.error_message(e)

    def show_OPL_plot(self):
        self._show_OPL_plot_default(lambda: calc.mixing(self.file))
    
    def show_OPL_plot_tv(self):
        self._show_OPL_plot_default(lambda: calc.mixing_tv(self.file))

    def validate_input_for_calculation_drymass(self):
        return (self.txt_OPL_low.text()=='' or
            self.txt_OPL_high.text() =='' or
            int(self.txt_OPL_low.text())<0 or
            int(self.txt_OPL_low.text())+self.file.idx_focused_image>=len(self.file.sample) or
            int(self.txt_OPL_high.text())<0 or
            int(self.txt_OPL_high.text())+self.file.idx_focused_image>=len(self.file.sample))

    def canny_edge_detection(self): #maybe there is some improvement with the second treshhold
            self.lbl_low_treshhold.setText("L:"+str(self.sld_low_treshhold.value()))
            self.lbl_high_treshhold.setText("H:"+str(self.sld_high_treshhold.value()))
            self.lbl_sigma.setText("S:"+str(self.sld_sigma.value()/100))

            self.file.edges,_=calc.canny_edge_detection(self.file.opd_dry_mass, self.sld_low_treshhold.value(), self.sld_high_treshhold.value(), self.sld_sigma.value()/100, 1, 255)
            
            self.layout().removeWidget(self.mc4)
            self.mc4=MplCanvas(self.file, self, False, width=5, height=4, dpi=100)
            self.page_layout.addWidget(self.mc4,10,3,7,1)
            self.mc4.draw_contour('Canny edge detection',self.file.edges, self.file.contours, self.sld_find_contour.value())

    def contour_detection(self):
            self.lbl_find_contour.setText("C:"+str(self.sld_find_contour.value()))
            self.lbl_find_contour_tresh.setText("T:"+str(self.sld_find_contour_tresh.value()))
            self.file.contours, self.file.hierarchy = calc.contour_detection(self.file.opd_dry_mass, treshhold=self.sld_find_contour_tresh.value())

            self.sld_find_contour.setMaximum(len(self.file.hierarchy)-1)

            self.sld_scale.setValue(100)
            if(self.sld_find_contour.value()!=-1):
                self.sld_scale.setEnabled(True)
                self.btn_calculate_mass.setEnabled(True)
            else:
                self.sld_scale.setDisabled(True)
                self.btn_calculate_mass.setEnabled(True)


            self.layout().removeWidget(self.mc2)
            self.mc2=MplCanvas(self.file, self, False, width=5, height=4, dpi=100)
            self.page_layout.addWidget(self.mc2,0,3,7,1)
            self.mc2.draw_contours_with_colorbar( 'OPL',self.file.opd_dry_mass, self.file.contours, self.sld_find_contour.value())

            self.layout().removeWidget(self.mc3)
            self.mc3=MplCanvas(self.file, self,False, width=5, height=4, dpi=100)
            self.page_layout.addWidget(self.mc3,10,2,7,1)
            self.mc3.draw_contour('selected Part',self.file.raw_image, self.file.contours, self.sld_find_contour.value())

            self.layout().removeWidget(self.mc4)
            self.mc4=MplCanvas(self.file, self, False, width=5, height=4, dpi=100)
            self.page_layout.addWidget(self.mc4,10,3,7,1)
            self.mc4.draw_contour('Canny edge detection',self.file.edges, self.file.contours, self.sld_find_contour.value())

    def error_message(self, message):
        QMessageBox.critical(self, "Error!", str(message), buttons=QMessageBox.StandardButton.Close,)
        
    def show_scaled_contours(self):
            self.file.contour_scaled=[]
            self.file.contour_scaled.append(calc.scale_contour(self.file.contours[self.sld_find_contour.value()], self.sld_scale.value()/100))
            self.file.drymass_contour, outside = calc.contour_mass(self.file, self.file.contour_scaled[0])
            self.lbl_scale.setText(str(self.sld_scale.value()/100))
            self.lbl_mass_total.setText("Total mass: "+str(self.file.drymass_ent))
            self.lbl_mass_inside.setText("Mass Inside: "+str(self.file.drymass_contour))
            self.lbl_mass_outside.setText("Mass Outside: "+str(outside))

            self.layout().removeWidget(self.mc2)
            self.mc2=MplCanvas(self.file, self, False, width=5, height=4, dpi=100)
            self.page_layout.addWidget(self.mc2,0,3,7,1)
            self.mc2.draw_contours_with_colorbar('OPL',self.file.opd_dry_mass, self.file.contour_scaled, 0)

            self.layout().removeWidget(self.mc3)
            self.mc3=MplCanvas(self.file, self, False, width=5, height=4, dpi=100)
            self.page_layout.addWidget(self.mc3,10,2,7,1)
            self.mc3.draw_contour('selected Part',self.file.raw_image, self.file.contour_scaled, 0)

            self.layout().removeWidget(self.mc4)
            self.mc4=MplCanvas(self.file, self, False, width=5, height=4, dpi=100)
            self.page_layout.addWidget(self.mc4,10,3,7,1)
            self.mc4.draw_contour('Canny edge detection',self.file.edges, self.file.contour_scaled, 0)

    def low_treshhold_up(self):
        self.sld_low_treshhold.setValue(self.sld_low_treshhold.value()+1)
   
    def low_treshhold_down(self):
        self.sld_low_treshhold.setValue(self.sld_low_treshhold.value()-1)

    def high_treshhold_up(self):
        self.sld_high_treshhold.setValue(self.sld_high_treshhold.value()+1)
    
    def high_treshhold_down(self):
        self.sld_high_treshhold.setValue(self.sld_high_treshhold.value()-1)
    
    def sigma_up(self):
        self.sld_sigma.setValue(self.sld_sigma.value()+1)
    
    def sigma_down(self):
        self.sld_sigma.setValue(self.sld_sigma.value()-1)

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

    def set_to_startvalue(self):
        self.sld_find_contour.setValue(-1)
        self.sld_find_contour_tresh.setValue(1)
        self.sld_high_treshhold.setValue(1)
        self.sld_low_treshhold.setValue(0)
        self.sld_scale.setValue(100)
        self.sld_sigma.setValue(100)
        self.lbl_mass_total.setText("Mass total [ng]: 0")
        self.lbl_mass_inside.setText("Mass inside [ng]: 0")
        self.lbl_mass_outside.setText("Mass outside [ng]: 0")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = Main()
    main_gui.show()
    sys.exit(app.exec())