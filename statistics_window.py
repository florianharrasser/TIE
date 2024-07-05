import matplotlib
matplotlib.use('QtAgg')
from daten import file
import os
import csv
import numpy as np
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QLineEdit,  QLabel, QGridLayout, QFileDialog, QFrame, QCheckBox, QMessageBox
    )
import calculation as calc
from PyQt6.QtGui import  QIntValidator
from MplCanvas import MplCanvas
import time


class StatisticWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 100)
        self.setWindowTitle("Statistics")

        self.directory_path=''
        self.fft=None
        self.tv=None
        self.shift=None
        self.shift_contour=np.array(file.selected_contour[0])

        self.page_layout = QGridLayout()
        self.setLayout(self.page_layout)
        

        #initializing the fields for parameter
        self.parameter_tv_layout=QGridLayout()
        self.page_layout.addLayout(self.parameter_tv_layout,0,0)
        
        self.parameter_fft_layout=QGridLayout()
        self.page_layout.addLayout(self.parameter_fft_layout,1,0)

        self.parameter_shift_layout=QGridLayout()
        self.page_layout.addLayout(self.parameter_shift_layout,2,0)

        self.button_layout=QGridLayout()
        self.page_layout.addLayout(self.button_layout,3,0)

        #initialize frames
        self.init_parameter_tv_frame()
        self.init_parameter_fft_frame()
        self.init_parameter_shift_frame()
        self.init_button_layout_frame()

    def init_parameter_tv_frame(self):
        frame=QFrame()
        frame_layout=QGridLayout(frame)

        self.tv_title=QLabel("Parameters for TV calculation")   
        self.do_tv_calculation=QCheckBox()    
        self.do_tv_calculation.setFixedSize(30,30) 
        frame_layout.addWidget(self.tv_title, 0,0)
        frame_layout.addWidget(self.do_tv_calculation,0,1)

        self.tv_lambda=QLabel("Lambda values:")        
        self.tv_lambda_input=QLineEdit()
        self.tv_lambda_input.setPlaceholderText("e.g. 1e-10 1e-20 0.001")
        
        frame_layout.addWidget(self.tv_lambda,1,0)
        frame_layout.addWidget(self.tv_lambda_input,1,1)

        self.tv_iteration=QLabel("Iteration values:")
        self.tv_iteration_input=QLineEdit()
        self.tv_iteration_input.setPlaceholderText("e.g. 10 50 100")
        frame_layout.addWidget(self.tv_iteration,2,0)
        frame_layout.addWidget(self.tv_iteration_input,2,1)

        self.parameter_tv_layout.addWidget(frame,0,0)
        
    def init_parameter_fft_frame(self):
        frame=QFrame()
        frame_layout=QGridLayout(frame)
        
        self.fft_title=QLabel("Parameter for FFT:")
        self.do_fft_calculation=QCheckBox()
        frame_layout.addWidget(self.fft_title,0,0)
        frame_layout.addWidget(self.do_fft_calculation,0,1)

        self.fft_axial_step=QLabel("Axial step values:")
        self.fft_axial_step_input=QLineEdit()        
        frame_layout.addWidget(self.fft_axial_step,1,0)
        frame_layout.addWidget(self.fft_axial_step_input,1,1)        

        self.parameter_fft_layout.addWidget(frame,1,0)

    def init_parameter_shift_frame(self):
        frame=QFrame()
        frame_layout=QGridLayout(frame)

        self.shift_title=QLabel("Parameter for shifting")
        frame_layout.addWidget(self.shift_title,0,0)

        self.parameter_coordinate=QLabel("Coordinate")
        self.parameter_start=QLabel("Start Value")
        self.parameter_end=QLabel("End Value")
        self.parameter_step=QLabel("Steps")
        frame_layout.addWidget(self.parameter_coordinate,1,0)
        frame_layout.addWidget(self.parameter_start,1,1)
        frame_layout.addWidget(self.parameter_end,1,2)
        frame_layout.addWidget(self.parameter_step,1,3)

        self.x1_title=QLabel("x1:")
        self.x1_start=QLineEdit()
        self.x1_start.setValidator(QIntValidator())
        self.x1_start.setText(str(0))
        
        
        self.x1_end=QLineEdit()
        self.x1_end.setText('200')
        self.x1_end.setValidator(QIntValidator())
        
        self.x1_step=QLineEdit()
        self.x1_step.setValidator(QIntValidator())
        self.x1_step.setText('50')
        self.do_x1=QCheckBox()        
        frame_layout.addWidget(self.x1_title,2,0)
        frame_layout.addWidget(self.x1_start,2,1)
        frame_layout.addWidget(self.x1_end,2,2)
        frame_layout.addWidget(self.x1_step,2,3)
        frame_layout.addWidget(self.do_x1,2,4)

        self.x2_title=QLabel("x2:")
        self.x2_start=QLineEdit()
        self.x2_start.setValidator(QIntValidator())
        self.x2_end=QLineEdit()
        self.x2_end.setValidator(QIntValidator())
        self.x2_step=QLineEdit()
        self.x2_step.setValidator(QIntValidator())
        self.do_x2=QCheckBox()
        frame_layout.addWidget(self.x2_title,3,0)
        frame_layout.addWidget(self.x2_start,3,1)
        frame_layout.addWidget(self.x2_end,3,2)
        frame_layout.addWidget(self.x2_step,3,3)
        frame_layout.addWidget(self.do_x2,3,4)

        self.y1_title=QLabel("y1:")
        self.y1_start=QLineEdit()
        self.y1_start.setValidator(QIntValidator())
        self.y1_end=QLineEdit()
        self.y1_end.setValidator(QIntValidator())
        self.y1_step=QLineEdit()
        self.y1_step.setValidator(QIntValidator())
        self.do_y1=QCheckBox()
        frame_layout.addWidget(self.y1_title,4,0)
        frame_layout.addWidget(self.y1_start,4,1)
        frame_layout.addWidget(self.y1_end,4,2)
        frame_layout.addWidget(self.y1_step,4,3)
        frame_layout.addWidget(self.do_y1,4,4)

        self.y2_title=QLabel("y2:")
        self.y2_start=QLineEdit()
        self.y2_start.setValidator(QIntValidator())
        self.y2_end=QLineEdit()
        self.y2_end.setValidator(QIntValidator())
        self.y2_step=QLineEdit()
        self.y2_step.setValidator(QIntValidator())
        self.do_y2=QCheckBox()
        frame_layout.addWidget(self.y2_title,5,0)
        frame_layout.addWidget(self.y2_start,5,1)
        frame_layout.addWidget(self.y2_end,5,2)
        frame_layout.addWidget(self.y2_step,5,3)
        frame_layout.addWidget(self.do_y2,5,4)

        self.parameter_shift_layout.addWidget(frame, 2,0)

    def init_button_layout_frame(self):
        frame=QFrame()
        frame_layout=QGridLayout(frame)

        self.btn_start=QPushButton("Start")
        self.btn_start.clicked.connect(self.start_statistics)
        frame_layout.addWidget(self.btn_start,0,0)

        self.button_layout.addWidget(frame,3,0)

    def start_statistics(self):
        try:
            self.fft=self.evaluate_entries_fft()
            self.tv=self.evaluate_entries_tv()
            self.shift=self.evaluate_entries_shift()
            

            path_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
            if not path_dir:
                raise Exception("No valid path")

            self.directory_path = os.path.join(path_dir, str(file.filename.replace('/', '_').replace(' ', '_')))
            os.makedirs(self.directory_path, exist_ok=True)

            self.save_metadata()
            
            start_time=time.time()
            self.shift_imagesize()
            end_time=time.time()
            duration=end_time-start_time
            print('------------------------------------------------------------------')
            print(f'Evaluation finished in : {duration/60}min {(duration)%60}s')
            print('------------------------------------------------------------------')
        except Exception as e:
            print(f'ERROR: {e}')

    #Statistic functions: FFT, TV-regularization, shifting
    def statistics_fft(self):
        axial_step_values=self.fft

        if not axial_step_values:
            return
        
        for i in axial_step_values:
            file.axial_separation=i

            file_name=file.filename+'_'+'FFT'+'_'+str(file.axial_separation)+'_'+str(file.cell_index)+'_'+str(file.dx1)+'_'+str(file.dx2)+'_'+str(file.dy1)+'_'+str(file.dy2)
            clean_filename=file_name.replace('/', '_').replace(' ', '_')

            calc.calculate_opl_fft(True)   
            self.save_mass_contour_images(clean_filename)   

            # Saving the calculated data            
            self.save_csv(clean_filename)            
            print(clean_filename)
    
    def statistics_tv(self):   
        lambda_values=self.tv[0]
        iteration_values=self.tv[1]

        for l in lambda_values:
            file.lbda_TV=l
            for i in iteration_values:
                file.iteration=i
                file_name=file.filename+'_'+'TvNorm'+'_'+str(file.lbda_TV)+'_'+str(file.iteration)+'_'+str(file.cell_index)+'_'+str(file.dx1)+'_'+str(file.dx2)+'_'+str(file.dy1)+'_'+str(file.dy2)             
                clean_filename=file_name.replace('/', '_').replace(' ', '_')                
        
                calc.calculate_opl_tv(True)                
                self.save_mass_contour_images(clean_filename)                

                # Saving the calculated data                
                self.save_csv(clean_filename)
                print(clean_filename)
           
    def shift_imagesize(self):
        if self.shift:
            x_neg_values, x_pos_values, y_pos_values, y_neg_values=self.shift

            for x_neg in range(x_neg_values[0],x_neg_values[1],x_neg_values[2]):
                for x_pos in range(x_pos_values[0],x_pos_values[1],x_pos_values[2]):
                    for y_neg in range(y_neg_values[0],y_neg_values[1],y_neg_values[2]):
                        for y_pos in range(y_pos_values[0],y_pos_values[1],y_pos_values[2]): 

                            file.dx1, file.dx2, file.dy1, file.dy2 =x_neg, x_pos, y_neg, y_pos                            
                            # Reshape to a 2D array of shape (n, 2)
                            contour_reshaped = self.shift_contour.reshape(-1, 2)

                            # Apply the shift
                            shifted_contour = contour_reshaped + [file.dx1, file.dy1]

                            # Reshape back to the original shape (n, 1, 2)
                            file.selected_contour=[]
                            file.selected_contour.append(shifted_contour.reshape(-1, 1, 2))
                
                            file.selected_stack = file.stack[:,file.y1-y_neg:file.y2+y_pos,file.x1-x_neg:file.x2+x_pos].copy()
                            file.raw_image=file.sample[1][file.y1-y_neg:file.y2+y_pos,file.x1-x_neg:file.x2+x_pos].copy()
                            
                            if self.fft:
                                self.statistics_fft()

                            if self.tv:
                                self.statistics_tv()

    #evaluation functions for the right entries for the statistic functions    
    def evaluate_entries_shift(self):
        def update_values(check, start, end, step, file_dim, label):
            if check.isChecked():
                start_val = int(start.text())
                end_val = int(end.text())
                step_val = int(step.text())

                if (file_dim - start_val) >= 0:
                    return [start_val, end_val, step_val]
                else:
                    raise Exception(f'{label} would exceed the image')
                
            return [0, 1, 1]

        try:
            x_neg = update_values(self.do_x1, self.x1_start, self.x1_end, self.x1_step, file.x1, 'x1')
            x_pos = update_values(self.do_x2, self.x2_start, self.x2_end, self.x2_step, file.x2, 'x2')
            y_neg = update_values(self.do_y1, self.y1_start, self.y1_end, self.y1_step, file.y1, 'y1')
            y_pos = update_values(self.do_y2, self.y2_start, self.y2_end, self.y2_step, file.y2, 'y2')

            return x_neg, x_pos, y_neg, y_pos

        except Exception as e:
            print(f'Adjust the boundaries, {e}')
            return None
        
    def evaluate_entries_tv(self):
        if not self.do_tv_calculation.isChecked():
            return None
    
        tv_lambda_values=[float(x) for x in self.tv_lambda_input.text().split()]
        tv_iteration_values=[int(x) for x in self.tv_iteration_input.text().split()]

        return tv_lambda_values, tv_iteration_values

    def evaluate_entries_fft(self):
        if not self.do_fft_calculation.isChecked():
            return
        
        #Calculatesa maximal axial distance
        if(file.idx_focused_image<(len(file.sample)/2)):
            max_axial_distance=file.idx_focused_image
        else: 
            max_axial_distance=len(file.sample)-file.idx_focused_image-1

        fft_axial_step_values=[int(x) for x in self.fft_axial_step_input.text().split()]
        
        if max_axial_distance<max(fft_axial_step_values):
            raise Exception(f'Axial distance to big! Maximal axial distsance: {max_axial_distance}')
            
        else:
            return fft_axial_step_values



    def save_csv(self, filename):
        csv_path = os.path.join(self.directory_path, 'Data')
        os.makedirs(csv_path, exist_ok=True)        
        csv_path=csv_path+'/'+filename+'.csv'
        with open(csv_path, 'w') as files:
            csv_writer = csv.writer(files)
            file.write_csv(csv_writer)

    def save_metadata(self):
        path=self.directory_path

        directory_path=path+'/'+'metadata.csv'
        filename_to_save=file.filename.replace('/', '_').replace(' ', '_')

        # Check if the file exists and open in the appropriate mode
        if os.path.isfile(directory_path):
            with open(directory_path,'r', newline='') as csvfile:
                csv_reader=csv.reader(csvfile)
                existing_filenames={row[0] for row in csv_reader}
            
            #check if in the existing metadat is already the filename
            if filename_to_save in existing_filenames:
                # right indexing of the file, if more then one cell of the image gets calculated
                file.cell_index+=1
                return
            else:
                mode = 'a'
        else:
            mode = 'w'

        # Adds the filename/creates new metadata
        with open(directory_path, mode, newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([filename_to_save])

    def save_mass_contour_images(self, filename):
            calc.opl_dry_mass()
            shift_aktiv=(self.do_x2.isChecked() or self.do_x1.isChecked() or self.do_y1.isChecked() or self.do_y2.isChecked())

            if not shift_aktiv:            
                title=f'Mass {file.calculation_option}: {np.round(file.entire_mass,3)}'
                mc2=MplCanvas(self, width=5, height=4, dpi=100)
                mc2.draw_selected_contour_with_colorbar(title, True, True)
                
            else:
                calc.contour_mass()
                calc.contourline_mean_mass()
                file.selected_contour_index=1

                title=f'Mass {file.calculation_option} in ng: {round(file.contour_inside_mass-file.contourline_mean_mass,3)}'
                mc2=MplCanvas(mainWindow=None, width=5, height=4, dpi=100)
                mc2.draw_selected_contour_with_colorbar(title, True)
                #  #keine Ahnung warum ich das brauche?
            
            images_path = os.path.join(self.directory_path, 'Images')
            os.makedirs(images_path, exist_ok=True)
            mc2.save_figure(images_path+'/'+filename)

    def show_message_box(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
