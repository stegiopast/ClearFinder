#from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

import sys
print(sys.version)
import os
import pathlib
from pathlib import Path
import re
import shutil
import pandas as pd
import numpy as np
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import Qt
from cellfinder_core.train.train_yml import run as run_training
from cellfinder_core.main import main as cellfinder_run
from cellfinder_core.tools.IO import read_with_dask
import tifffile
from tifffile import imread,imwrite
from imlib.IO.cells import save_cells
from PIL import Image
from natsort import natsorted
from skimage.transform import rescale,resize, downscale_local_mean
from skimage.util import img_as_uint

from plotnine import ggplot, aes, geom_bar, coord_flip


def on_top_clicked():
    alert = QMessageBox()
    alert.setText("You moved to the top !")
    alert.exec()

class Rename_Box(QWidget):
    def __init__(self, filename_to_check, acceptor, position, _path):
        super().__init__()
        self.path = _path
        self.acceptor = acceptor
        self.position = position
        self.rename_box = None
        self.setWindowTitle("Cellfinder GUI")
        self.filename_to_check = filename_to_check
        self.channel_chosen = "C01";
        self.shift_bar = QLineEdit("0")
        self.accept = QPushButton("Accept")
        self.reject = QPushButton("Reject and shift")
        self.quit_renaming = QPushButton("Quit Renaming")
        self.layout = QGridLayout()
        self.update_layout() 
        self.setLayout(self.layout)



    def update_layout(self):
        self.int_shift = int(self.shift_bar.text())
        self.new_position = self.position + self.int_shift
        self.update(self.new_position)
        print("Filename: ",self.filename_to_check[self.position:len(self.filename_to_check)])
        print("Current Filename: ",self.current_filename)
        print(self.position)
        inner_layout = QGridLayout()
        inner_layout.addWidget(QLabel("Current output Filename:"),0,0)
        inner_layout.addWidget(QLabel(self.current_filename),0,1)
        inner_layout.addWidget(QLabel("      "),1,0)
        inner_layout.addWidget(QLabel("Does filename not fit to template 001_C01.tif - 9999_C01.tif ?"),2,0)
        inner_layout.addWidget(QLabel("Provide shift (+ and - allowed) and Reject:"), 3,0)
        inner_layout.addWidget(self.shift_bar, 3,1)
        inner_layout.addWidget(self.reject,3,2)
        inner_layout.addWidget(QLabel("      "),4,0)
        inner_layout.addWidget(QLabel("Does filename fit ?"),5,0)
        inner_layout.addWidget(QLabel("Press accept:"), 6,0)
        inner_layout.addWidget(self.accept,6,1)
        inner_layout.addWidget(QLabel("      "),7,0)
        inner_layout.addWidget(QLabel("Doesn't the filename fit at all?"),8,0)
        inner_layout.addWidget(QLabel("Press Quit:"),9,0)
        inner_layout.addWidget(self.quit_renaming,9,1)

        self.deleteItemsOfLayout(self.layout)


        self.layout.addLayout(inner_layout,0,0)
        return self.layout
         

        


    def update(self,current_position):
            self.position = current_position
            self.current_filename = self.filename_to_check[self.position:len(self.filename_to_check)]


    def deleteItemsOfLayout(self,layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteItemsOfLayout(item.layout())
    
    def perform_cut(self):
        print("path:",self.path)
        counter = 0

        for file in pathlib.Path(self.path).iterdir():
            if file.is_file():
                print(file.stem)
                old_name = file.stem + ".tif"
                new_name = old_name[self.position:len(old_name)]
                dir = file.parent
            
                new_obj = re.match(r'^[0-9]{3}_',new_name)
                if new_obj:
                    new_name = "Z0" + new_name
                else:
                    new_obj = re.match(r'[0-9]',new_name)
                    if new_obj:
                        new_name = "Z" + new_name
                print(new_name)
                file.rename(pathlib.Path(dir, new_name))

            else:
                if counter == 0:
                    alert = QMessageBox()
                    alert.setText("You have more than one channel, please select a channel")
                    alert.exec()
                    counter += 1



    

class Main_Window(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cellfinder GUI")
        self.resize(1600,800)
        layout = QVBoxLayout()
        self.setLayout(layout)
        tabs = QTabWidget()
        tabs.addTab(self.rename_layout(), "Determine Path and Rename Filenames")
        tabs.addTab(self.preprocess_layout(), "Preprocessing")
        tabs.addTab(self.cd_layout(),"Cell Detection | Assignment")
        tabs.addTab(self.training_layout(),"Train Network")  
        tabs.addTab(self.analysing_output(), "Analyzing Results")
        layout.addWidget(tabs)
        self.my_working_directory = ""
        self.channel_chosen = ""
        
    def warning_ws(self):
        alert = QMessageBox()
        alert.setText("You didn't choose a sample yet! Please choose a sample.")
        alert.exec()
        


    def init_workspace(self,path = '/home/cellfinder_data',channel = 0):
        if channel == 1:
            channel_str = "C01"

        elif channel == 2:
            channel_str = "C02"

        else:
            channel_str = ""

        if os.path.exists(path + '/Signal/' + channel_str):
            self.channel_chosen = channel_str

        else:
            self.channel_chosen = ""
            alert = QMessageBox()
            alert.setText("Path does not exist!")
            alert.exec()
            if not os.path.exists(path + '/Signal'):    
                alert2 = QMessageBox()
                alert2.setText("In this folder there is no Signal folder existent! Please choose different sample!")
                alert2.exec()

        my_working_directory = path

        if os.path.exists(my_working_directory):
            self.my_working_directory = my_working_directory
            print("Working dir:",self.my_working_directory)
            print("Channel chosen:", self.channel_chosen)
            return my_working_directory
        else:
            print("Path does not exist!")


    def resize_pictures(self, _voxel_size_signal_x=5,_voxel_size_signal_y=2,_voxel_size_signal_z=2,
                              _voxel_size_auto_x = 5,_voxel_size_auto_y = 2,_voxel_size_auto_z = 2):

        if self.my_working_directory != "":
            filepath = self.my_working_directory;
            print(filepath)
            print(os.path.exists(filepath))
            filepath_auto = str(filepath + '/Auto/') 
            print(filepath_auto)
            if self.channel_chosen == "":
                filepath_signal = str(filepath + '/Signal/')
                print(filepath_signal)
            else:
                filepath_signal = str(filepath + '/Signal/' + self.channel_chosen + '/')

            filenames_auto = []
            filenames_signal = []

            for base,dirs,files in os.walk(filepath_auto):
                filenames_auto = files

            for base,dirs,files in os.walk(filepath_signal):
                filenames_signal = files

            print(len(filenames_auto),len(filenames_signal))
            
            filenames_auto = natsorted(filenames_auto, reverse = False)
            filenames_signal = natsorted(filenames_signal, reverse = False)

            #print("Filenames Auto ",filenames_auto,"\nFilenames Signal:",filenames_signal)

            if len(filenames_auto) != len(filenames_signal):
                difference = abs(len(filenames_auto) - len(filenames_signal))
                if len(filenames_auto) > len(filenames_signal):
                    longer_array = filenames_auto
                    shorter_array = filenames_signal
                    longer_str = "/Auto"
                else:
                    longer_array = filenames_signal
                    shorter_array = filenames_auto
                    longer_str = "/Signal"
        
                print(longer_array)

                if (difference % 2) == 0:
                    front = difference // 2
                    back = difference // 2
                else:
                    front = difference // 2 + 1
                    back = difference // 2
        
                if not os.path.exists(filepath + longer_str +"_moved"):
                    os.mkdir(filepath +  longer_str + "_moved")
                else:
                    print("File existed")

                for i in range(front):
                    print(longer_array[0])
                    #os.rename(filepath + longer_str + "/" + longer_array[0], filepath + longer_str + "_moved/" + longer_array[0])
                    os.remove(filepath + longer_str + "/" + longer_array[0])
                    longer_array.pop(0)

                for j in range(0,back):
                    print(longer_array[-1])
                    #os.rename(filepath + longer_str + "/" + longer_array[-1], filepath + longer_str + "_moved/" + longer_array[-1])
                    os.remove(filepath + longer_str + "/" + longer_array[-1])
                    longer_array.pop()

                    print("Same lenght now ?:", len(filenames_auto) == len(filenames_signal))

            else:
                print("Lengths are equal\n")

            counter = 0
            for i,j in zip(filenames_auto,filenames_signal):
               
                #im1 = img_as_uint(filepath_auto + i)
                #im2 = img_as_uint(filepath_auto + j)

                im1 = Image.open(filepath_auto + i)
                im2 = Image.open(filepath_signal + j)

                if im1.size != im2.size:
                    print("I'm in if")

                    pixel_growth_x_signal = im2.size[0] / 2050#im1.size[0]
                    pixel_growth_y_signal = im2.size[1] / 3500#im1.size[1]
            
                    pixel_growth_x_auto = im1.size[0] / 2050
                    pixel_growth_y_auto = im1.size[1] / 3500

                    print("Image 1 size",im1.size)
                    print("Image2 size",im2.size)
                    #new_signal_size_x =  (im1.size[0] / im2.size[0]) * im2.size[0]
                    #new_signal_size_y = (im1.size[1] / im2.size[1]) * im2.size[1]
            
                    new_size = (3500,2050)
            
            
                    im1 = np.asarray(im1)
                    im2 = np.asarray(im2)             
            
                    print("Image1 old shape: ", im1.shape)
                    print("Image2 old shape: ", im2.shape)
            
                    im1 = resize(im1,new_size)
                    im2 = resize(im2,new_size)   
        
                    print("Image 1 new shape: ", im1.shape)
                    print("Image 2 new shape: ", im2.shape)

                    im1 = img_as_uint(im1)
                    im2 = img_as_uint(im2)
                        
                    im1 = Image.fromarray(im1)
                    im2 = Image.fromarray(im2)
            
                    print("Image 1 new size",im1.size)
                    print("Image 2 new size",im2.size)
            
                    im1.save(filepath_auto + i)
                    im2.save(filepath_signal + j)
            
                    if counter < 1:
                        if not os.path.exists(self.my_working_directory +"/" + self.channel_chosen + "_voxel_size_signal"):

                            os.mkdir(self.my_working_directory + "/" + self.channel_chosen + "_voxel_size_signal")
            
                            voxel_filepath = self.my_working_directory +"/" + self.channel_chosen + "_voxel_size_signal"
                            new_voxel_size_x = _voxel_size_signal_x * pixel_growth_x_signal
                            new_voxel_size_y = _voxel_size_signal_y * pixel_growth_y_signal
                            new_voxel_size_z = _voxel_size_signal_z 

                            with open(voxel_filepath + "/voxel_sizes.txt", "w") as file:
                                file.write(str(new_voxel_size_x))
                                file.write(",")
                                file.write(str(new_voxel_size_y))
                                file.write(",")
                                file.write(str(new_voxel_size_z))
                
                        if not os.path.exists(self.my_working_directory+"/voxel_size_auto"):
                            os.mkdir(self.my_working_directory + "/voxel_size_auto")
            
                            voxel_filepath = self.my_working_directory+ "/voxel_size_auto";
                            new_voxel_size_x = _voxel_size_auto_x * pixel_growth_x_auto
                            new_voxel_size_y = _voxel_size_auto_y * pixel_growth_y_auto
                            new_voxel_size_z = _voxel_size_auto_z

                            with open(voxel_filepath+"/voxel_sizes.txt", "w") as file:
                                file.write(str(new_voxel_size_x))
                                file.write(",")
                                file.write(str(new_voxel_size_y))
                                file.write(",")
                                file.write(str(new_voxel_size_z))

                else:
                    print("I'm in else")

                    if counter < 1:
                        if not os.path.exists(self.my_working_directory +"/" + self.channel_chosen + "_voxel_size_signal"):
                            os.mkdir(self.my_working_directory +"/" + self.channel_chosen + "_voxel_size_signal")
            
                            voxel_filepath = self.my_working_directory +"/" + self.channel_chosen + "_voxel_size_signal";
                            new_voxel_size_x = _voxel_size_signal_x
                            new_voxel_size_y = _voxel_size_signal_y
                            new_voxel_size_z = _voxel_size_signal_z

                            with open(voxel_filepath + "/voxel_sizes.txt", "w") as file:
                                file.write(str(new_voxel_size_x))
                                file.write(",")
                                file.write(str(new_voxel_size_y))
                                file.write(",")
                                file.write(str(new_voxel_size_z))
                
                        if not os.path.exists(self.my_working_directory+"/voxel_size_auto"):
                            os.mkdir(self.my_working_directory + "/voxel_size_auto")
            
                            voxel_filepath = self.my_working_directory+"/voxel_size_auto";
                            new_voxel_size_x = _voxel_size_auto_x
                            new_voxel_size_y = _voxel_size_auto_y
                            new_voxel_size_z = _voxel_size_auto_z

                            with open(voxel_filepath + "/voxel_sizes.txt", "w") as file:
                                file.write(str(new_voxel_size_x))
                                file.write(",")
                                file.write(str(new_voxel_size_y))
                                file.write(",")
                                file.write(str(new_voxel_size_z))

                counter += 1
                print("Finished work!")

        else:
            self.warning_ws()



    def detect_cells(self,_number_of_free_cpus=4,
                          _n_sds_above_mean_thresh=10,
                          _trained_model="",
                          _soma_diameter=16,
                          _xy_cell_size=6,
                          _z_cell_size=6,
                          _gaussian_filter=0.2,
                          _orientation = "asl",
                          _batch_size = 256):

        ##Basic comman for cellfinder
        if self.my_working_directory != "":

            basic_string = "cellfinder "
            
            if self.channel_chosen != "":
                filepath = self.my_working_directory + "/Signal/" + str(self.channel_chosen)
            else:
                filepath = self.my_working_directory + "/Signal"
            
            if os.path.exists(self.my_working_directory +"/" + self.channel_chosen + "_voxel_size_signal"):

                with open(self.my_working_directory +"/" + self.channel_chosen + "_voxel_size_signal/voxel_sizes.txt", "r") as file:
                    x = file.read().split(sep=",")
                    voxel_x = x[0]
                    voxel_y = x[1]
                    voxel_z = x[2]
                    print("Voxel X: ",voxel_x, " Voxel Y: ", voxel_y, "Voxel Z: ", voxel_z, "\n")

                ###Mandatory Signal folder path
                if self.channel_chosen != "":
                    signal_string = "-s " + str(self.my_working_directory) + "/Signal/" + str(self.channel_chosen) + " "
                else:
                    signal_string = "-s " + self.my_working_directory + "/Signal" + " "
                
                ###Mandatory Background folder path
                background_string = "-b " + self.my_working_directory + "/Auto" + " "
                
                ###Mandatory voxel sizes
                voxel_sizes_string = "-v " + str(voxel_x) + " " + str(voxel_y) + " " + str(voxel_z) + " "
                
                ###Threshold 
                threshold_string = "--threshold " + str(_n_sds_above_mean_thresh) + " "
                
                ###Trained model
                if _trained_model == "":
                    trained_model_string = ""
                else:
                    if os.path.exists(_trained_model):
                        trained_model_string = "--trained-model " + _trained_model_string + " "
                    else:
                        trained_model_string = ""
                        alert = QMessageBox()
                        alert.setText("Path to trained model does not exist!\n Process continued without trained model")

                ###Number of free CPUs
                cpu_string = "--n-free-cpus " + str(_number_of_free_cpus) + " "

                ###Soma diameter
                soma_diameter_string = "--soma-diameter " + str(_soma_diameter) + " "
               
                ###Cell size in XY Plane
                xy_cell_size_string = "--ball-xy-size " + str(_xy_cell_size) + " "
                
                ###Cell size in Z 
                z_cell_size_string = "--ball-z-size " + str(_z_cell_size) + " "
                
                ###Gaussian filter sigma 
                gaussian_filter_string = "--log-sigma-size " + str(_gaussian_filter) + " "
                
                ###Orientation
                orientation_string = "--orientation " + _orientation + " " 
                
                ###Batch size
                batch_size_string = "--batch-size " + str(_batch_size) + " "


                ###Output 
                output_string = "-o " + self.my_working_directory + " "


                ###Final command construction
                final_string = (basic_string +
                                signal_string + 
                                background_string +
                                voxel_sizes_string + 
                                threshold_string + 
                                trained_model_string +
                                cpu_string + 
                                soma_diameter_string +
                                xy_cell_size_string +
                                z_cell_size_string +
                                gaussian_filter_string +
                                batch_size_string +
                                orientation_string +
                                output_string) 

                ###Execute contructed command
                os.system(final_string)
           
            else:
                alert = QMessageBox()
                alert.setText("Please perform Preprocessing first!")
                alert.exec()
        else:
            self.warning_ws()



    def train_network(self, _yaml_files="",
                            _trained_model = "",
                            _continue_training=True, 
                            _test_fraction=0.1, 
                            _learning_rate=0.0001, 
                            _batch_size=32,
                            _epochs=1):

        if not os.path.exists(self.my_working_directory + "/" + self.channel_chosen + "_output_training"):

            os.mkdir(self.my_working_directory + "/" + self.channel_chosen + "_output_training")
            _output_directory = self.my_working_directory + "/" + self.channel_chosen + "_output_training"

            print("Output directory will be", _output_directory)

            home = Path.home()
            install_path = home / ".cellfinder"
            
            if _trained_model != "":
                run_training(output_dir=Path(_output_directory),
                             trained_model = _trained_model,
                             yaml_file=[Path(_yaml_files)],
                             install_path=install_path,
                             learning_rate=_learning_rate, 
                             continue_training=_continue_training,
                             test_fraction=_test_fraction,
                             batch_size=_batch_size,
                             save_progress=True,
                             epochs=_epochs)
            else:
                if os.path.exists(_output_directory):
                    run_training(output_dir=Path(_output_directory),
                                 yaml_file=[Path(_yaml_files)],
                                 install_path=install_path,
                                 learning_rate=_learning_rate,
                                 continue_training=_continue_training,
                                 test_fraction=_test_fraction,
                                 batch_size=_batch_size,
                                 save_progress=True,
                                 epochs=_epochs)
                else:
                    alert = QMessageBox()
                    alert.setText("Output directory already exists! Please save old output_training directory somewhere and remove it from this path!")
                    alert.exec()

        else:
            alert = QMessageBox()
            alert.setText("Output directory already exists! Please save old output_training directory somewhere and remove it from this path!")
            alert.exec()



    def rename_layout(self):

        def rename_files(_path, extend):     
            if os.path.exists(_path):
                pathlist = [_path + extend]
            
                ## Remove all the tabs in the filenames
                ## Iteration over each file in Auto and Signal directories
                ## Each filename-string is iterated and a new_name string without tabs is generated by skipping every " " in the old_name.
                ## The filename becomes then substituted by the new name 
                for i in pathlist:
                    for file in pathlib.Path(i).iterdir():
                        if file.is_file():
                            old_name = file.stem
                            print(file.stem)  
                            new_name = ""
                            for i in old_name:
                                if i != " ":
                                    new_name += i
                            new_name += ".tif"
                            dir = file.parent
                            file.rename(pathlib.Path(dir, new_name))



                ##Selecting the right range for each filename:
                for i in pathlist:
                    filename_list = [file for file in pathlib.Path(i).iterdir()]
                    first_file = filename_list[0]
                    first_filename = first_file.stem + ".tif"

                    size_bool = False
                    string_pos = 0

                    self.rename_box = Rename_Box(first_filename,size_bool,string_pos,i)
                    self.rename_box.show()


                    #self.rename_box.reject.clicked.connect(lambda: self.rename_box.update(False,self.rename_box.new_position))
                    self.rename_box.reject.clicked.connect(self.rename_box.update_layout)
                    self.rename_box.reject.clicked.connect(self.rename_box.repaint)


                    #reject.clicked.connect(self.close())
                    self.rename_box.accept.clicked.connect(self.rename_box.perform_cut)
                    self.rename_box.accept.clicked.connect(self.rename_box.close)

                    #Next line is implemented to quit the application in case a renaming is not possible. 
                    #self.rename_box.quit_renaming.clicked.connect(lambda: self.rename_box.update(False,4000000))
                    self.rename_box.quit_renaming.clicked.connect(self.rename_box.close)
                    
            else:
                alert = QMessageBox()
                alert.setText("Path does not exist!")
                alert.exec()        

                
        tab = QWidget()
        outer_layout = QVBoxLayout()
        inner_layout = QGridLayout()

        ## Widget for input path
        ws_path = QLabel("/home/cellfinder_data")
        choose_ws = QPushButton("Choose sample")
        channel_button = QComboBox()
        channel_button.insertItem(0,"")
        channel_button.insertItem(1,"C01")
        channel_button.insertItem(2,"C02")
        set_ws = QPushButton("Set workspace")
        rename_button1 = QPushButton("Rename files in Auto")
        rename_button2 = QPushButton("Rename files in Signal")
        
       
        ##Function for selection of working directory
        def choose_sample():
            path = QFileDialog.getExistingDirectory(self, "Choose sample data folder")
            if path != ('', ''):
                ws_path.setText(path)    
            else:
                ws_path.setText("")

        ##
        inner_layout.addWidget(QLabel("<b>Set Workspace:</b>"),0,0)
        inner_layout.addWidget(QLabel("Input path of interest:"),1,0)
        inner_layout.addWidget(ws_path,1,1)
        inner_layout.addWidget(channel_button,1,2)
        inner_layout.addWidget(set_ws,1,3)
        inner_layout.addWidget(rename_button1,1,4)
        inner_layout.addWidget(rename_button2,1,5)
        inner_layout.addWidget(choose_ws,2,1)
        inner_layout.addWidget(QLabel("      "),3,0)

        
        choose_ws.clicked.connect(lambda: choose_sample())
        set_ws.clicked.connect(lambda: self.init_workspace(ws_path.text(),channel_button.currentIndex()))
        rename_button1.clicked.connect(lambda: rename_files(_path = self.my_working_directory, extend='/Auto'))
        rename_button2.clicked.connect(lambda: rename_files(_path = self.my_working_directory, extend='/Signal/' + self.channel_chosen))
                

        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab




    def preprocess_layout(self):
            
        tab = QWidget()
        outer_layout = QVBoxLayout()
        inner_layout = QGridLayout()


        ### Widgets for determining voxel size
        voxel_size_signal_x = QLineEdit("5.00")
        voxel_size_signal_y = QLineEdit("2.00")
        voxel_size_signal_z = QLineEdit("2.00")
        voxel_size_auto_x = QLineEdit("5.00")
        voxel_size_auto_y = QLineEdit("2.00")
        voxel_size_auto_z = QLineEdit("2.00")

        ### Widgets for starting Prepprocessing
        start_preprocess_button = QPushButton("Start Preprocessing")


        ### Visualization of Widgets for preprocessing tab on GUI
        inner_layout.addWidget(QLabel("<b>Insert voxel sizes: <\b>"),0,0)
        
        inner_layout.addWidget(QLabel("Voxel size Signal X:"),1,0)
        inner_layout.addWidget(voxel_size_signal_x,1,1)
        
        inner_layout.addWidget(QLabel("Voxel size Signal Y:"),2,0)
        inner_layout.addWidget(voxel_size_signal_y,2,1)
        
        inner_layout.addWidget(QLabel("Voxel Size Signal Z:"),3,0)
        inner_layout.addWidget(voxel_size_signal_z,3,1)

        inner_layout.addWidget(QLabel("Voxel size Auto X:"),4,0)
        inner_layout.addWidget(voxel_size_auto_x,4,1)
        
        inner_layout.addWidget(QLabel("Voxel size Auto Y:"),5,0)
        inner_layout.addWidget(voxel_size_auto_y,5,1)
        
        inner_layout.addWidget(QLabel("Voxel Size Auto Z:"),6,0)
        inner_layout.addWidget(voxel_size_auto_z,6,1)

        
        inner_layout.addWidget(start_preprocess_button,7,0)

    
        ### Connection of button and preprocessing function 
        start_preprocess_button.pressed.connect(lambda: self.resize_pictures(_voxel_size_signal_x = float(voxel_size_signal_x.text()),
                                                                             _voxel_size_signal_y = float(voxel_size_signal_y.text()),
                                                                             _voxel_size_signal_z = float(voxel_size_signal_z.text()),
                                                                             _voxel_size_auto_x = float(voxel_size_auto_x.text()),
                                                                             _voxel_size_auto_y = float(voxel_size_auto_y.text()), 
                                                                             _voxel_size_auto_z = float(voxel_size_auto_z.text())))

        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab




    def cd_layout(self):
        tab = QWidget()
        outer_layout = QVBoxLayout()
        inner_layout = QGridLayout()


        ### Widgets for technical Technical Settings
        n_cpus = QLineEdit("4")
        
        ### Widgets for Parameters
        n_sds_above_mean = QLineEdit("10")
        soma_diameter = QLineEdit("16")
        xy_cell_size = QLineEdit("6")
        z_cell_size = QLineEdit("6")
        gaussian_filter = QLineEdit("0.2")
        
        ### Widget for trained model
        path = ""
        trained_model = QLabel()
        choose_model_button = QPushButton("Choose model")

        def choose_model():
            path = QFileDialog.getOpenFileName(self, "Choose a Model file (.h5)")
            if path != ('', ''):
                trained_model.setText(str(path[0]))
            else:
                trained_model.setText('')
        
        ### Widget for orientation

        orientation = QLineEdit("asl")

        ## Widget for starting cell detection
        start_cell_detection_button = QPushButton("Start Cell Detection")
       

        ## Widget for saving | loading settings
        config_path = QLineEdit("Insert filename extension")
        load_config_button = QPushButton("Load parameters")
        save_config_button = QPushButton("Safe parameters")



        ### Visualization of Widgets for cell detection tab on GUI      
        inner_layout.addWidget(QLabel("Number of cpus available:"),1,0)
        inner_layout.addWidget(n_cpus,1,1)
        inner_layout.addWidget(QLabel(" "),2,0)
        inner_layout.addWidget(QLabel("Lower Boundary measured in number of standarddeviations above mean illumination:"),3,0)
        inner_layout.addWidget(n_sds_above_mean,3,1)
        inner_layout.addWidget(QLabel("Mean soma diamter:"),4,0)
        inner_layout.addWidget(soma_diameter,4,1)
        inner_layout.addWidget(QLabel("Mean cell size in xy plane:"),5,0)
        inner_layout.addWidget(xy_cell_size,5,1)
        inner_layout.addWidget(QLabel("Mean cell size in z plane:"),6,0)
        inner_layout.addWidget(z_cell_size,6,1)
        inner_layout.addWidget(QLabel("Gaussian Filter:"),7,0)
        inner_layout.addWidget(gaussian_filter,7,1)
        inner_layout.addWidget(QLabel("Custom pretrained model:"),8,0)
        inner_layout.addWidget(trained_model,8,1)
        inner_layout.addWidget(choose_model_button,8,2)
        inner_layout.addWidget(QLabel("Choose brain orientation (anterior/posterior,superior/inferior,left/right)"),9,0)
        inner_layout.addWidget(orientation,9,1)
        

        inner_layout.addWidget(config_path,10,0)
        inner_layout.addWidget(load_config_button,10,1)
        inner_layout.addWidget(save_config_button,10,2)
        inner_layout.addWidget(start_cell_detection_button,10,3)


        ###

        def save_config(save_path):
            if not os.path.exists(save_path):    
                print(save_path)
                resample_variable_list = [n_cpus.text(),
                                          n_sds_above_mean.text(),
                                          soma_diameter.text(),
                                          xy_cell_size.text(),
                                          z_cell_size.text(),
                                          gaussian_filter.text(),
                                          trained_model.text(),
                                          orientation.text()]

                pd_df = pd.DataFrame([resample_variable_list], 
                                     index = [1], 
                                     columns = ["Number of CPUs", "Number SDS above mean",
                                                "Soma Diameter", "XY Plane Cell Size",
                                                "Z Plane Cell Size","Gaussian Filter",
                                                "Trained Model","Orientation"])
                pd_df.to_csv(save_path)
            else:
                alert = QMessageBox()
                alert.setText("File already exists!")
                alert.exec()
               
        def load_config(load_path):
            if os.path.exists(load_path):    
                print(load_path)
                pd_df = pd.read_csv(load_path, header = 0)
                n_cpus.setText(str(pd_df["Number of CPUs"][0]))
                n_sds_above_mean.setText(str(pd_df["Number SDS above mean"][0]))
                soma_diameter.setText(str(pd_df["Soma Diameter"][0]))
                xy_cell_size.setText(str(pd_df["XY Plane Cell Size"][0]))
                z_cell_size.setText(str(pd_df["Z Plane Cell Size"][0]))
                gaussian_filter.setText(str(pd_df["Gaussian Filter"][0]))
                trained_model.setText(str(pd_df["Trained Model"][0])) 
                orientation.setText(str(pd_df["Orientation"][0]))
            else:
                alert = QMessageBox()
                alert.setText("Path does not exist!")
                alert.exec()    


        
       ### Connection of Widgets with cell_detection functions 

       
        load_config_button.pressed.connect(lambda: load_config(load_path = os.getcwd() + "/cell_detection_" + config_path.text() + ".csv"))
        save_config_button.pressed.connect(lambda: save_config(save_path = os.getcwd() + "/cell_detection_" + config_path.text() + ".csv"))

        start_cell_detection_button.clicked.connect(lambda: self.detect_cells(_number_of_free_cpus=int(n_cpus.text()),
                                                                              _n_sds_above_mean_thresh=int(n_sds_above_mean.text()),
                                                                              _trained_model=str(trained_model.text()),
                                                                              _soma_diameter=int(soma_diameter.text()),
                                                                              _xy_cell_size=int(xy_cell_size.text()),
                                                                              _z_cell_size=int(z_cell_size.text()),
                                                                              _gaussian_filter=float(gaussian_filter.text()),
                                                                              _orientation = str(orientation.text())))
        
        choose_model_button.clicked.connect(lambda: choose_model())
        

        outer_layout.addLayout(inner_layout)       
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab
    
    def analysing_output(self):
        tab = QWidget()
        outer_layout = QVBoxLayout()
        inner_layout = QGridLayout()


        result_file = QLineEdit("")
        choose_resultfile_button = QPushButton("Load Resultfile")

        load_barplot_button = QPushButton("Load Barplot")

        inner_layout.addWidget(load_barplot_button,1,0)
        inner_layout.addWidget(result_file,2,0)
        inner_layout.addWidget(choose_resultfile_button,2,1)

        def choose_resultfile():
            path = QFileDialog.getOpenFileName(self, "Choose Resultfile.csv")
            if not path[0].endswith('.csv'):
                alert = QMessageBox()
                alert.setText("You need to choose a .csv file")
                alert.exec()

            else:
                result_file.setText(str(path[0]))


        def load_barplot():
            if not os.path.exists(os.getcwd()+"/Nils/Result_Graph_Directory"):
               os.makedirs(os.getcwd()+"/Nils/Result_Graph_Directory")
            
            if not result_file.text():
                alert = QMessageBox()
                alert.setText("Please load a file to visualize!")
                alert.exec()
                return
            
            if not os.path.exists(result_file.text()):
                alert = QMessageBox()
                alert.setText("The entered file could not be found!")
                alert.exec()
                return

            df = pd.read_csv(result_file.text())
           


            resultframe = [["Isocortex", df[df['structure_name'].str.contains('socortex')]["total_cells"].sum()],
                           ["Cerebral area", df[df['structure_name'].str.contains('erebral')]["total_cells"].sum()],
                           ["Hypothalamus", df[df['structure_name'].str.contains('ypothala')]["total_cells"].sum()],
                           ["Striatum", df[df['structure_name'].str.contains('tria')]["total_cells"].sum()],
                           ["Olfactory area", df[df['structure_name'].str.contains('factory')]["total_cells"].sum()],
                           ["Somatosensory area", df[df['structure_name'].str.contains('omatosen')]["total_cells"].sum()],
                           ["Motor area", df[df['structure_name'].str.contains('otor')]["total_cells"].sum()],
                           ["Thalamus", df[df['structure_name'].str.contains('halamus')]["total_cells"].sum()],
                           ["Piriform", df[df['structure_name'].str.contains('iriform')]["total_cells"].sum()],
                           ["Dentate Gyrus", df[df['structure_name'].str.contains('entate')]["total_cells"].sum()],
                           ["Hypocampus", df[df['structure_name'].str.contains('ypocampus')]["total_cells"].sum()],
                           ["Entorhinal area", df[df['structure_name'].str.contains('ntorhin')]["total_cells"].sum()],
                           ["Pallidum", df[df['structure_name'].str.contains('allidum')]["total_cells"].sum()],
                           ["Cerebellum", df[df['structure_name'].str.contains('erebell')]["total_cells"].sum()],
                           ["Epithalamus", df[df['structure_name'].str.contains('pithalam')]["total_cells"].sum()],
                           ["Midbrain", df[df['structure_name'].str.contains('idbrain')]["total_cells"].sum()],
                           ["Pons", df[df['structure_name'].str.contains('ons')]["total_cells"].sum()],
                           ["Medulla", df[df['structure_name'].str.contains('edulla')]["total_cells"].sum()],
                           ["Gustatory area", df[df['structure_name'].str.contains('ustato')]["total_cells"].sum()],
                           ["Amygdala", df[df['structure_name'].str.contains('mygda')]["total_cells"].sum()],
                           ["Zona incerna", df[df['structure_name'].str.contains('ona in')]["total_cells"].sum()],
                           ["Limbic", df[df['structure_name'].str.contains('imbic')]["total_cells"].sum()],
                           ["Optic area", df[df['structure_name'].str.contains('ptic')]["total_cells"].sum()]]

            resultframe = pd.DataFrame(resultframe, columns=['Region', 'Cellcount'])
            print(resultframe)
            graph = ggplot(resultframe, aes(x='Region', y='Cellcount')) + geom_bar(stat="identity") + coord_flip()
            print(graph)

        load_barplot_button.pressed.connect(lambda: load_barplot())
        choose_resultfile_button.pressed.connect(lambda: choose_resultfile())

        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab

    def training_layout(self):  
        tab = QWidget()
        outer_layout = QVBoxLayout()
        inner_layout = QGridLayout()


        ### Widgets for data access to trained models and training data
        yaml_files = QLabel("")
        choose_yaml_button = QPushButton("Choose Yaml")
        trained_model = QLabel("")
        choose_trained_model_button = QPushButton("Choose trained model")
        continue_training = QCheckBox()
        
        ###Widgets for training parameters 
        test_fraction = QLineEdit("0.1")
        learning_rate = QLineEdit("0.0001")
        batch_size = QLineEdit("32")
        epochs  = QLineEdit("1")

        ###Widgets for starting training,loading and saving parametes
        config_path = QLineEdit("Insert filename extension")
        load_config_button = QPushButton("Load parameters")
        save_config_button = QPushButton("Save parameters")
        train_network_button = QPushButton("Train network")

        

        ### Visualization of Widgets 
        inner_layout.addWidget(QLabel("Training data"),0,0)
        inner_layout.addWidget(yaml_files,0,1)
        inner_layout.addWidget(choose_yaml_button,0,2)
        
        inner_layout.addWidget(QLabel("Pretrained Model"),1,0)
        inner_layout.addWidget(trained_model,1,1)
        inner_layout.addWidget(choose_trained_model_button,1,2)

        inner_layout.addWidget(QLabel("Continue training ?"),2,0)
        inner_layout.addWidget(continue_training,2,1)

        inner_layout.addWidget(QLabel("Test fraction"),3,0)
        inner_layout.addWidget(test_fraction,3,1)
        
        inner_layout.addWidget(QLabel("Learning Rate"),4,0)
        inner_layout.addWidget(learning_rate,4,1)
        
        inner_layout.addWidget(QLabel("Batch size"),5,0)
        inner_layout.addWidget(batch_size,5,1)
        
        inner_layout.addWidget(QLabel("Epochs"),6,0)
        inner_layout.addWidget(epochs,6,1)
        
        inner_layout.addWidget(config_path,7,0)
        inner_layout.addWidget(load_config_button,7,1)
        inner_layout.addWidget(save_config_button,7,2)
        inner_layout.addWidget(train_network_button,7,3)

        ###Save and load paramters function
        def save_config(save_path):
            if not os.path.exists(save_path):    
                print(save_path)
                resample_variable_list = [continue_training.isChecked(),
                                          test_fraction.text(),
                                          learning_rate.text(),
                                          batch_size.text(),
                                          epochs.text()]

                pd_df = pd.DataFrame([resample_variable_list],
                                     index = [1],
                                     columns = ["Continue training", "Test fraction",
                                                "Learning rate","Batch size","Epochs"])
                pd_df.to_csv(save_path)
            else:
                alert = QMessageBox()
                alert.setText("File already exists!")
                alert.exec()
               
        def load_config(load_path):
            if os.path.exists(load_path):    
                print(load_path)
                pd_df = pd.read_csv(load_path, header = 0)
                continue_training.setCheckState(bool(pd_df["Continue training"][0]))
                test_fraction.setText(str(pd_df["Test fraction"][0]))
                learning_rate.setText(str(pd_df["Learning rate"][0]))
                batch_size.setText(str(pd_df["Batch size"][0]))
                epochs.setText(str(pd_df["Epochs"][0]))
          
            else:
                alert = QMessageBox()
                alert.setText("Path does not exist!")
                alert.exec()   

        ### Function for choosing .yaml fiels or trained models (.h5) files
        def choose_yaml():
            path = QFileDialog.getOpenFileName(self, "Choose a Model file (.h5)")
            if path != ('', ''):
                yaml_files.setText(str(path[0]))
                print("Yaml files text", yaml_files.text())
            else:
                yaml_files.setText('')
                print("Yaml files text", yaml_files.text())

        def choose_model():
            path = QFileDialog.getOpenFileName(self, "Choose a Model file (.h5)")
            if path != ('', ''):
                trained_model.setText(str(path[0]))
                print("Trained model text",trained_model.text())
            else:
                trained_model.setText('')
                print("Trained model text",trained_model.text())


        ### Connection of widgets with fundtion, start training, save and load, choose yaml or trained models
        
        load_config_button.pressed.connect(lambda: load_config(load_path = os.getcwd() + "/train_network_" + config_path.text() + ".csv"))
        save_config_button.pressed.connect(lambda: save_config(save_path = os.getcwd() + "/train_network_" + config_path.text() + ".csv"))
        
        train_network_button.clicked.connect(lambda: self.train_network(_yaml_files=str(yaml_files.text()),
                                                                        _trained_model =str(trained_model.text()),
                                                                        _continue_training=bool(continue_training.isChecked()),
                                                                        _test_fraction=float(test_fraction.text()),
                                                                        _learning_rate=float(learning_rate.text()),
                                                                        _batch_size=int(batch_size.text()),
                                                                        _epochs=int(epochs.text())))

        choose_yaml_button.clicked.connect(lambda: choose_yaml())
        choose_trained_model_button.clicked.connect(lambda: choose_model())

        ### Add inner layout to outer layout, add outer layout to tab and return tab
        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab
    
if __name__ == "__main__":
    app = QApplication([])
    main_window = Main_Window()
    main_window.show()
    app.exec()








