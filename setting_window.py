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

        if(self.file.idx_focused_image!=-1): 
            self.lbl_idx_focused_image=QLabel("Index of focused image: "+str(self.file.idx_focused_image))
            layout.addWidget(self.lbl_idx_focused_image)

        self.btn_save_properties = QPushButton("Continue")
        self.btn_save_properties.clicked.connect(self.save_properties)
        layout.addWidget(self.btn_save_properties)

    def save_properties(self):
        self.file.magnification = float(self.txt_magnification.text())
        self.file.camera_increment = float(self.txt_camera_increment.text())
        self.file.axial_step = float(self.txt_axial_step.text())
        self.file.idx_background = int(self.txt_idx_background.text())
        self.file.idx_sample = int(self.txt_idx_sample.text())
        calc.calculate_background_sample_stack(self.file)
        self.close()
    
    def closeEvent(self, event):
        try:
            if(self.file.magnification==-1): raise Exception('Please set the parameters right!')
            self.main_window.show_raw_image()
            self.main_window.lbl_focused_image.setText("Index focused image: "+str(self.file.idx_focused_image_calc))
        except Exception as e:
            event.ignore()
            self.main_window.error_message(e)