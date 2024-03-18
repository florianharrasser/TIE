import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QLineEdit,  QLabel
    )




class SettingWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.resize(300, 100)
        self.setWindowTitle("Properties")

        self.file=main_window.file

        layout = QVBoxLayout()
        self.setLayout(layout)
      
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

        self.btn_save_properties = QPushButton("Save")
        self.btn_save_properties.clicked.connect(self.save_properties)
        layout.addWidget(self.btn_save_properties)


    def save_properties(self):
        self.file.magnification = float(self.txt_magnification.text())
        self.file.camera_increment = float(self.txt_camera_increment.text())
        self.file.axial_step = float(self.txt_axial_step.text())
        self.file.idx_background = float(self.txt_idx_background.text())
        self.file.idx_sample = float(self.txt_idx_sample.text())
        self.close()
