import matplotlib
matplotlib.use('QtAgg')
from daten import file
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QLineEdit,  QLabel, QComboBox, QMessageBox, QFrame, QGridLayout, QFileDialog
    )
import calculation as calc
from state import FileFormat
import numpy as np
import multipagetiff as mtif
import tifffile as tiff 


class SettingWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.resize(300, 100)
        self.setWindowTitle("Settings")
        self.main_window=main_window

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        if file.file_format==FileFormat.LIF:
            self.init_sample_background_frame_lif()
        elif file.file_format== FileFormat.TIF:
            self.init_sample_background_frame_tif()
        else:
            self.layout.addWidget(QLabel('No File uploaded!'))

        self.init_parameter_frame()
        self.init_button_frame()
    #init frames
    def init_sample_background_frame_lif(self):
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)

        frame_layout.addWidget(QLabel("Index for Sample:"))
        self.cmb_idx_sample=QComboBox()
        self.cmb_idx_sample.addItems(file.lifProperties)
        self.cmb_idx_sample.setCurrentIndex(file.idx_sample)
        frame_layout.addWidget(self.cmb_idx_sample)

        frame_layout.addWidget(QLabel("Index for Background:"))
        self.cmb_idx_background=QComboBox()
        self.cmb_idx_background.addItems(file.lifProperties)
        self.cmb_idx_background.setCurrentIndex(file.idx_background)
        frame_layout.addWidget(self.cmb_idx_background)

        self.layout.addWidget(frame)

    def init_sample_background_frame_tif(self):
        frame=QFrame()
        frame_layout=QGridLayout(frame)

        self.lbl_sample=QLabel(file.name[0])
        frame_layout.addWidget(QLabel('Sample'),0,0)
        frame_layout.addWidget(self.lbl_sample,1,0)
        self.btn_load_sample=QPushButton('Upload Sample')
        self.btn_load_sample.clicked.connect(self.load_sample)
        frame_layout.addWidget(self.btn_load_sample, 1,1)

        frame_layout.addWidget(QLabel('Background'),2,0)
        self.lbl_background=QLabel(file.name[1])
        
        frame_layout.addWidget(self.lbl_background,3,0)
        self.btn_load_background=QPushButton('Upload Background')
        self.btn_load_background.clicked.connect(self.load_background)
        frame_layout.addWidget(self.btn_load_background, 3,1)

        self.layout.addWidget(frame)

    def init_parameter_frame(self):         
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)

        frame_layout.addWidget(QLabel(text = "Magnification:"))
        self.txt_magnification = QLineEdit()
        self.txt_magnification.setValidator(QDoubleValidator())
        self.txt_magnification.setText(str(file.magnification))
        frame_layout.addWidget(self.txt_magnification)

        frame_layout.addWidget(QLabel(text = "Pixel size in nm:"))
        self.txt_pixel_size = QLineEdit()
        self.txt_pixel_size.setValidator(QDoubleValidator())
        self.txt_pixel_size.setText(str(file.pixel_size*1e9))
        frame_layout.addWidget(self.txt_pixel_size)

        frame_layout.addWidget(QLabel(text = "Axial step in nm:"))
        self.txt_axial_step = QLineEdit()
        self.txt_axial_step.setValidator(QDoubleValidator())
        self.txt_axial_step.setText(str(round((file.axial_step*1e9),2)))
        frame_layout.addWidget(self.txt_axial_step)

        frame_layout.addWidget(QLabel(text = "Constant alpha in nm^3/g:"))
        self.txt_alpha = QLineEdit()
        self.txt_alpha.setValidator(QDoubleValidator())
        self.txt_alpha.setText(str(round(file.alpha*1e9,3)))
        frame_layout.addWidget(self.txt_alpha)

        frame_layout.addWidget(QLabel(text = "Regularisation constant (lbda_TV*10^6):"))
        self.txt_lbda_TV = QLineEdit()
        self.txt_lbda_TV.setValidator(QDoubleValidator())
        self.txt_lbda_TV.setText(str(file.lbda_TV*1e6))
        frame_layout.addWidget(self.txt_lbda_TV)

        frame_layout.addWidget(QLabel(text = "#Iterations for TV Norm:"))
        self.txt_iteration = QLineEdit()
        self.txt_iteration.setValidator(QIntValidator())
        self.txt_iteration.setText(str(file.iteration))
        frame_layout.addWidget(self.txt_iteration)

        self.layout.addWidget(frame)
    
    def init_button_frame(self):
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
    
        self.btn_save_properties = QPushButton("Continue")
        self.btn_save_properties.clicked.connect(self.save_properties)
        frame_layout.addWidget(self.btn_save_properties)

        self.layout.addWidget(frame)

    #if a .tif-file gets uploaded a different approach is choosen to save sample and background
    def load_sample(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "TIF Files (*.tif);; STK Files (*.stk)")

        if path:
            # sample_stack=mtif.read_stack(path)
            sample_stack=tiff.imread(path)
            file.sample=np.asarray([slice for slice in sample_stack])
            file.file[0]=file.sample
            file.name[0]= self.main_window.extract_filename(path)
            self.lbl_background.setText(file.name[0])

    def load_background(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "TIF Files (*.tif);; STK Files (*.stk)")

        if path:
            # bgd_stack=mtif.read_stack(path)
            bgd_stack=tiff.imread(path)
            file.background=np.asarray([slice for slice in bgd_stack])
            file.file[1]=file.background
            file.name[1]= self.main_window.extract_filename(path)
            self.lbl_background.setText(file.name[1])


    def save_properties(self):
        try:
            if file.file!=None:
                idx_changed=self.helper_method()

                
                if file.file_format==FileFormat.LIF:
                    file.idx_background = int(self.cmb_idx_background.currentIndex())
                    file.idx_sample = int(self.cmb_idx_sample.currentIndex())
                    file.filename=file.name+'_'+file.uploaded_files[file.idx_sample]
                else:
                    file.idx_background=0
                    file.idx_sample=0
                    file.filename=str(file.name)

                file.magnification = float(self.txt_magnification.text())
                file.pixel_size = float(self.txt_pixel_size.text())*1e-9
                file.axial_step = float(self.txt_axial_step.text())*1e-9
                file.alpha=float(self.txt_alpha.text())*1e-9
                file.lbda_TV=float(self.txt_lbda_TV.text())*1e-6
                file.iteration=int(self.txt_iteration.text())
                

                if idx_changed:
                    calc.calculate_background_sample_stack()
                    calc.find_focused_image(file)
                    self.main_window.btn_statistics.setDisabled(True)

                # Setting Labels and enable buttons
                self.main_window.lbl_filename.setText("Current file: "+ file.filename)
                self.main_window.lbl_focused_image.setText("Index focused image: "+str(file.idx_focused_image))
                self.main_window.btn_show_select_window.setDisabled(False)
                self.main_window.btn_show_raw_image.setDisabled(False)
                self.main_window.btn_show_stack.setDisabled(False)
                self.main_window.btn_show_background.setDisabled(False)
                self.main_window.show_raw_image()
            self.close()

        except Exception:
            QMessageBox.critical(self, "Error!", 'Invalid Input: Please check the Index for Sample and Background!', buttons=QMessageBox.StandardButton.Close,)

    #Checks if settings for background&sample calculations cahanged
    def helper_method(self):
        if file.file_format==FileFormat.TIF:
            return True
        else:
            return (
                file.idx_background != int(self.cmb_idx_background.currentIndex()) or
                file.idx_sample != int(self.cmb_idx_sample.currentIndex())
            )

