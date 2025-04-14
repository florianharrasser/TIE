import sys
import csv
from daten import file
from setting_window import SettingWindow
from statistics_window import StatisticWindow
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
from PyQt6.QtGui import QIntValidator
from state import State, FileFormat
import numpy as np
import multipagetiff as mtif
import tifffile as tif
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIE Calculation")
        self.showMaximized()
        self.page_layout = QGridLayout()       

        #initializing the plot fields and adding to the page layout
        self.mc1=MplCanvas(self, width=5, height=4, dpi=100)
        self.page_layout.addWidget(self.mc1,1,1)

        self.mc2=MplCanvas(self, width=5, height=4, dpi=100)
        self.page_layout.addWidget(self.mc2,2,0)
        
        self.mc3=MplCanvas(self, width=5, height=4, dpi=100)
        self.page_layout.addWidget(self.mc3,2,1) 

        #defining the layout for the parameter frame
        self.parameter_layout=QGridLayout()
        self.page_layout.addLayout(self.parameter_layout,0,0,2,1)

        #initializing the frames for toolbar, buttons, labels and slider
        toolbar=self.init_toolbar()
        self.addToolBar(toolbar)

        self.init_label_frame()       
        self.init_calculation_frame()
        self.init_parameter_frame()
        self.init_button_frame()
        self.init_imagebutton_frame()
              
        widget = QWidget()
        widget.setLayout(self.page_layout)
        self.setCentralWidget(widget)

    #initializing the toolbar and adding the actions
    def init_toolbar(self):
        toolBar=QToolBar()

        self.btn_open_dialog = QAction("Upload File")
        self.btn_open_dialog.triggered.connect(self.open_dialog)
        toolBar.addAction(self.btn_open_dialog)

        self.btn_save_file =QAction("Save File")
        self.btn_save_file.setDisabled(True)
        self.btn_save_file.triggered.connect(self.save_file)
        toolBar.addAction(self.btn_save_file)

        self.btn_show_select_window = QAction("Select Focus Image")
        self.btn_show_select_window.setDisabled(True)
        self.btn_show_select_window.triggered.connect(self.show_select_window)
        toolBar.addAction(self.btn_show_select_window)

        self.btn_show_setting_window = QAction("Settings")
        self.btn_show_setting_window.setDisabled(True)
        self.btn_show_setting_window.triggered.connect(self.show_setting_window)
        self.btn_show_setting_window.setToolTip("Hit this button to set the settings for the calculation")
        toolBar.addAction(self.btn_show_setting_window)

        self.btn_show_evaluation_window=QAction("Evaluation")
        self.btn_show_evaluation_window.triggered.connect(self.show_evaluation_window)
        toolBar.addAction(self.btn_show_evaluation_window)

        self.btn_statistics=QAction("Statistics")
        self.btn_statistics.triggered.connect(self.statictis)
        self.btn_statistics.setDisabled(True)
        toolBar.addAction(self.btn_statistics)

        return toolBar
    
    def statictis(self):
        self.statistic_window= StatisticWindow()
        self.statistic_window.show()

    #initializing frame for labels
    def init_label_frame(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: lightgray; border: 2px lightgray; border-radius: 10px;}")
        frame_layout = QGridLayout(frame)

        self.lbl_filename = QLabel("Current File: None")
        self.lbl_filename.setToolTip("This is the name of the selected image")
        frame_layout.addWidget(self.lbl_filename, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        self.lbl_focused_image = QLabel("Index focused image: 0")
        self.lbl_focused_image.setToolTip("This is the index of the focused image")
        frame_layout.addWidget(self.lbl_focused_image, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        self.lbl_mass_total = QLabel("Mass total in ng: 0")
        self.lbl_mass_total.setToolTip("This is the mass calculated for the whole image")
        frame_layout.addWidget(self.lbl_mass_total, 0, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        self.lbl_mass_inside = QLabel("Mass inside contour in ng: 0")
        self.lbl_mass_inside.setToolTip("This is the mass calculated inside the selected contour")
        frame_layout.addWidget(self.lbl_mass_inside, 0, 3, alignment=Qt.AlignmentFlag.AlignRight)

        self.lbl_mass_contour_mean = QLabel("Contour mean in ng: 0")
        self.lbl_mass_contour_mean.setToolTip("This is the mean mass directly on the contour")
        frame_layout.addWidget(self.lbl_mass_contour_mean, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        self.lbl_mass_contour_effective = QLabel("<b>Contour effective in ng: 0</b>")
        self.lbl_mass_contour_effective.setToolTip("This is the effective mass inside the contour normalized")
        frame_layout.addWidget(self.lbl_mass_contour_effective, 1, 3, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.parameter_layout.addWidget(frame,0,0,2,3)

    #initializing frame for the calculation options     
    def init_calculation_frame(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: lightgray; border: 2px lightgray; border-radius: 10px;}")
        frame_layout = QGridLayout(frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)  # Add padding around the layout
        frame_layout.setHorizontalSpacing(15)  # Set horizontal spacing between columns
        frame_layout.setVerticalSpacing(10)  # Set vertical spacing between rows

        self.lbl_axial_separation = QLabel("Axial separation:")
        frame_layout.addWidget(self.lbl_axial_separation, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        self.txt_axial_separation = QLineEdit()
        self.txt_axial_separation.setValidator(QIntValidator())
        self.txt_axial_separation.setToolTip("This field specifies the axial distance (index) for the calculation with the FFT.")
        self.txt_axial_separation.setDisabled(True)
        self.txt_axial_separation.setFixedSize(50, 30)
        self.txt_axial_separation.setText("1")  # Example default value
        frame_layout.addWidget(self.txt_axial_separation, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        self.lbl_axial_separation_high = QLabel("Axial separation_high:")
        frame_layout.addWidget(self.lbl_axial_separation_high, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        self.txt_axial_separation_high = QLineEdit()
        self.txt_axial_separation_high.setValidator(QIntValidator())
        self.txt_axial_separation_high.setToolTip("This field specifies the axial distance (index) for the calculation with the FFT.")
        self.txt_axial_separation_high.setDisabled(True)
        self.txt_axial_separation_high.setFixedSize(50, 30)
        self.txt_axial_separation_high.setText("1")  # Example default value
        frame_layout.addWidget(self.txt_axial_separation_high, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        self.btn_calculate_US = QPushButton("Calculate Optical Path Length (US)")
        self.btn_calculate_US.setToolTip("Use calculation option with the universal solution")
        self.btn_calculate_US.setDisabled(True)
        self.btn_calculate_US.clicked.connect(self.show_plot_opl_US)
        frame_layout.addWidget(self.btn_calculate_US, 1, 3, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.btn_calculate_FFT = QPushButton("Calculate Optical Path Length (FFT)")
        self.btn_calculate_FFT.setToolTip("Use calculation option with FFT")
        self.btn_calculate_FFT.setDisabled(True)
        self.btn_calculate_FFT.clicked.connect(self.show_plot_opl_fft)
        frame_layout.addWidget(self.btn_calculate_FFT, 0, 2, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.btn_calculate_FFT_mixing = QPushButton("Calculate FFT mixing")
        self.btn_calculate_FFT_mixing.setToolTip("mixing")
        self.btn_calculate_FFT_mixing.setDisabled(True)
        self.btn_calculate_FFT_mixing.clicked.connect(self.show_plot_opl_fft_mixing)
        frame_layout.addWidget(self.btn_calculate_FFT_mixing, 1, 2, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.btn_calculate_TV = QPushButton("Calculate Optical Path Length (TV Regularization)")
        self.btn_calculate_TV.setToolTip("Use calculation option with regularization")
        self.btn_calculate_TV.setDisabled(True)
        self.btn_calculate_TV.clicked.connect(self.show_plot_opl_tv)
        frame_layout.addWidget(self.btn_calculate_TV, 0, 3, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.parameter_layout.addWidget(frame, 2, 0, 1, 3)

    #initializing frame for the parameter slider
    def init_parameter_frame(self):
        frame=QFrame()
        frame.setStyleSheet("QFrame {background-color: lightgray; border: 2px lightgray; border-radius: 10px;}")
        frame_layout=QGridLayout(frame)

        # initializing Slider for adjusting the threshold for contourdetection
        self.sld_find_contour_threshold = QSlider()
        self.sld_find_contour_threshold.setFixedSize(500,30)
        self.sld_find_contour_threshold.setOrientation(Qt.Orientation.Horizontal)
        self.sld_find_contour_threshold.setMinimum(1)
        self.sld_find_contour_threshold.setMaximum(250)
        self.sld_find_contour_threshold.setDisabled(True)
        self.sld_find_contour_threshold.sliderReleased.connect(self.contour_detection)        
        self.sld_find_contour_threshold.setToolTip("Refine the threshold to precisely identify contours in your image")
        frame_layout.addWidget(self.sld_find_contour_threshold,1,1,1,1, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.lbl_find_contour_threshold=QLabel("Treshold: 0")
        frame_layout.addWidget(self.lbl_find_contour_threshold,0,0,1,3,alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.btn_find_contour_threshold_down=QPushButton("<")
        self.btn_find_contour_threshold_down.setFixedSize(30,30)
        self.btn_find_contour_threshold_down.setDisabled(True)
        self.btn_find_contour_threshold_down.clicked.connect(self.find_contour_threshold_down)
        frame_layout.addWidget(self.btn_find_contour_threshold_down,1,0)

        self.btn_find_contour_threshold_up=QPushButton(">")
        self.btn_find_contour_threshold_up.setFixedSize(30,30)
        self.btn_find_contour_threshold_up.setDisabled(True)
        self.btn_find_contour_threshold_up.clicked.connect(self.find_contour_threshold_up)
        frame_layout.addWidget(self.btn_find_contour_threshold_up,1,2)

        self.txt_find_contour_threshold=QLineEdit()
        self.txt_find_contour_threshold.setValidator(QIntValidator(1,255,self))
        self.txt_find_contour_threshold.setText("1")
        self.txt_find_contour_threshold.setFixedSize(60,30)
        self.txt_find_contour_threshold.setDisabled(True)
        self.txt_find_contour_threshold.editingFinished.connect(self.find_contour_threshold)
        frame_layout.addWidget(self.txt_find_contour_threshold,1,3)


        #initializing slider for iterating found contours
        self.sld_find_contour_index = QSlider()
        self.sld_find_contour_index.setFixedSize(500,30)
        self.sld_find_contour_index.setOrientation(Qt.Orientation.Horizontal)
        self.sld_find_contour_index.setMinimum(-1)
        self.sld_find_contour_index.setMaximum(10)
        self.sld_find_contour_index.setValue(-1)
        self.sld_find_contour_index.setDisabled(True)
        self.sld_find_contour_index.valueChanged.connect(self.draw_contour) #this here could be wrong! it is just plotting, not calculating everything!
        self.sld_find_contour_index.setToolTip("Use this slider to choose the right contour")
        frame_layout.addWidget(self.sld_find_contour_index,3,1,1,1, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.lbl_find_contour_index=QLabel("All Contours")
        frame_layout.addWidget(self.lbl_find_contour_index,2,0,1,3,alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.btn_find_contour_index_down=QPushButton("<")
        self.btn_find_contour_index_down.setFixedSize(30,30)
        self.btn_find_contour_index_down.setDisabled(True)
        self.btn_find_contour_index_down.clicked.connect(self.find_contour_index_down)
        frame_layout.addWidget(self.btn_find_contour_index_down,3,0)

        self.btn_find_contour_index_up=QPushButton(">")
        self.btn_find_contour_index_up.setFixedSize(30,30)
        self.btn_find_contour_index_up.setDisabled(True)
        self.btn_find_contour_index_up.clicked.connect(self.find_contour_index_up)
        frame_layout.addWidget(self.btn_find_contour_index_up,3,2)

        self.btn_find_contour_index_all=QPushButton("Show All")
        self.btn_find_contour_index_all.setFixedSize(60,30)
        self.btn_find_contour_index_all.setDisabled(True)
        self.btn_find_contour_index_all.clicked.connect(self.find_contour_index_all)
        frame_layout.addWidget(self.btn_find_contour_index_all,3,3)

        #initializing slider for inflating the selected contour
        self.sld_inflate_contour = QSlider()
        self.sld_inflate_contour.setOrientation(Qt.Orientation.Horizontal)
        self.sld_inflate_contour.setMinimum(50)
        self.sld_inflate_contour.setMaximum(150)
        self.sld_inflate_contour.setDisabled(True)
        self.sld_inflate_contour.setValue(100)
        self.sld_inflate_contour.setFixedSize(500,30)
        self.sld_inflate_contour.setToolTip("Use this slider to adjust the scale of the contour")
        self.sld_inflate_contour.sliderReleased.connect(self.show_scaled_contours)
        frame_layout.addWidget(self.sld_inflate_contour,5,1,1,1, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.lbl_inflate=QLabel("Inflate Contour: 1")
        frame_layout.addWidget(self.lbl_inflate,4,0,1,3,alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.btn_inflate_down=QPushButton("<")
        self.btn_inflate_down.setFixedSize(30,30)
        self.btn_inflate_down.setDisabled(True)
        self.btn_inflate_down.clicked.connect(self.scale_down)
        frame_layout.addWidget(self.btn_inflate_down,5,0)

        self.btn_inflate_up=QPushButton(">")
        self.btn_inflate_up.setFixedSize(30,30)
        self.btn_inflate_up.setDisabled(True)
        self.btn_inflate_up.clicked.connect(self.scale_up)
        frame_layout.addWidget(self.btn_inflate_up,5,2)

        self.txt_inflate_contour=QLineEdit()
        #self.txt_inflate_contour.setValidator(QDoubleValidator(0.5,1.5).setDecimals(2))
        self.txt_inflate_contour.setText("1")
        self.txt_inflate_contour.setFixedSize(60,30)
        self.txt_inflate_contour.setDisabled(True)
        self.txt_inflate_contour.editingFinished.connect(self.inflate)
        frame_layout.addWidget(self.txt_inflate_contour,5,3)

        self.parameter_layout.addWidget(frame,4,0,3,3)

    #Initializes a frame containing buttons for contour operations
    def init_button_frame(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: lightgray; border: 2px lightgray; border-radius: 10px;}")
        frame_layout = QGridLayout(frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)  # Add padding around the layout
        frame_layout.setHorizontalSpacing(15)  # Set horizontal spacing between columns
        frame_layout.setVerticalSpacing(10)  # Set vertical spacing between rows

        self.btn_draw_contour_yourself = QPushButton("Draw Contour Manually")
        self.btn_draw_contour_yourself.setAccessibleName("draw_status")
        self.btn_draw_contour_yourself.setToolTip("Hit this button to draw the contour by yourself")
        self.btn_draw_contour_yourself.setDisabled(True)
        self.btn_draw_contour_yourself.clicked.connect(self.draw_contour_manually)
        frame_layout.addWidget(self.btn_draw_contour_yourself, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_store_contour = QPushButton("Store Contour")
        self.btn_store_contour.setToolTip("You can store this Contour for further calculations.")
        self.btn_store_contour.setDisabled(True)
        self.btn_store_contour.clicked.connect(self.store_contour)
        frame_layout.addWidget(self.btn_store_contour, 0, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_recall_contour = QPushButton("Recall Contour")
        self.btn_recall_contour.setAccessibleName("_stored")
        self.btn_recall_contour.setToolTip("With this Button you can recall the stored Contour")
        self.btn_recall_contour.setDisabled(True)
        self.btn_recall_contour.clicked.connect(self.recall_contour)
        frame_layout.addWidget(self.btn_recall_contour, 0, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_select_contour = QPushButton("Calculate Contour Mass")
        self.btn_select_contour.setToolTip("Hit this button to choose the drawn points as contour")
        self.btn_select_contour.setDisabled(True)
        self.btn_select_contour.clicked.connect(self.calculate_contour_mass)
        frame_layout.addWidget(self.btn_select_contour, 0, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.parameter_layout.addWidget(frame,7,0,1,3)

    #Initializes a frame containing buttons for image display options
    def init_imagebutton_frame(self):
        frame=QFrame()
        frame.setStyleSheet("QFrame { background-color: lightgray; border: 2px lightgray; border-radius: 10px;}")
        frame_layout=QGridLayout(frame)
        frame.setMaximumHeight(40)
        frame.setLineWidth(1)

        self.btn_show_background=QPushButton("Background Image")
        self.btn_show_background.setToolTip("Show the Background")
        self.btn_show_background.setMaximumHeight(33)
        self.btn_show_background.setDisabled(True)
        self.btn_show_background.clicked.connect(self.show_background)
        frame_layout.addWidget(self.btn_show_background, 0,0, alignment=Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignCenter)

        self.btn_show_raw_image=QPushButton("Image")
        self.btn_show_raw_image.setToolTip("Show the Image")
        self.btn_show_raw_image.setMaximumHeight(33)
        self.btn_show_raw_image.setDisabled(True)
        self.btn_show_raw_image.clicked.connect(self.show_raw_image)
        frame_layout.addWidget(self.btn_show_raw_image, 0,0, alignment=Qt.AlignmentFlag.AlignCenter|Qt.AlignmentFlag.AlignCenter)

        self.btn_show_stack=QPushButton("Stack Image")
        self.btn_show_stack.setToolTip("Show the Stack")
        self.btn_show_stack.setMaximumHeight(33)
        self.btn_show_stack.setDisabled(True)
        self.btn_show_stack.clicked.connect(self.show_stack)
        frame_layout.addWidget(self.btn_show_stack, 0,0, alignment=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignCenter)

        self.page_layout.addWidget(frame,0,1)
    
    def init_mc1(self, plot_option):
        frame=QFrame()
        frame_layout=QGridLayout(frame)

        self.layout().removeWidget(self.mc1)
        self.mc1=MplCanvas(self, width=5, height=4, dpi=100)
        toolbar_zoom = NavigationToolbar(self.mc1, self)

        frame_layout.addWidget(toolbar_zoom, 0,0)
        frame_layout.addWidget(self.mc1,1,0)   
        
        self.page_layout.addWidget(frame,1,1)
        if plot_option: plot_option()
    
    def init_mc2(self, plot_option):
        frame=QFrame()
        frame_layout=QGridLayout(frame)

        self.layout().removeWidget(self.mc2)
        self.mc2=MplCanvas(self, width=5, height=4, dpi=100)

        toolbar_zoom = NavigationToolbar(self.mc2, self)
        frame_layout.addWidget(toolbar_zoom, 0,0)
        frame_layout.addWidget(self.mc2,1,0) 

        self.page_layout.addWidget(frame,2,0)        
        if plot_option: plot_option()

    def init_mc3(self, plot_option):
        frame=QFrame()
        frame_layout=QGridLayout(frame)

        self.layout().removeWidget(self.mc3)
        self.mc3=MplCanvas(self, width=5, height=4, dpi=100)

        toolbar_zoom = NavigationToolbar(self.mc3, self)
        frame_layout.addWidget(toolbar_zoom, 0,0)
        frame_layout.addWidget(self.mc3,1,0)   

        self.page_layout.addWidget(frame,2,1)
        if plot_option: plot_option()

    #dialog for uploading files
    def open_dialog(self):
        try:   
            path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "LIF Files (*.lif);;TIF Files (*.tif);;STK Files (*.stk)")

            if path:
                file.reset()
                if path.endswith('.lif'):
                    self.initialize_lif_file(path)
                if path.endswith('.stk') or path.endswith('.tif'):
                    self.initialize_tif_file(path)
            else: 
                return                

            #reseting the mainwindow
            self.init_mc1(None)
            self.init_mc2(None)
            self.init_mc3(None)
            self.init_label_frame()
            self.init_calculation_frame()
            self.init_parameter_frame()
            self.init_button_frame()
            self.init_imagebutton_frame()

            self.setting_window = SettingWindow(self)
            self.setting_window.show()

        except Exception as e:
            self.error_message(e)            
    
    #dialog for saving file
    def save_file(self):
        try:
            if file.filename=="": raise Exception ('Error: No file to save! Please ensure that there is a file to save before proceeding.')
            file_name = file.filename.replace('/', '-')
            path, _ = QFileDialog.getSaveFileName(self, "Save File",file_name, " csv Files (*.csv) ;; Text Files (*.txt)") #str(file.filename)
            if path:
                self.mc1.save_figure(path[:-4]+'(rawfile)')
                self.mc2.save_figure(path[:-4]+'(drymass)')
                self.mc3.save_figure(path[:-4]+'(selectedpart)')
                        
                csv_path = f"{path[:-4]}.csv"
                with open(csv_path, 'w') as files:
                    csv_writer = csv.writer(files)
                    file.write_csv(csv_writer)
                
                npy_path = f"{path[:-4]}.npy"
                np.save(npy_path, file.selected_contour)

            else: raise Exception('Error: Wrong path. Please provide a valid path.')
        except Exception as e:
            self.error_message(e)

    #loading the .tif-file with corresponding data
    def initialize_tif_file(self, path):
        file.file_format=FileFormat.TIF

        file.file=[[],[]]
        file.name=[[],[]]

        if path:
            sample_stack=tif.imread(path)
            # sample_stack=mtif.read_stack(path)
            file.sample=np.asarray([slice for slice in sample_stack])
            file.file[0]=file.sample
            file.name[0]= self.extract_filename(path)

        file.name[1]="Please Upload a Background Image!"

    #loading the .lif-file with corresponding data
    def initialize_lif_file(self, path):
        file.file_format=FileFormat.LIF

        file.file=LifFile(path)

        if file.file==None: 
            raise Exception('Invalid input: No file selected. Please select a file.')
        
        file.lifProperties = []    
        file.uploaded_files=[]
        file.name=""

        for idx, entry in enumerate(file.file.image_list):
            file.lifProperties.append(f"Index: {idx:<5}Name:{entry['name']:<60}Dimensions: {str(entry['dims']):<40}")
            file.uploaded_files.append(entry['name'])
        
        file.name=self.extract_filename(path)

    #extracting the filename from path
    def extract_filename(self, path):
        name=''
        for i in range (len(path)-5, -1, -1):
            if(path[i] == '/'): 
                break
            name=name+path[i]

        return name[::-1] #reversing the filename

    #opens window for entering the microscope&calculation setting
    def show_setting_window(self):
        if file.file==None: 
            file.lifProperties=['No File Uploaded']

        self.setting_window = SettingWindow(self) 
        self.setting_window.show()

    #opens a window to select de focused image
    def show_select_window(self):
        self.select_window = SelectWindow(file, self, len(file.sample))
        self.select_window.value_changed(file.idx_focused_image)
        self.select_window.show()

    #opens a window for evaluation 
    def show_evaluation_window (self):
        self.evaluation_window=EvaluationWindow()
        self.evaluation_window.show()

    #shows backgroundimage in mc1
    def show_background(self):
        self.init_mc1(lambda: self.mc1.show_image('Background Idx 1', file.background[1]))
        self.mc1.with_selector()

    #shows sample image in mc1    
    def show_raw_image(self):#passt
        self.init_mc1(lambda: self.mc1.show_image('Sample Idx 1', file.sample[1]))
        self.mc1.with_selector()

    #shows stack image in mc1
    def show_stack(self):#passt
        self.init_mc1(lambda: self.mc1.show_image('Stack Idx 1', file.stack[1]))
        self.mc1.with_selector()

    #calculates the mass and opl and displays plots for opl and selected part
    def _show_OPL_plot_default(self, calculation_option):
        try: 
            # reset labels, buttons, drawn contour and slider when calculating a new image           
            file.draw_x=[]
            file.draw_y=[]
            self.reset_labels()
            self.reset_sliders()
            self.toggle_contour_index(True)
            self.toggle_contour_threshold(True)
            self.btn_save_file.setEnabled(True)
            self.btn_statistics.setDisabled(True)
            self.btn_draw_contour_yourself.setText("Draw Contour Manually")
            self.btn_draw_contour_yourself.setAccessibleName("draw_status")
            self.btn_recall_contour.setText("Recall Contour")
            self.btn_recall_contour.setAccessibleName("_stored")
            self.btn_recall_contour.setStyleSheet("")   
            
            self.enable_all_buttons()
            
            file.axial_separation=int(self.txt_axial_separation.text())
            file.axial_separation_high=int(self.txt_axial_separation_high.text())

            # calculation of opl and dry mass
            calculation_option()
            calc.opl_dry_mass()

            # display drymass and contours with default values
            self.contour_detection()  
        except ValueError:
            self.error_message(Exception("INVALID INPUT! The value for inflating has to be between 0.5 and 1.5"))
        except Exception as e:
           self.error_message(e)

    def show_plot_opl_fft(self):
        self._show_OPL_plot_default(lambda: calc.calculate_opl_fft(statistics=False, low=True, high=False)) 

    def show_plot_opl_fft_mixing(self):
        self._show_OPL_plot_default(lambda: calc.mixing())   

    def show_plot_opl_US(self):
        self._show_OPL_plot_default(lambda: calc.calculate_opl_US_method())     
    
    def show_plot_opl_tv(self):
        self._show_OPL_plot_default(lambda: calc.calculate_opl_tv())                
    
    #calculates the contours and displays them in mc3 plot
    def contour_detection(self):#passt
        # reset & update of GUI-elements and fileproperties
        file.threshold=self.sld_find_contour_threshold.value()
        self.lbl_find_contour_threshold.setText("Treshold: "+str(file.threshold)) 
        self.txt_find_contour_threshold.setText(str(file.threshold))       
        self.sld_inflate_contour.setValue(100)
        self.lbl_inflate.setText("Inflate Contour: " + str(self.sld_inflate_contour.value()/100))

        # searching for contours
        calc.contour_detection()
        self.sld_find_contour_index.setMaximum(len(file.hierarchy)-1)
        self.draw_contour()

    #draw contours in image with opl and in the image for the selected part
    def draw_contour(self):
        file.selected_contour_index=self.sld_find_contour_index.value()
        file.state=State.DEFAULT

        self.reset_labels()

        self.validate_scale_functionality()

        self.init_mc2(lambda: self.mc2.draw_contour_with_colorbar( 'To get the Mass hit \'Calculate Contour Mass\'', True))

        self.init_mc3(lambda: self.mc3.draw_contour('Selected Part', True))

    #it is only possible to scale if a contour is selected, if all contours are shown, the scale functionality is disabled   
    def validate_scale_functionality(self):
        if file.selected_contour_index!=-1:
            self.lbl_find_contour_index.setText("Contour Index: "+str(file.selected_contour_index))
            self.toggle_inflate_contour(True)
        else:
            self.lbl_find_contour_index.setText('All Contours')
            self.toggle_inflate_contour(False)

    def draw_contour_manually(self):
        self.btn_statistics.setDisabled(True)
        self.reset_labels()
        self.btn_recall_contour.setText("Recall Contour")
        self.btn_recall_contour.setAccessibleName("_stored")
        self.btn_recall_contour.setStyleSheet("")

        self.toggle_contour_index(False)
        self.toggle_contour_threshold(False)
        self.toggle_inflate_contour(False)

        if(self.btn_draw_contour_yourself.accessibleName()=="draw_status"):
            file.state=State.DRAWN            
            self.toggle_contour_index(False)
            self.toggle_contour_threshold(False)
            self.toggle_inflate_contour(False)

            #initialize the plots with draw functionality
            self.init_mc2(lambda: self.mc2.draw_contour_with_colorbar( 'Draw a contour', False))
            self.mc2.with_draw()
            
            self.btn_draw_contour_yourself.setText("generate Contour")
            self.btn_draw_contour_yourself.setAccessibleName("contour_status")
        else:
            file.draw_x=[]
            file.draw_x=[]
            self.toggle_contour_index(True)
            self.toggle_contour_threshold(True)
            self.toggle_inflate_contour(False)
            self.contour_detection()

            self.btn_draw_contour_yourself.setText("Draw Contour Manually")
            self.btn_draw_contour_yourself.setAccessibleName("draw_status")

    #calculates the mass for contour and sets the labels right
    def calculate_contour_mass(self):
        try:
            if(file.state==State.DRAWN):
                if(file.draw_x==[]):
                    raise Exception("Please draw a contour first.")
            else:
                self.btn_draw_contour_yourself.setText("Draw Contour Manually")
                self.btn_draw_contour_yourself.setAccessibleName("draw_status")
            self.btn_statistics.setEnabled(True)
            calc.select_contour()
            calc.contour_mass()
            calc.contourline_mean_mass()

            self.set_labels()
            title='Dry Mass in ng: '+str(round(file.contour_inside_mass-file.contourline_mean_mass,3))
            self.init_mc2(lambda: self.mc2.draw_selected_contour_with_colorbar(title, True))

        except Exception as e:
            self.error_message(e)
            
    def show_scaled_contours(self):
        file.state=State.SCALED
        file.inflatefactor=self.sld_inflate_contour.value()/100
        self.reset_labels()
        self.lbl_inflate.setText("Inflate Contour: "+str(self.sld_inflate_contour.value()/100))
        self.txt_inflate_contour.setText(str(file.inflatefactor))

        calc.scale_contour()
        
        self.init_mc2(lambda: self.mc2.draw_inflated_contour_with_colorbar( 'To get the Mass hit \'Calculate Contour Mass\'', True))
        self.init_mc3(lambda: self.mc3.draw_inflated_contour('Selected Part', True))

    def store_contour(self):
        calc.select_contour()
        self.btn_recall_contour.setEnabled(True)
        file.stored_contour=file.selected_contour
        self.btn_recall_contour.setAccessibleName("_stored")
    
    def recall_contour(self):
        self.reset_labels()        
        
        if  self.btn_recall_contour.accessibleName()=="_stored":
            self.toggle_contour_index(False)
            self.toggle_contour_threshold(False)
            self.toggle_inflate_contour(False)
            file.state=State.STORED
            calc.select_contour()
            self.init_mc2(lambda: self.mc2.draw_selected_contour_with_colorbar('To get the Mass hit \'Calculate Contour Mass\'', contour_bool=True) )
            self.init_mc3(lambda: self.mc3.draw_stored_contour('Selected Part', True))
            self.btn_recall_contour.setText("Hide Stored Contour")
            self.btn_recall_contour.setAccessibleName("_hide")
            self.btn_recall_contour.setStyleSheet("background-color: lightblue; color: black; border: 1px solid black;")
            file.selected_contour=file.stored_contour
        else:
            if(file.inflatefactor==1):
               self.draw_contour()
            else:
                self.show_scaled_contours()

            self.toggle_contour_index(True)
            self.toggle_contour_threshold(True)
            self.toggle_inflate_contour(True)
            self.btn_recall_contour.setText("Recall Contour")
            self.btn_recall_contour.setAccessibleName("_stored")
            self.btn_recall_contour.setStyleSheet("")
            self.btn_draw_contour_yourself.setText("Draw Contour Manually")
            self.btn_draw_contour_yourself.setAccessibleName("draw_status")

    #button functions for increase/decrease the sliders
    def find_contour_threshold_up(self):
        self.sld_find_contour_threshold.setValue(self.sld_find_contour_threshold.value()+1)
        self.contour_detection()
    
    def find_contour_threshold_down(self):
        self.sld_find_contour_threshold.setValue(self.sld_find_contour_threshold.value()-1)
        self.contour_detection()

    def find_contour_index_up(self):
        self.sld_find_contour_index.setValue(self.sld_find_contour_index.value()+1)
    
    def find_contour_index_down(self):
        self.sld_find_contour_index.setValue(self.sld_find_contour_index.value()-1)
    
    def scale_down(self):
        self.sld_inflate_contour.setValue(self.sld_inflate_contour.value()-1)
        self.show_scaled_contours()

    def scale_up(self):
        self.sld_inflate_contour.setValue(self.sld_inflate_contour.value()+1)
        self.show_scaled_contours()
    
    #enables all buttons except inflate buttons and recall button
    def enable_all_buttons(self):
        for button in self.findChildren(QPushButton):
            if(button==self.btn_inflate_down or button==self.btn_inflate_up or button==self.btn_recall_contour): continue
            button.setEnabled(True)

    #resets the labels in label_frame (-> mass=0)
    def reset_labels(self):
        self.lbl_mass_total.setText("Mass total in ng: 0")
        self.lbl_mass_inside.setText("Mass inside cont. in ng: 0")
        self.lbl_mass_contour_mean.setText("Contour mean in ng: 0")
        self.lbl_mass_contour_effective.setText("<b>Contour effective in ng: 0</b>")
        
    #Sets the labels in label_frame (->mass=calculated mass)
    def set_labels(self):
        self.lbl_mass_total.setText("Mass total in ng: "+str(round(file.entire_mass,3)))
        self.lbl_mass_inside.setText("Mass inside cont. in ng: "+str(round(file.contour_inside_mass,3)))
        self.lbl_mass_contour_mean.setText("Contour mean in ng: "+str(round(file.contourline_mean_mass,3)))
        self.lbl_mass_contour_effective.setText("<b>Contour effective in ng: </b><b>{}</b>".format(round(file.contour_inside_mass - file.contourline_mean_mass, 3)))
    
    #resets the sliders to default value
    def reset_sliders(self):#passt
        self.sld_find_contour_threshold.setValue(1)
        self.sld_find_contour_index.setValue(-1)
        self.sld_inflate_contour.setValue(100)
        self.lbl_inflate.setText("Inflate Contour: 1")
        self.txt_inflate_contour.setText("1")

    def toggle_contour_index(self, enable):
        self.btn_find_contour_index_up.setEnabled(enable)
        self.btn_find_contour_index_down.setEnabled(enable)
        self.sld_find_contour_index.setEnabled(enable)
        self.btn_find_contour_index_all.setEnabled(enable)

    def toggle_contour_threshold(self, enable):
        self.btn_find_contour_threshold_up.setEnabled(enable)
        self.btn_find_contour_threshold_down.setEnabled(enable)
        self.sld_find_contour_threshold.setEnabled(enable)
        self.txt_find_contour_threshold.setEnabled(enable)

    def toggle_inflate_contour(self, enable):
        self.btn_inflate_up.setEnabled(enable)
        self.btn_inflate_down.setEnabled(enable)
        self.sld_inflate_contour.setEnabled(enable)
        self.txt_inflate_contour.setEnabled(enable)

    def find_contour_index_all(self):
        self.sld_find_contour_index.setValue(-1)
    
    def inflate(self):
        try:
            self.sld_inflate_contour.setValue(int(100*float(self.txt_inflate_contour.text())))
        except ValueError:
            self.error_message(Exception("WROG INPUT!"))

    def find_contour_threshold(self):
        self.sld_find_contour_threshold.setValue(int(self.txt_find_contour_threshold.text()))

    #displays the errormessage
    def error_message(self, message):
        QMessageBox.critical(self, "Error!", str(message), buttons=QMessageBox.StandardButton.Close,)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = Main()
    main_gui.show()
    sys.exit(app.exec())