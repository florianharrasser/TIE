import numpy as np
import csv
import os
import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QGridLayout, QFileDialog, QMessageBox, QLabel
    )
from  MplCanvas import MplCanvas



class EvaluationWindow(QWidget):
    def __init__(self):
        super().__init__()        
        self.setWindowTitle("Evaluation")

        self.page_layout = QGridLayout()
        self.setLayout(self.page_layout)
        self.parameter_layout=QGridLayout()
        self.page_layout.addLayout(self.parameter_layout,0,0)

        self.btn_open_dialog = QPushButton("Upload file")
        self.btn_open_dialog.clicked.connect(self.open_dialog)
        self.parameter_layout.addWidget(self.btn_open_dialog,0,0)

        self.lbl_mean_cellmass=QLabel('Mean cell mass in ng: 0')
        self.parameter_layout.addWidget(self.lbl_mean_cellmass,0,1)

        self.mc1=MplCanvas(self,width=50, height=40, dpi=100)
        self.page_layout.addWidget(self.mc1,1,0)

       
    def open_dialog(self):
        try:
            path, _ = QFileDialog.getOpenFileNames(self, "Open File", "",  "CSV Files (*.csv)")
            cell_mass=[]
            cell_area=[]
            
            if path: 
                if path==None: raise Exception('Invalid input: No file selected. Please select a file.')
            
            for i in range(len(path)):
                if os.path.exists(path[i]):
                    csv_data = self.import_csv(path[i])
                    cell_mass.append(float(csv_data[48][1]))
                    cell_area.append(float(csv_data[64][1]))
            
            self.cell_mass=np.array(cell_mass)
            self.cell_area=np.array(cell_area)
            self.normalised_mass=(self.cell_mass/self.cell_area)
            
            self.page_layout.removeWidget(self.mc1)
            self.mc1=MplCanvas(self, width=5, height=4, dpi=100)
            self.page_layout.addWidget(self.mc1,1,0)
            self.mc1.evaluation(self.normalised_mass,'Mass/Area')

            self.lbl_mean_cellmass.setText('Mean areal mass density in ng/um: '+str(np.mean(self.normalised_mass)))

        except Exception as e:
            self.error_message(e)
    
       

    def import_csv(self, file_path):
        data = []
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                data.append(row)
        return data
    

    def error_message(self, message):
        QMessageBox.critical(self, "Error!", str(message), buttons=QMessageBox.StandardButton.Close)