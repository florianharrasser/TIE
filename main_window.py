import sys
import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QFileDialog,
    QVBoxLayout, QLabel, QHBoxLayout
    )
from daten import Daten
from setting_window import SettingWindow

from select_window import SelectWindow
import calculation as calc



class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(500, 200)
        self.setWindowTitle("Main Window")

        #initialisation of liffile and windows
        self.file = Daten()        
        self.setting_window = SettingWindow(self)
        self.select_window = SelectWindow(self.file)
        

        self.page_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.page_layout.addLayout(self.button_layout)

    	
        # opens the dialog to upload a .lif file
        btn_open_dialog = QPushButton("Upload a .lif file")
        btn_open_dialog.clicked.connect(self.open_dialog)
        self.button_layout.addWidget(btn_open_dialog)

        # opens a Window for entering the properties of the Experiment
        btn_show_setting_window = QPushButton("Settings")
        btn_show_setting_window.clicked.connect(self.show_setting_window)
        self.button_layout.addWidget(btn_show_setting_window)

        #displays the actual status if a file is uploaded
        self.lbl_statuts=QLabel("NO FILE UPLOADED")
        self.page_layout.addWidget(self.lbl_statuts)

        self.btn_show_select_window = QPushButton("PLEASE UPLOAD A FILE!")
        self.btn_show_select_window.setEnabled(False)
        self.btn_show_select_window.clicked.connect(self.show_select_window)
        self.page_layout.addWidget(self.btn_show_select_window)

        
        widget = QWidget()
        widget.setLayout(self.page_layout)
        self.setCentralWidget(widget)


    #pops up the dialog and saves the path in the Daten object
    def open_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "${HOME}",
            "LIF Files (*.lif)",
        )

        self.file.loadFile(filename)
        if(self.file.file != None): 
            self.btn_show_select_window.setText("Start Calculation")
            self.btn_show_select_window.setEnabled(True)
        
        lifProperties = []
        for idx, entry in enumerate(self.file.file.image_list):
            lifProperties.append(f"Index: {idx:<5}Name:{entry['name']:<60}Dimensions: {str(entry['dims']):<40}")
            self.lbl_statuts.setText("\n".join(lifProperties))


    def show_setting_window(self):
        self.setting_window.show()

    def show_select_window(self):
        calc.calculate_background_sample(self.file, self.file.idx_background, self.file.idx_sample)
        self.file.idx_focused_image=calc.find_focused_image(self.file)
        self.select_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = Main()
    main_gui.show()
    sys.exit(app.exec())