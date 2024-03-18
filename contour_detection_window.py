# import matplotlib
# matplotlib.use('QtAgg')
# from PyQt6.QtWidgets import (
#     QPushButton, QWidget, QVBoxLayout, QSlider, QLabel
#     )
# from  MplCanvas import MplCanvas
# import calculation as calc
# from PyQt6.QtCore import Qt


# class ContourDetectionWindow(QWidget):
#     def __init__(self, phase_window):
#         super().__init__()        
#         self.setWindowTitle("Contour detection")

#         self.file=phase_window.file
#         self.mc = MplCanvas(self, width=500, height=500, dpi=100)
#         self.idx_hierarchy=0

#         self.layout = QVBoxLayout()
#         self.setLayout(self.layout)

#         self.sld_select_image = QSlider()
#         self.sld_select_image.setOrientation(Qt.Orientation.Horizontal)
#         self.sld_select_image.setMinimum(0)
#         self.sld_select_image.setMaximum(len(self.file.hierarchy[0]))
#         self.sld_select_image.valueChanged.connect(self.value_changed)
#         self.layout.addWidget(self.sld_select_image)

#         self.lbl_idx_of_hierarchy = QLabel("0")
#         self.lbl_idx_of_hierarchy.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.layout.addWidget(self.lbl_idx_of_hierarchy)


#         # self.btn_show_contourdetection = QPushButton("Calculate contours")
#         # self.btn_show_contourdetection.clicked.connect(self.show_contours)
#         # self.layout.addWidget(self.btn_show_contourdetection)



#         self.layout.addWidget(self.mc)


    
#     # def show_contours(self):
#     #     calc.contour_detection(self.file)
#     #     self.mc.draw_contours(self.file)

#     def value_changed(self, i):
#         self.mc.draw_previous_contour(self.file, i)
#         self.lbl_idx_of_hierarchy.setText(str(i))



