import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QLabel, QLineEdit
    )
from  MplCanvas import MplCanvas
import calculation as calc
# from contour_detection_window import ContourDetectionWindow


class PhaseWindow(QWidget):
    def __init__(self, file):
        super().__init__()        
        self.setWindowTitle("Phase calculation")

        self.file=file
        self.mc=MplCanvas(file, width=5, height=4, dpi=100)
        # self.contour_detection_window = ContourDetectionWindow(self.file)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel(text = "alpha in m^3/g:"))
        self.txt_alpha = QLineEdit()
        self.txt_alpha.setText(str(0.190 * 1e-6))
        layout.addWidget(self.txt_alpha)

        btn_show_image = QPushButton("Show raw image")
        btn_show_image.clicked.connect(self.show_image)
        layout.addWidget(btn_show_image)
    
        self.btn_calculate_phase = QPushButton("Calculate drymass")
        self.btn_calculate_phase.clicked.connect(self.show_phase_plot)
        layout.addWidget(self.btn_calculate_phase)
        self.btn_calculate_phase.setEnabled(False)
        
        layout.addWidget(self.mc)

        # btn_show_contour_detection_window = QPushButton("find contours")
        # btn_show_contour_detection_window.clicked.connect(self.show_contour_detection_window)
        # layout.addWidget(btn_show_contour_detection_window)
        # btn_show_contour_detection_window.setEnabled(False)


    def show_phase_plot(self):
        print("in phase window: ", self.file.x1, self.file.x2, self.file.y1, self.file.y2)
        if(self.file.x1==0 and self.file.x2==0 and self.file.y1==0 and self.file.y2==0): 
            self.btn_calculate_phase.setText("please select a section first!")
            return
        calc.calculate_phase(self.file)
        calc.calculate_drymass(self.file, float(self.txt_alpha.text()))
        self.mc.show_drymass(self.file)
    
    # def show_contour_detection_window(self):
    #     calc.contour_detection(self.file)
    #     self.contour_detection_window.show()
    
    def show_image(self):
        self.btn_calculate_phase.setEnabled(True)
        self.mc.check_z_position_images(self.file, self.file.idx_focused_image)