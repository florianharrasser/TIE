import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QLabel, QSlider, QGridLayout
    )
from  MplCanvas import MplCanvas
from PyQt6.QtCore import Qt


class SelectWindow(QWidget):
    def __init__(self, file, main_window, len_sample):
        super().__init__()        
        self.setWindowTitle("Select File")

        self.file =file
        self.mc = MplCanvas(self, self.file, False, False, width=50, height=40, dpi=100)
        self.len_sample=len_sample-1
        self.main_window=main_window

        self.page_layout = QGridLayout()
        self.setLayout(self.page_layout)

        self.lbl_focused_image_calc=QLabel("Calculated focused image: " +str(self.file.idx_focused_image_calc))
        self.page_layout.addWidget(self.lbl_focused_image_calc, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        self.page_layout.addWidget(self.mc,1,0,3,1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_select_image_up=QPushButton("^")
        self.btn_select_image_up.clicked.connect(self.select_image_up)
        self.btn_select_image_up.setFixedSize(20, 20)
        self.page_layout.addWidget(self.btn_select_image_up, 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.sld_select_image=QSlider()
        self.sld_select_image.setOrientation(Qt.Orientation.Vertical)
        self.sld_select_image.setMinimum(0)
        self.sld_select_image.setMaximum(self.len_sample)
        self.sld_select_image.setValue(self.file.idx_focused_image)
        self.sld_select_image.valueChanged.connect(self.value_changed)
        self.page_layout.addWidget(self.sld_select_image,2, 1)

        self.btn_select_image_down=QPushButton("v")
        self.btn_select_image_down.clicked.connect(self.select_image_down)
        self.btn_select_image_down.setFixedSize(20, 20)
        self.page_layout.addWidget(self.btn_select_image_down, 3, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
    
        self.lbl_idx_of_image=QLabel("0")
        self.page_layout.addWidget(self.lbl_idx_of_image, 4, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_save_idx_focused_image=QPushButton("Choose this image")
        self.btn_save_idx_focused_image.clicked.connect(self.save_idx_focused_image)
        self.page_layout.addWidget(self.btn_save_idx_focused_image, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
       
    def value_changed(self, i):
        self.mc.show_focused_image('Raw image', self.file.pixel_size, self.file.sample[i])
        self.lbl_idx_of_image.setText(str(i))
        self.idx_focused_image=i
    
    def select_image_up(self):
        self.sld_select_image.setValue(self.sld_select_image.value()+1)
        self.lbl_idx_of_image.setText(str(self.sld_select_image.value()))

    def select_image_down(self):
        self.sld_select_image.setValue(self.sld_select_image.value()-1)
        self.lbl_idx_of_image.setText(str(self.sld_select_image.value()))
        self.idx_focused_image=self.sld_select_image.value()
    
    def save_idx_focused_image(self):
        self.file.idx_focused_image=self.idx_focused_image
        self.close()

    def closeEvent(self, event):
        self.main_window.show_raw_image()
        self.main_window.lbl_focused_image.setText("Index focused image: "+str(self.file.idx_focused_image))