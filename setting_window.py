import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QLineEdit,  QLabel
    )
import calculation as calc


class SettingWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.resize(300, 100)
        self.setWindowTitle("Properties")

        self.main_window=main_window
        self.file=main_window.file

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.lbl_status=QLabel("Please upload a file!")
        layout.addWidget(self.lbl_status)
      
        layout.addWidget(QLabel(text = "Magnification:"))
        self.txt_magnification = QLineEdit()
        self.txt_magnification.setText(str(self.file.magnification))
        layout.addWidget(self.txt_magnification)

        layout.addWidget(QLabel(text = "Camera Increment:"))
        self.txt_camera_increment = QLineEdit()
        self.txt_camera_increment.setText(str(self.file.camera_increment))
        layout.addWidget(self.txt_camera_increment)

        layout.addWidget(QLabel(text = "Axial Step:"))
        self.txt_axial_step = QLineEdit()
        self.txt_axial_step.setText(str(self.file.axial_step))
        layout.addWidget(self.txt_axial_step)

        layout.addWidget(QLabel(text = "File for Sample:"))
        self.txt_idx_sample = QLineEdit()
        self.txt_idx_sample.setText(str(self.file.idx_sample))
        layout.addWidget(self.txt_idx_sample)

        layout.addWidget(QLabel(text = "File for Background:"))
        self.txt_idx_background = QLineEdit()
        self.txt_idx_background.setText(str(self.file.idx_background))
        layout.addWidget(self.txt_idx_background)

        layout.addWidget(QLabel(text = "alpha [m^3/g]:"))
        self.txt_alpha = QLineEdit()
        self.txt_alpha.setText(str(self.file.alpha))
        layout.addWidget(self.txt_alpha)

        layout.addWidget(QLabel(text = "lbda_TV"))
        self.txt_lbda_TV = QLineEdit()
        self.txt_lbda_TV.setText(str(self.file.lbda_TV))
        layout.addWidget(self.txt_lbda_TV)

        layout.addWidget(QLabel(text = "Iterations:"))
        self.txt_iteration = QLineEdit()
        self.txt_iteration.setText(str(self.file.iteration))
        layout.addWidget(self.txt_iteration)

        if(self.file.idx_focused_image!=-1): 
            self.lbl_idx_focused_image=QLabel("Index of focused image: "+str(self.file.idx_focused_image))
            layout.addWidget(self.lbl_idx_focused_image)

        self.btn_save_properties = QPushButton("Continue")
        self.btn_save_properties.clicked.connect(self.save_properties)
        layout.addWidget(self.btn_save_properties)

    def save_properties(self):
        self.close()
    
    def closeEvent(self, event):
        try:
            self.file.magnification = float(self.txt_magnification.text())
            self.file.camera_increment = float(self.txt_camera_increment.text())
            self.file.axial_step = float(self.txt_axial_step.text())
            self.file.idx_background = int(self.txt_idx_background.text())
            self.file.idx_sample = int(self.txt_idx_sample.text())
            self.file.alpha=float(self.txt_alpha.text())
            self.file.lbda_TV=float(self.txt_lbda_TV.text())
            self.file.iteration=int(self.txt_iteration.text())
            
            if self.file.file!=None:
                if(self.file.magnification==-1 or self.file.axial_step==-1 or self.file.camera_increment==-1): raise Exception('Error: Unable to proceed. Please verify and adjust the parameter settings as needed.')
                calc.calculate_background_sample_stack(self.file)
                self.main_window.lbl_focused_image.setText("Index focused image: "+str(self.file.idx_focused_image))
                self.main_window.btn_show_select_window.setDisabled(False)
                self.main_window.show_raw_image()
            self.close()
        except Exception as e:
            self.main_window.error_message(e)
