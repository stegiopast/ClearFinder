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

from dask_image.imread import imread
from multiprocessing import Process

from sklearn.datasets import make_blobs
from sklearn import decomposition
import scipy.stats
import matplotlib.pyplot as plt
import seaborn as sns

from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
import matplotlib
matplotlib.use('Qt5Agg')
#from plotnine import ggplot, aes, geom_bar, coord_flip


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


class Plot_Window(QDialog):
      
    # constructor
    def __init__(self, parent=None):
        super(Plot_Window, self).__init__(parent)
  
        # a figure instance to plot on
        self.figure = plt.figure()
  
        # this is the Canvas Widget that
        # displays the 'figure'it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
  
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
  
        # Just some button connected to 'plot' method
        # self.button = QPushButton('Plot')
          
        # adding action to the button
        # self.button.clicked.connect(self.plot)
  
        # creating a Vertical Box layout
        layout = QVBoxLayout()
          
        # adding tool bar to the layout
        layout.addWidget(self.toolbar)
          
        # adding canvas to the layout
        layout.addWidget(self.canvas)
          
        # adding push button to the layout
        #layout.addWidget(self.button)
          
        # setting layout to the main window
        self.setLayout(layout)
    

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
        tabs.addTab(self.preanalysis_layout(), "Grouping and Normalization")
        tabs.addTab(self.analysis_layout(),"Analysis and Plots")
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
                        trained_model_string = "--trained-model " + _trained_model + " "
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



    """
    Input: pd.Dataframe (of mouse_ontology.csv) 
    Creates a pd.Dataframe with 2 columns:  The Way from the current region to the root and the corresponding Level
    Returns this pd.Dataframe
    """
    def createTrackingList(self,dataframe: pd.DataFrame) -> pd.DataFrame:
        reference_df_ID = dataframe.set_index(dataframe["id"])
        reference_df_Name = dataframe.set_index(dataframe["name"])

        trackedlevels = [[] for x in range(dataframe.shape[0])]
        correspondingLevel = [[] for x in range(dataframe.shape[0])]

        for i in range(len(dataframe)):
            name = dataframe.iloc[i, 4]  # iterate over all rows of "names'
            df_temp = reference_df_Name.loc[name]
            temp_name = df_temp["name"]

            trackedlevels[i].append(temp_name)
            correspondingLevel[i].append(int(df_temp["st_level"]))
            if not df_temp.empty:
                while (int(df_temp["st_level"]) >= 0):
                    if (int(df_temp["st_level"]) == 0):
                        break
                    df_temp = reference_df_ID.loc[int(df_temp["parent_structure_id"])]
                    temp_name = df_temp["name"]
                    trackedlevels[i].append(temp_name)
                    correspondingLevel[i].append(int(df_temp["st_level"]))

        

        df = np.array([trackedlevels, correspondingLevel], dtype=object)

        df = np.transpose(df)

        df = pd.DataFrame(data=df,
                          columns=["TrackedWay",
                                   "CorrespondingLevel"])
        return df


    """
    Input: pd.Dataframe (mouse_ontology.csv) , trackedList (pd.Dataframe from createTrackingList), and the length of the pd.Dataframe
    Creates a Template-Resultframe, which can be used for every sample
    Cols: Region, trackedWay, CorrespondingLevel, RegionCellCount, RegionCellCountSummedUp
    """
    def createResultframe(self, df, trackedList):
        resultframe = np.array([list(df["name"]),  # Takes all important Brain Regions in first Col
                                trackedList["TrackedWay"],
                                trackedList["CorrespondingLevel"],
                                [0 for x in range(trackedList.shape[0])],  # Sets the count of each Brain Region to 0
                                [0 for x in range(trackedList.shape[0])]])  # Creates a column for normalized Values
        resultframe = np.transpose(resultframe)

        resultframe = pd.DataFrame(data=resultframe,
                                   columns=["Region",
                                            "TrackedWay",
                                            "CorrespondingLevel",
                                            "RegionCellCount",
                                            "RegionCellCountSummedUp"])

        resultframe["RegionCellCount"] = pd.to_numeric(resultframe["RegionCellCount"])
        resultframe["RegionCellCountSummedUp"] = pd.to_numeric(resultframe["RegionCellCountSummedUp"])

        return resultframe


    """
    df = summarized_counts
    reference = mouse_ontology.csv as pd.Dataframe
    trackedLevels = pd.Dataframe of the tracked regions and corresponding Levels
    
    Output: The Template-Resultframe from (createResultframe) but filled with values of the cellcount of each region
    """
    def analyse_csv(self,df: pd.DataFrame,reference_df: pd.DataFrame, trackedLevels: list, choice: str) -> pd.DataFrame:
        if choice == "Whole brain":
            total_cells = "total_cells"
        elif choice == "Left hemisphere":
            total_cells = "left_cell_count"
        else:
            total_cells = "right_cell_count"
        
        #total_cellcount = int(df[total_cells].sum())  # get total cellcount for reference
        df["name"] = df["structure_name"]

        #Reference_df_ID becomes copied twice to allow O(1) access to "id" or "name" as index of reference_frame
        reference_df_ID = reference_df.set_index(reference_df["id"])
        reference_df_Name = reference_df.set_index(reference_df["name"])
        
        #Creation of a template resultframe including all regions and a fusion of ontology_csv and trackedLevels mask, 
        # all entries in RegionCellCount and RegionCellCountSummedUp are initialized as 0
        resultframe = self.createResultframe(reference_df, trackedLevels)

        # Loop Iterates over all entries in summary.csv and tries to embed them into resultframe
        # For each entry in summary.csv the parent_id will iteratively indentify the parent structure of this entry 
        # and sum these entries up, until the root is reached. In that way the cellcounts become summarized over all brain regions in different hierarchies
        
        
        for i in range(len(df.iloc[:, 0])):
            name = df.iloc[i]["name"]  # get the Name of the Region at current index
            print(name)

            # Structures like "No label" and "universe" are not part of ontology.csv and therefore will be removed with this try nd except function    
            try:
                df_temp = reference_df_Name.loc[name]
            except KeyError:
                samplename = os.path.basename(self.my_working_directory)
                filename = self.my_working_directory + "/" + samplename + "_unmapped_regions.csv"
        
                with open(filename, "a+") as KeyError_file:
                    KeyError_file.write(str(name) + ";" + str(df.iloc[i][total_cells]) + "\n")
                continue

            temp_name = df_temp["name"] #Name of current region
            index_outerCount = resultframe.index[resultframe["Region"] == temp_name] # Find index in resultframe where current region occurs
            cellcountRegion = df[df["structure_name"] == resultframe["Region"][index_outerCount[0]]][
                total_cells].sum()  # Cell counts in current region become saved as integer
            resultframe.loc[index_outerCount[0], "RegionCellCount"] += cellcountRegion #Cell count for structure in current iteration is written into resultframe
            resultframe.loc[index_outerCount[0], "RegionCellCountSummedUp"] += cellcountRegion #Cell count for structure in current iteration is written into resultframe
            if not df_temp.empty:
                while (int(df_temp["st_level"]) >= 0):
                    if (int(df_temp["st_level"]) == 0):
                        break  # While loop breaks if root structure is reached in hierarchical tree
                    df_temp = reference_df_ID.loc[int(df_temp["parent_structure_id"])] # Temporary dataframe of parent region 
                    temp_name = df_temp["name"] #Update name of parent region 
                    index_innerCount = resultframe.index[resultframe["Region"] == temp_name] 
                    resultframe.loc[index_innerCount[0], "RegionCellCountSummedUp"] += cellcountRegion # Add cell count of leaf structure to parent structure

        return resultframe

    """
    Calls the writeXML-Function to actually transfer certain CSV Files to XML
    """
    def processCellsCsv(self):

        df_filename = "/analysis/summary.csv"
        df_name = self.my_working_directory + df_filename
        df = pd.read_csv(df_name, header=0)

        df_final_filename = "/analysis/cells_" + self.channel_chosen + "_final.csv"
        df_final_name = self.my_working_directory + df_final_filename
        df_final = df[df["structure_name"] != "universe"]
        df_final = df_final[df_final["structure_name"] != "No label"]
        df_final.to_csv(df_final_name, sep=";")

        #Counts abundancy in different brain regions
        df_final = pd.DataFrame(df_final)

        #Writes a final csv with single cell counts 
        df_final.to_csv(self.my_working_directory + "/analysis/cells_" + self.channel_chosen + "_summarized_counts.csv", sep=";")



    """
    calls the analyse_csv Function to actually create the embedded_ontology.csv which is needed from each sample for the analysis
    """
    def embedOntology(self,choice):
        # Reads ontology file holding the reference region dictionairy
        reference_df = pd.read_csv(str(os.path.dirname(os.path.realpath(sys.argv[0]))) + "/ontology_mouse.csv",
                               # Current Refernce Dataframe for mapping
                               # File which stores all important Brain Regions (Atlas?)
                               sep=";",  # Separator
                               header=0,  # Header
                               index_col=0)  # Index Col

        #Creates a mask table with all regions abundant in the ontology file for comparibility
        # Additionally allt the structural abundancies between regions of different hierarchy become recorded in form of id- and structurename arrays 
        trackedLevels = self.createTrackingList(reference_df)

        #Reads the cell detection csv on a single cell basis (coordinates, transformed coordinates and regionname)
        df = pd.read_csv(self.my_working_directory + "/analysis/cells_" + self.channel_chosen + "_summarized_counts.csv", header=0, sep=";")

        samplename = os.path.basename(self.my_working_directory)
        new_df = self.analyse_csv(df,reference_df, trackedLevels, choice)
        new_df_name = self.my_working_directory + "/" + samplename + "_" + self.channel_chosen + "_embedded_ontology.csv"
        new_df.to_csv(new_df_name, sep=";", index=0)
        return

    def assignment(self, choice):
        self.processCellsCsv()
        self.embedOntology(choice)
        return


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

        ## Widget for embedding summary.csv in hierarchical dataframe
        choose_structure = QComboBox()
        choose_structure.insertItem(0, "Whole brain")
        choose_structure.insertItem(1, "Left hemisphere")
        choose_structure.insertItem(0, "Right hemisphere")

        assignment_button = QPushButton("Embed Ontology")



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

        inner_layout.addWidget(choose_structure,11,0)
        inner_layout.addWidget(assignment_button,11,1)


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
        assignment_button.clicked.connect(lambda: self.assignment(choice=str(choose_structure.currentText())))
        

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


    def preanalysis_layout(self):
        tab = QWidget()
        outer_layout = QHBoxLayout()
        inner_layout1 = QVBoxLayout()
        inner_layout2 = QVBoxLayout()
        inner_layout3 = QVBoxLayout()

        
        #Widgets for inner layout 1
        result_file_list = QListWidget()
        add_resultfile_button = QPushButton("Add analysis file")
        remove_resultfile_button = QPushButton("Remove last file")
        final_output_directory = QLineEdit("")
        create_final_output_directory = QPushButton("Set output dir")
        make_analysis_data = QPushButton("Create analysis data (absolute values)")

        
        #Widgets for inner Layout2
        choose_log_transformation_ComboBox = QComboBox()
        choose_log_transformation_ComboBox.insertItem(0, "None")
        choose_log_transformation_ComboBox.insertItem(1, "log_10")
        choose_log_transformation_ComboBox.insertItem(2, "log_2")
    
        
        choose_normalization_ComboBox = QComboBox()
        choose_normalization_ComboBox.insertItem(0,"None") 
        choose_normalization_ComboBox.insertItem(1,"Counts per million")
        choose_normalization_ComboBox.insertItem(2,"Median of ratio")
        #choose_normalization_ComboBox.insertItem(3,"Percentile normalization (0.05,0.95)")
        

        #filter_level_ComboBox = QComboBox()
        #filter_level_ComboBox.insertItem(0,"None")
        #filter_level_ComboBox.insertItem(1,"1")
        #filter_level_ComboBox.insertItem(2,"2")
        #filter_level_ComboBox.insertItem(3,"3")
        #filter_level_ComboBox.insertItem(4,"4")
        #filter_level_ComboBox.insertItem(5,"5")
        #filter_level_ComboBox.insertItem(6,"6")
        #filter_level_ComboBox.insertItem(7,"7")
        #filter_level_ComboBox.insertItem(8,"8")
        #filter_level_ComboBox.insertItem(9,"9")
        #filter_level_ComboBox.insertItem(10,"10")
        #filter_level_ComboBox.insertItem(11,"11")
        #filter_level_ComboBox.insertItem(12,"12")

        #filter_region_LineEdit = QLineEdit("")

        filter_normalization_button = QPushButton("Log Transform | Normalize | Filter ")


        #Widgets for inner Layout 3
        metadata_table = QTableWidget(12,2)

        save_metadata = QPushButton("Save Metadata")
        for i in range(metadata_table.rowCount()):
            for j in range(metadata_table.columnCount()):
                metadata_table.setCellWidget(i,j,QLineEdit(""))

        metadata_table.setHorizontalHeaderLabels(["sample","condition"]) 
        

        

        inner_layout1.addWidget(QLabel("<b>Pre-analysis steps</b>"))
        
        inner_layout1.addWidget(QLabel("Input for count table:"))
        inner_layout1.addWidget(add_resultfile_button)
        inner_layout1.addWidget(remove_resultfile_button)
        inner_layout1.addWidget(result_file_list)
        inner_layout1.addWidget(QLabel("Output directory for resulting files:"))
        inner_layout1.addWidget(final_output_directory)
        inner_layout1.addWidget(create_final_output_directory)
        inner_layout1.addWidget(make_analysis_data)
        
        inner_layout2.addWidget(QLabel("<b>Normalization</b>"))
        
        inner_layout2.addWidget(QLabel("Normalization"))
        inner_layout2.addWidget(choose_normalization_ComboBox)

        inner_layout2.addWidget(QLabel("Choose log transformation or None"))
        inner_layout2.addWidget(choose_log_transformation_ComboBox)
        

        
        #inner_layout2.addWidget(QLabel("                                          "))
        #inner_layout2.addWidget(QLabel("                                          "))
        #inner_layout2.addWidget(QLabel("Filter for level in hierarchical structure"))
        #inner_layout2.addWidget(filter_level_ComboBox)



        #inner_layout2.addWidget(QLabel("                                          "))
        #inner_layout2.addWidget(QLabel("                                          "))
        #inner_layout2.addWidget(QLabel("Filter for a region and it's subregions"))
        #inner_layout2.addWidget(filter_region_LineEdit)

        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(filter_normalization_button)


        inner_layout3.addWidget(QLabel("<b>Metadata</b>"))
        inner_layout3.addWidget(metadata_table)
        inner_layout3.addWidget(save_metadata)
    
        #Embed inner layouts in outer layout
       
        inner_layout1.addStretch()
        inner_layout2.addStretch()
        inner_layout3.addStretch()
        

        outer_layout.addLayout(inner_layout1)
        outer_layout.addLayout(inner_layout2)
        outer_layout.addLayout(inner_layout3)
        tab.setLayout(outer_layout)

        add_resultfile_button.pressed.connect(lambda: add_analysis_file())
        remove_resultfile_button.pressed.connect(lambda: remove_last_element())
        create_final_output_directory.pressed.connect(lambda: set_output_directory())
        make_analysis_data.pressed.connect(lambda: preprocess_analysis_data())
        filter_normalization_button.pressed.connect(lambda: logtransform_normalize_filter())
        save_metadata.pressed.connect(lambda: save_metadata())
        

       #Functions for preprocessing  

        def add_analysis_file():
            path = QFileDialog.getOpenFileName(self,"Choose embedded_ontology.csv of interest")
            if "ontology.csv" in str(path[0]):
                result_file_list.addItem(str(path[0]))
            else:
                alert = QMessageBox()
                alert.setText("Please load an embedded_ontology.csv file !")
                alert.exec()
                return

                
        def remove_last_element():
            result_file_list.takeItem(result_file_list.count()-1)

        def set_output_directory():
            if os.path.exists(final_output_directory.text()):
                pass
            else:
                try:
                    os.makedirs(final_output_directory.text())
                except (ValueError,NameError):
                    alert = QMessageBox()
                    alert.setText("Directory  is not creatable!\n Make sure the parent path to the new directory exists.")
                    alert.exec()
                    return

                    

        def save_metadata():
            metadata_list = []
            for i in range(metadata_table.rowCount()):
                if metadata_table.cellWidget(i,0).text() != ""  and metadata_table.cellWidget(i,1).text() != "":
                    metadata_list.append([metadata_table.cellWidget(i,j).text() for j in range(metadata_table.columnCount())])
                else:
                    pass
            metadata_df = pd.DataFrame(np.array(metadata_list),columns = ["sample","condition"])
            metadata_df.to_csv(final_output_directory.text()+"/metadata.csv", sep = ";")
            print(metadata_list)
        

        
        def preprocess_analysis_data():
            files_to_analyse = [result_file_list.item(i).text() for i in range(result_file_list.count())] 
            df_list = []
            print(files_to_analyse)
            for i in files_to_analyse:
                df_list.append(pd.read_csv(i, header=0, sep=";"))

            new_df = pd.DataFrame(df_list[0]["Region"])
            new_df2 = pd.DataFrame(df_list[0]["Region"])
            new_df3 = pd.DataFrame(df_list[0][["Region","TrackedWay","CorrespondingLevel"]])
            

            for i,val in enumerate(df_list):
                new_df[str(os.path.basename(os.path.dirname(files_to_analyse[i])))] = val["RegionCellCount"]

            for i,val in enumerate(df_list):
                new_df2[str(os.path.basename(os.path.dirname(files_to_analyse[i])))] = val["RegionCellCountSummedUp"]


            new_df.to_csv(final_output_directory.text() + "/absolute_counts.csv", sep=";",index=False)
            new_df2.to_csv(final_output_directory.text() + "/hierarchical_absolute_counts.csv",sep=";",index=False)
            new_df3.to_csv(final_output_directory.text() + "/list_information.csv", sep = ";", index=False)


        def logtransform_normalize_filter():
            if os.path.exists(final_output_directory.text()):
                df_abs = pd.read_csv(final_output_directory.text() + "/absolute_counts.csv", sep = ";", header = 0,index_col=0)
                df_hier_abs = pd.read_csv(final_output_directory.text() + "/hierarchical_absolute_counts.csv", sep = ";",header = 0,index_col = 0)
                
                df_abs_filename = "absolute_counts.csv"
                df_hier_abs_filename = "hierarchical_absolute_counts.csv"

                if choose_normalization_ComboBox.currentText() == "Counts per million":
                    print("Running counts per million normalization")

                    sum_df_abs = df_abs.sum()
                    df_abs = df_abs / sum_df_abs * 1000000
                    df_hier_abs = df_hier_abs / sum_df_abs * 1000000

                    df_abs_filename = "cpm_norm_" + df_abs_filename
                    df_hier_abs_filename = "cpm_norm_" + df_hier_abs_filename

                elif choose_normalization_ComboBox.currentText() == "Median of ratio":
                    print("Running Median of ratio normalization")

                    df_abs_rowmean = df_abs.mean(axis = 1)
                    df_hier_abs_rowmean = df_hier_abs.mean(axis = 1)

                   # print(df_abs_rowmean)
                   # print(df_hier_abs_rowmean)
                    
                    df_abs_copy = df_abs.copy()
                    df_hier_abs_copy = df_hier_abs.copy()

                    for i in range(len(df_abs_copy.iloc[0,:])):
                        df_abs_copy.iloc[:,i] = df_abs_copy.iloc[:,i] / df_abs_rowmean

                        
                    for i in range(len(df_hier_abs_copy.iloc[0,:])):
                        df_hier_abs_copy.iloc[:,i] = df_hier_abs_copy.iloc[:,i] / df_hier_abs_rowmean

                    df_abs_copy_median = df_abs_copy.median()
                    df_hier_abs_copy_median = df_hier_abs_copy.median()

                    df_abs = df_abs / df_abs_copy_median
                    df_hier_abs = df_hier_abs / df_hier_abs_copy_median

                    
                    df_abs_filename = "mor_norm_" + df_abs_filename
                    df_hier_abs_filename = "mor_norm_" + df_hier_abs_filename
    

                if choose_log_transformation_ComboBox.currentText() == "log_2":
                    print("Running log2 transformation")

                    df_abs = np.log2(df_abs)
                    df_hier_abs = np.log2(df_hier_abs)

                    df_abs_filename = "log2_" + df_abs_filename
                    df_hier_abs_filename = "log2_" + df_hier_abs_filename

                elif choose_log_transformation_ComboBox.currentText() == "log_10":
                    df_abs = np.log10(df_abs)
                    df_hier_abs = np.log10(df_hier_abs)

                    df_abs_filename = "log10_" + df_abs_filename
                    df_hier_abs_filename = "log10_" + df_hier_abs_filename

                #if filter_level_ComboBox.currentText() != "None":
                #    level = int(filter_level_ComboBox.currentText())
                #    information = pd.read_csv(final_output_directory.text() + "/list_information.csv", sep = ";",index_col = 0)
                #    index_list = []
                #    for i,val in enumerate(information["CorrespondingLevel"]):
                #        array = eval(val)
                #        if level == array[0]:
                #            index_list.append(i)

                #    df_abs = df_abs.iloc[index_list,:]
                #    df_hier_abs = df_hier_abs.iloc[index_list,:]

                #    df_abs_filename = "level_" + str(level) + "_" + df_abs_filename
                #    df_hier_abs_filename = "level_" + str(level) + "_" + df_hier_abs_filename

                #if filter_region_LineEdit.text() != "":
                #    region = filter_region_LineEdit.text()
                #    information = pd.read_csv(final_output_directory.text() + "/list_information.csv", sep = ";",index_col = 0)
                #    if region in information["TrackedWay"]:
                #        index_list = []
                #        for i,val in enumerate(information["TrackedWay"]):
                #            if region in val:
                #                index_list.append(i)  


                #        df_abs = df_abs.iloc[index_list,:]
                #        df_hier_abs = df_hier_abs.iloc[index_list,:]

                #       df_abs_filename = "region_" + str(region) + "_" + df_abs_filename
                #       df_hier_abs_filename = "level_" + str(region) + "_" + df_hier_abs_filename
                #    else:
                #        alert = QMessageBox()
                #        alert.setText("Region does not exist in ontology file! Please check if Region is written in the correct way!")
                #        alert.exec()
                #        return


                df_abs.to_csv(final_output_directory.text() + "/" + df_abs_filename, sep = ";")
                df_hier_abs.to_csv(final_output_directory.text() + "/" + df_hier_abs_filename, sep = ";")

            else:
                alert = QMessageBox()
                alert.setText("Directory input does not exist!\n Maike sure that the path to the new directory exists.")
                alert.exec()
                return
        return tab

    """
    Layout for final analysis Volcano plots, Boxplots etc.
    """
    def analysis_layout(self):
        
        tab = QWidget()

        
        
        outer_layout = QVBoxLayout()

        inner_layout = QGridLayout()

        intermediate_layout = QHBoxLayout()
        inner_layout2 = QVBoxLayout()
        inner_layout3 = QVBoxLayout()
        inner_layout4 = QVBoxLayout()
        inner_layout5 = QVBoxLayout()
        
        inner_layout6 = QHBoxLayout()

        

        input_file = QLineEdit("")
        choose_input_file = QPushButton("Choose input file")

        input_information_file = QLineEdit("")
        choose_information_file = QPushButton("Choose List information file (information.csv)")

        metadata_file = QLineEdit("")
        choose_metadata_file = QPushButton("Choose metadata file")

        
        plot_window = Plot_Window()
        
        
        
        
        
        
        
        
        self.input_csv = pd.DataFrame()
        self.metadata_csv = pd.DataFrame()
        self.information_csv = pd.DataFrame()

        filter_level_ComboBox = QComboBox()
        filter_level_ComboBox.insertItem(0,"None")
        filter_level_ComboBox.insertItem(1,"1")
        filter_level_ComboBox.insertItem(2,"2")
        filter_level_ComboBox.insertItem(3,"3")
        filter_level_ComboBox.insertItem(4,"4")
        filter_level_ComboBox.insertItem(5,"5")
        filter_level_ComboBox.insertItem(6,"6")
        filter_level_ComboBox.insertItem(7,"7")
        filter_level_ComboBox.insertItem(8,"8")
        filter_level_ComboBox.insertItem(9,"9")
        filter_level_ComboBox.insertItem(10,"10")
        filter_level_ComboBox.insertItem(11,"11")
        filter_level_ComboBox.insertItem(12,"12")

        filter_region_LineEdit = QLineEdit("")

        filter_specific_region_LineEdit = QLineEdit("")

        set_input = QPushButton("Set input and metadata")

        create_pca = QPushButton("PCA")
        create_heatmap = QPushButton("Heatmap")
        #create_vol_plot = QPushButton("Volcano Plot")
        create_boxplot = QPushButton("Boxplot")


        inner_layout.addWidget(QLabel("<b>Input file</b>"),0,0)
        inner_layout.addWidget(input_file,0,1)
        inner_layout.addWidget(choose_input_file,0,2)

        inner_layout.addWidget(QLabel("<b>Metadata file</b>"),1,0)
        inner_layout.addWidget(metadata_file,1,1)
        inner_layout.addWidget(choose_metadata_file,1,2)

        inner_layout.addWidget(QLabel("<b>Information file</b>"),2,0)
        inner_layout.addWidget(input_information_file,2,1)
        inner_layout.addWidget(choose_information_file,2,2)

        inner_layout.addWidget(set_input,3,0)

        inner_layout2.addWidget(QLabel("<b>PCA</b>"))
        inner_layout2.addWidget(create_pca)
        inner_layout2.addStretch()

        #inner_layout3.addWidget(QLabel("<b>Volcano Plot</b>"))
        #inner_layout3.addWidget(create_vol_plot)
        #inner_layout3.addStretch()

        inner_layout4.addWidget(QLabel("<b>Heatmap</b>"))
        inner_layout4.addWidget(QLabel("Select a structure level to filter for"))
        inner_layout4.addWidget(filter_level_ComboBox)
        inner_layout4.addWidget(QLabel("Name a region to filter for ist subregions"))
        inner_layout4.addWidget(filter_region_LineEdit)
        inner_layout4.addWidget(create_heatmap)
        inner_layout4.addStretch()

        inner_layout5.addWidget(QLabel("<b>Boxplot</b>"))
        inner_layout5.addWidget(QLabel("Please name specific region"))
        inner_layout5.addWidget(filter_specific_region_LineEdit)
        inner_layout5.addWidget(create_boxplot)
        inner_layout5.addStretch()

        inner_layout6.addWidget(plot_window)

       

        intermediate_layout.addLayout(inner_layout2)
        intermediate_layout.addLayout(inner_layout3)
        intermediate_layout.addLayout(inner_layout4)
        intermediate_layout.addLayout(inner_layout5)

        outer_layout.addLayout(inner_layout)
        outer_layout.addLayout(intermediate_layout)
        outer_layout.addLayout(inner_layout6)
        tab.setLayout(outer_layout)


        choose_input_file.pressed.connect(lambda: select_input_file())
        choose_metadata_file.pressed.connect(lambda: select_metadata_file())
        choose_information_file.pressed.connect(lambda: select_information_file())
        create_pca.pressed.connect(lambda: pca())
        create_heatmap.pressed.connect(lambda:heatmap())
        create_boxplot.pressed.connect(lambda:boxplot())
        set_input.pressed.connect(lambda: set_input_and_metadata())
        
    

        def select_input_file():
            path = QFileDialog.getOpenFileName(self,"Choose input file of interest")
            input_file.setText(path[0])

        def select_metadata_file():
            path = QFileDialog.getOpenFileName(self,"Choose metadata file of interest")
            metadata_file.setText(path[0])

        def select_information_file():
            path = QFileDialog.getOpenFileName(self,"Choose metadata file of interest")
            input_information_file.setText(path[0])
        
        def set_input_and_metadata():
            self.input_csv = pd.read_csv(input_file.text(),sep=";",header = 0,index_col = 0)
            self.metadata_csv = pd.read_csv(metadata_file.text(),sep=";",header = 0,index_col = 0)
            self.information_csv = pd.read_csv(input_information_file.text(),sep=";",header=0, index_col=0)
            print(self.input_csv)
            print(self.metadata_csv)
            print(self.information_csv)

        def pca():
           
            input_csv = self.input_csv.copy()
            input_csv = input_csv.reset_index(drop = True)
            input_csv = input_csv.loc[:,input_csv.columns != "Region"]
            input_csv = input_csv.dropna()
            input_csv = input_csv[np.isfinite(input_csv).all(1)]
            print(input_csv)
            

            sample_names = list(input_csv.columns)
            input_csv = np.array(input_csv.transpose())
            print(input_csv)
           
           
            metadata_csv = self.metadata_csv.copy()
            print(sample_names)
           
            output_dir = os.path.dirname(input_file.text())
            output_name = "/PCA_" + os.path.basename(input_file.text())[:-4] + ".png"

            pca = decomposition.PCA(n_components=2)

            pc = pca.fit_transform(input_csv)
            pc_df = pd.DataFrame(data = pc , columns = ['PC1', 'PC2'])
            print(pc_df)
            pc_df["Cluster"] = sample_names

            print(pc_df)

            condition_array = []

            for i in pc_df["Cluster"]:
                for j,val in enumerate(metadata_csv["sample"]):
                    if str(i) == str(val):
                        condition_array.append(list(metadata_csv["condition"])[j])
            pc_df["Condition"] = condition_array            

            var_df = pd.DataFrame({'var':pca.explained_variance_ratio_, 'PC':['PC1','PC2']})
            fig = sns.lmplot( x="PC1", y="PC2",data=pc_df,fit_reg=False,hue='Condition',legend=True,scatter_kws={"s": 80})

            for i,txt in enumerate(pc_df["Cluster"]):
                plt.annotate(txt,(list(pc_df["PC1"])[i],list(pc_df["PC2"])[i]), ha = "center", va = "bottom")
            
            plt.savefig(output_dir + output_name)
            plt.close()

            def hue_regplot(data, x, y, hue, palette=None, **kwargs):
                from matplotlib.cm import get_cmap
    
                regplots = []
    
                levels = data[hue].unique()
    
                if palette is None:
                    default_colors = get_cmap('tab10')
                    palette = {k: default_colors(i) for i, k in enumerate(levels)}
    
                for key in levels:
                    regplots.append(
                        sns.regplot(
                            x=x,
                            y=y,
                            data=data[data[hue] == key],
                            color=palette[key],
                            **kwargs
                        )
                    )
                
                for i,txt in enumerate(data["Cluster"]):
                    plt.annotate(txt,(list(data["PC1"])[i],list(data["PC2"])[i]), ha = "center", va = "bottom")
    
                return regplots

            plot_window.figure.clear()
            ax = plot_window.figure.add_subplot(111)
            hue_regplot(data=pc_df, x='PC1', y='PC2', hue='Condition', ax=ax)
            plot_window.canvas.draw()
            
            




        #def volcano():
        #    pass

        def heatmap():
            input_csv = self.input_csv.copy()
            print(input_csv)
            information = self.information_csv.copy()

            if filter_region_LineEdit.text() != "":
                region = filter_region_LineEdit.text()
                print(information["TrackedWay"])
                if region in information["TrackedWay"]:
                    index_list = []
                    for i,val in enumerate(information["TrackedWay"]):
                        if region in val:
                            index_list.append(i)  


                    input_csv = input_csv.iloc[index_list,:]
                    information = information.iloc[index_list,:]
                    
                else:
                    alert = QMessageBox()
                    alert.setText("Region does not exist in ontology file! Please check if Region is written in the correct way!")
                    alert.exec()
                    return
                brainregion = "region_" + region

            if filter_level_ComboBox.currentText() != "None":
                level = int(filter_level_ComboBox.currentText())
                index_list = []
                for i,val in enumerate(information["CorrespondingLevel"]):
                    array = eval(val)
                    if level == array[0]:
                        index_list.append(i)

                input_csv = input_csv.iloc[index_list,:]
                information = information.iloc[index_list,:]
                brainregion = "level_" + str(level)
            
            

            brainregion = brainregion + "_heatmap"

            if input_csv.empty:
                alert = QMessageBox()
                alert.setText("After filtering the region the dataframe it is empty! - Try other filters")
                alert.exec()
                return

            input_csv = input_csv.dropna()
            input_csv = input_csv.loc[:,input_csv.columns != "Region"]
            input_csv = input_csv[np.isfinite(input_csv).all(1)]
            input_csv = input_csv.loc[(input_csv!=0).any(axis=1)]

            regions = input_csv.index.to_numpy()
            input_csv = input_csv.reset_index(drop = True)
            
            output_dir = os.path.dirname(input_file.text())
            output_name = "/" + brainregion + "_" + os.path.basename(input_file.text())[:-4] + ".png"

            sns.heatmap(input_csv, yticklabels=regions, annot=False)
            plt.title(brainregion)
            plt.savefig(output_dir + output_name, bbox_inches='tight')
            plt.close()
            
            plot_window.figure.clear()
            
            ax = plot_window.figure.add_subplot(111)
            
            sns.heatmap(input_csv, yticklabels=regions, annot=False, ax = ax)
            plt.close()
            

            plot_window.canvas.draw()
            



        def boxplot():
            input_csv = self.input_csv.copy()
            print(input_csv)
            information = self.information_csv.copy()
            if filter_specific_region_LineEdit.text() != "":
                region = filter_specific_region_LineEdit.text()
                if region in input_csv.index:
                    input_csv = input_csv[input_csv.index == region]
            
                conditions = self.metadata_csv["condition"].unique()
                

                sample_names = list(input_csv.columns)
                for i in sample_names:
                    cpm_name = i + "_processed"
                    input_csv[cpm_name] = input_csv[i]


                for i in conditions:
                    array_of_means = []
                    array_of_stdd = []
                    array_of_medians = []
                    array_of_single_values = []
                    metadata_list_tmp = self.metadata_csv[self.metadata_csv["condition"] == i]
                    for j in range(len(input_csv)):
                        array_of_cpms = []
                        array_of_condition_samples = []
                        for k in range(len(input_csv.iloc[0, :])):
                            print(input_csv.columns[k])
                            print(list([str(i) + "_processed" for i in list(metadata_list_tmp["sample"])]))
                            if input_csv.columns[k] in list(
                                    [str(i) + "_processed" for i in list(metadata_list_tmp["sample"])]):
                                array_of_cpms.append(input_csv.iloc[j, k])
                                array_of_condition_samples.append(input_csv.columns[k])
                        if len(array_of_cpms) < 2:
                            mean = array_of_cpms[0]
                            stdd = 0
                            med = array_of_cpms[0]
                        else:
                            mean = np.mean(array_of_cpms)
                            stdd = np.std(array_of_cpms)
                            med = np.median(array_of_cpms)
                        array_of_means.append(mean)
                        array_of_stdd.append(stdd)
                        array_of_medians.append(med)
                        array_of_single_values.append(array_of_cpms)
                    input_csv[str(i) + "_mean"] = array_of_means
                    input_csv[str(i) + "_stdd"] = array_of_stdd
                    input_csv[str(i) + "_med"] = array_of_medians
                    input_csv[str(i) + "_single_values"] = array_of_single_values
                
                print(input_csv)
                array_for_boxplots = []

                for i in conditions:
                    spread = list(input_csv[str(i) + "_single_values"])

                    data = np.concatenate(spread)
                    array_for_boxplots.append(data)
                print("Array for boxplots\n",array_for_boxplots)

                df_boxplot = pd.DataFrame()

                for val, i in enumerate(conditions):
                    method = "absolute"
                    region_name = region
                    df_tmp = pd.DataFrame({method: array_for_boxplots[val]})
                    df_tmp["condition"] = i
                    df_boxplot = pd.concat([df_boxplot, df_tmp])
                    fig, ax = plt.subplots()
                    ax = sns.boxplot(x="condition", y=method, data=df_boxplot)
                    ax = sns.swarmplot(x="condition", y=method, data=df_boxplot, color=".25")
                    
                    region_name = str(region_name).replace(" ", "")
                    region_name = str(region_name).replace("/", "")
                    plt.title(region)
                
                output_dir = os.path.dirname(input_file.text())
                output_name = "/" + region + "_boxplot_" + os.path.basename(input_file.text())[:-4] + ".png"
                plt.savefig( output_dir + output_name, bbox_inches='tight')
                plt.close
                
                plot_window.figure.clear()
                ax2 = plot_window.figure.add_subplot(111)
                sns.boxplot(x="condition", y=method, data=df_boxplot,ax = ax2)
                sns.swarmplot(x="condition", y=method, data=df_boxplot, color=".25", ax = ax2)
                plot_window.canvas.draw()
        return tab
               

    
if __name__ == "__main__":
    app = QApplication([])
    main_window = Main_Window()
    main_window.show()
    app.exec()








