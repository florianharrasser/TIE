import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QLabel, QSlider 
    )
from  MplCanvas import MplCanvas
from PyQt6.QtCore import Qt
from phase_window import PhaseWindow
import calculation as calc


class SelectWindow(QWidget):
    def __init__(self, file):
        super().__init__()        
        self.setWindowTitle("Select File")

        self.file =file
        self.phase_window = PhaseWindow(self.file)
        self.mc = MplCanvas(self, width=50, height=40, dpi=100)
        self.idx_focused_image = 0
        #self.file.stack = self.file.sample/self.file.background

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)


        sld_select_image = QSlider()
        sld_select_image.setOrientation(Qt.Orientation.Horizontal)
        sld_select_image.setMinimum(0)
        sld_select_image.setMaximum(11)
        sld_select_image.valueChanged.connect(self.value_changed)
        self.layout.addWidget(sld_select_image)

        self.lbl_idx_of_image = QLabel("0")
        self.lbl_idx_of_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lbl_idx_of_image)

        self.layout.addWidget(self.mc)

        btn_save_idx_focused_image = QPushButton("choose this image")
        btn_save_idx_focused_image.clicked.connect(self.save_idx_focused_image)
        self.layout.addWidget(btn_save_idx_focused_image)

        # self.lbl_focused_image_calculated=QLabel(str(5))
        # self.layout.addWidget(self.lbl_focused_image_calculated)
       
    def value_changed(self, i):
        self.mc.check_z_position_images(self.file, i)
        self.lbl_idx_of_image.setText(str(i))
        self.idx_focused_image = i
    
    def save_idx_focused_image(self):
        self.file.idx_focused_image = self.idx_focused_image
        self.phase_window.show()
        self.close()