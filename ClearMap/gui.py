#from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

import sys
print(sys.version)
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import Qt
import os
import sys
import pathlib
import re
import pandas as pd
from ClearMap.Environment import *
import numpy.lib.recfunctions as rfn
import napari
from dask_image.imread import imread

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
        self.setWindowTitle("ClearMap2 GUI")
        #self.resize(400,400)
        self.filename_to_check = filename_to_check
        self.channel_chosen = "C01";

        self.shift_bar = QLineEdit("0")
        self.accept = QPushButton("Accept")
        self.reject = QPushButton("Reject and shift")
        self.quit_renaming = QPushButton("Quit Renaming")
        #self.update(False,self.position)
        self.layout = QGridLayout()
        self.update_layout()
        
        self.setLayout(self.layout)



        
        
        '''
        int_shift = int(self.shift_bar.text())
        new_position = self.position + int_shift

        self.reject.clicked.connect(lambda: self.update(False,new_position))
        self.reject.clicked.connect(self.update_layout)

        #reject.clicked.connect(self.close())

        self.accept.clicked.connect(lambda: self.update(True,self.position))
        self.accept.clicked.connect(self.close)

        #Next line is implemented to quit the application in case a renaming is not possible. 
        self.quit_renaming.clicked.connect(lambda: self.update(False,4000000))
        self.quit_renaming.clicked.connect(self.close)
        '''

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
        for file in pathlib.Path(self.path).iterdir():
            if file.is_file():
                old_name = file.stem + ".tif"
                #print(file.stem)  
                new_name = old_name[self.position:len(old_name)]
                #print("new_name",new_name)
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
    

class Main_Window(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClearMap2 GUI")
        #self.resize(400,400)
        layout = QVBoxLayout()
        self.setLayout(layout)
        tabs = QTabWidget()
        tabs.addTab(self.rename_layout(), "Determine Path | Rename Path")
        tabs.addTab(self.resample_layout(), "Resampling | Alignment")
        tabs.addTab(self.cd_layout(),"Cell Detection")
        #tabs.addTab(self.visualization_layout(),"Visualization")
        layout.addWidget(tabs)
        #self.init_workspace()
        self.debug = False
        


    def init_workspace(self,path = '/home/cellfinder_data',channel = 0): 
        if channel == 0:
            channel_str = "C01"
        elif channel == 1:
            channel_str = "C02"
        self.channel_chosen = channel_str
        my_working_directory = path

        if os.path.exists(my_working_directory):
            #my_working_directory = '/raid/CellRegistration_Margaryta/ClearMap1_2/ClearMap2/' # base directory <- alles relativ dazu
            expression_raw      = 'Signal/' + channel_str + '/Z<Z,4>_' + channel_str +'.tif' # applies for example : "Z0001_C01.tif, Z0023..."
            expression_auto     = 'Auto/Z<Z,4>_'+ 'C01' +'.tif'
            ws = wsp.Workspace('CellMap', directory=my_working_directory);
            ws.update(raw_C01 = 'Signal/C01/Z<Z,4>_C01.tif', raw_C02 = 'Signal/C02/Z<Z,4>_C02.tif', stitched_C01 = 'stitched_C01.npy' , stitched_C02 = 'stitched_C02.npy', resampled_C01 = 'resampled_C01.tif', resampled_C02 = 'resampled_C02.tif')
            if self.channel_chosen == "C01":
                ws.update(raw_C01=expression_raw, autofluorescence=expression_auto)
            if self.channel_chosen == "C02":
                ws.update(raw_C02=expression_raw, autofluorescence=expression_auto)

            if os.path.exists(my_working_directory + '/stitched_'+self.channel_chosen+'.tif'):
                expression_stitched = 'stitched_'+ self.channel_chosen + '.npy'
                if self.channel_chosen == "C01":   
                    ws.update(stitched_C01 = expression_stitched)
                if self.channel_chosen == "C02":
                    ws.upate(stitched_C02 = expression_stitched)

            if os.path.exists(my_working_directory + '/resampled_'+ self.channel_chosen +'.tif'):
                expression_resampled = 'resampled_' + self.channel_chosen + '.tif'
                if self.channel_chosen == "C01":
                    ws.update(resampled_C01 = expression_resampled)
                if self.channel_chosen == "C02":
                    ws.update(resampled_C02 = expression_resampled)
            ws.info()
            print(ws.filename('cells', postfix = 'raw_C01'))
            #sink_maxima = ws.filename('cells', postfix = 'maxima')
            #source = ws.filename('stitched')
            #sink_raw = ws.source('cells', postfix='raw')
            self.ws = ws
            self.my_working_directory = my_working_directory

            print("Worksapce: ",self.ws)
            print("Working dir:",self.my_working_directory)
            print("Channel chosen:", self.channel_chosen)
            return [ws, my_working_directory]
        else:
            print("Path does not exist!")


    def create_testdata(self, index):
        if index == 0:
            slicing = (slice(700,816),slice(1300,1500),slice(1100,1130));
            self.ws.create_debug('stitched_'+self.channel_chosen,slicing=slicing);
            #self.ws.debug = False;

        elif index == 1:
            slicing = (slice(500,616),slice(1100,1300),slice(1100,1130)); 
            self.ws.create_debug('stitched_'+self.channel_chosen,slicing=slicing);
            #self.ws.debug = False;

        else:
            pass

    def start_debug(self):
        self.ws.debug = True;
        
    def end_debug(self):
        self.ws.debug = False;

    def change_debug(self):
        if self.debug == False:
            self.ws.debug = True
            self.debug = True
        else:
            self.ws.debug = False
            self.debug = False
        print(self.ws.info())

    def init_reference(self, source_res_x=3.02, source_res_y=3.02,source_res_z=3,sink_res_x=25,sink_res_y=25,sink_res_z=25,auto_source_res_x=3.02,auto_source_res_y=3.02,auto_source_res_z=3,auto_sink_res_x=25,auto_sink_res_y=25,auto_sink_res_z=25, orientation_x=1,orientation_y=2,orientation_z=3):

        if not os.path.exists(self.my_working_directory + "/elastix_resampled_to_auto_" + self.channel_chosen):
            os.mkdir(self.my_working_directory +  "/elastix_resampled_to_auto_"+ self.channel_chosen)
        else:
            print(self.my_working_directory + "/elastix_resampled_to_auto_"+self.channel_chosen + " already exists\n")

        if not os.path.exists(self.my_working_directory + "/elastix_auto_to_reference_"+ self.channel_chosen):    
            os.mkdir(self.my_working_directory + "/elastix_auto_to_reference_"+self.channel_chosen)
        else:
            print(self.my_working_directory + "/elastix_auto_to_reference_" + self.channel_chosen + " already exists\n")


        
        resources_directory = settings.resources_path
        # gives more output -> still nearly useless but atleasr something
        annotation_file, reference_file, distance_file=ano.prepare_annotation_files(
        slicing=(slice(None),slice(None),slice(0,256)), orientation=(orientation_x,orientation_y,orientation_z),
        overwrite=False, verbose=True);

        align_channels_affine_file   = io.join(resources_directory, 'Alignment/align_affine.txt')
        align_reference_affine_file  = io.join(resources_directory, 'Alignment/align_affine.txt')
        align_reference_bspline_file = io.join(resources_directory, 'Alignment/align_bspline.txt')

        resample_parameter = {
            "source_resolution" : (source_res_x, source_res_y, source_res_z),       # Resolution of your own files!
            "sink_resolution"   : (sink_res_x,sink_res_y,sink_res_z),
            "processes" : 4,
            "verbose" : True,             
            };
        source = self.ws.source('raw_'+self.channel_chosen);
        sink   = self.ws.filename('stitched_'+self.channel_chosen);
        io.convert(source, sink, verbose=True)

        res.resample(self.ws.filename('stitched_'+self.channel_chosen), sink=self.ws.filename('resampled_'+self.channel_chosen), **resample_parameter)

        resample_parameter_auto = {
        "source_resolution" : (auto_source_res_x, auto_source_res_y, auto_source_res_z),
        "sink_resolution"   : (auto_sink_res_x,auto_sink_res_y,auto_sink_res_z),
        "processes" : 4,
        "verbose" : True,
        };

        res.resample(self.ws.filename('autofluorescence'),
                        sink=self.ws.filename('resampled_'+self.channel_chosen, postfix='autofluorescence'),
                     **resample_parameter_auto)

        align_channels_parameter = {
            #moving and reference images
            "moving_image" : self.ws.filename('resampled_'+self.channel_chosen, postfix='autofluorescence'),
            "fixed_image"  : self.ws.filename('resampled_'+self.channel_chosen),

            #elastix parameter files for alignment
            "affine_parameter_file"  : align_channels_affine_file,
            "bspline_parameter_file" : None,

            #directory of the alig'/home/nicolas.renier/Documents/ClearMap_Ressources/Par0000affine.txt',nment result
           #"result_directory" :  "/raid/CellRegistration_Margaryta/ClearMap1_2/ClearMap2/elastix_resampled_to_auto" 
           "result_directory" :  self.my_working_directory +"/elastix_resampled_to_auto_" + self.channel_chosen
            };

# erstes algnment sollte klappen!
        elx.align(**align_channels_parameter);

        align_reference_parameter = {
            #moving and reference images
            "moving_image" : reference_file,
            "fixed_image"  : self.ws.filename('resampled_' + self.channel_chosen, postfix='autofluorescence'),

            #elastix parameter files for alignment
            "affine_parameter_file"  :  align_reference_affine_file,
            "bspline_parameter_file" :  align_reference_bspline_file,
            #directory of the alignment result
            "result_directory" :  self.my_working_directory + "/elastix_auto_to_reference_" + self.channel_chosen
            };

# dimensionsfehler möglicherweise
        elx.align(**align_reference_parameter);
        return
    

    def write_xml(self,df,pathname):
        df = pd.DataFrame(df)
        pathname = pathname[0:-3] + "xml"
        row_counter = 1
        df_length = len(df)
        with open(pathname,"a") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<CellCounter_Marker_File>\n')
            file.write('  <Image_Properties>\n')
            file.write('    <Image_Filename>placeholder.tif</Image_Filename>\n')
            file.write('  </Image_Properties>\n')
            file.write('  <Marker_Data>\n')
            file.write('    <Current_Type>1</Current_Type>\n')
            file.write('    <Marker_Type>\n')
            file.write('      <Type>1</Type>\n')
            for i in range(len(df.iloc[:,0])):
                row_counter = row_counter + 1
                if (row_counter % 1000 == 0):
                    print(str(row_counter),"/",str(df_length)," lines are processes")
                file.write('      <Marker>\n')
                file.write('        <MarkerX>'+ str(df.iloc[i,:].x) +'</MarkerX>\n')
                file.write('        <MarkerY>'+ str(df.iloc[i,:].y) +'</MarkerY>\n')
                file.write('        <MarkerZ>'+ str(df.iloc[i,:].z) +'</MarkerZ>\n')
                file.write('      </Marker>\n')
            file.write('    </Marker_Type>\n')
            file.write('  </Marker_Data>\n')
            file.write('</CellCounter_Marker_File>\n')

    def process_cells_csv(self):
        df_name = self.my_working_directory + "/cells_" + self.channel_chosen + ".csv"
        df = pd.read_csv(df_name,header=0,sep =";")

        no_label_name = self.my_working_directory + "cells_" + self.channel_chosen + "_no_label.csv"
        df_no_label = df[df["name"] == "No label"]
        df_no_label.to_csv(no_label_name,sep = ";")

        df_universe_name = self.my_working_directory + "cells_" + self.channel_chosen + "_universe.csv"
        df_universe = df[df["name"] == "universe"]
        df_universe.to_csv(df_universe_name,sep = ";")
        
        df_final_name = self.my_working_directory + "cells_" + self.channel_chosen + "_final.csv"
        df_final = df[df["name"] != "universe"]
        df_final = df_final[df_final["name"] != "No label"]   
        df_final.to_csv(df_final_name, sep = ";")

        self.write_xml(df,df_name)
        self.write_xml(df_no_label,no_label_name)
        self.write_xml(df_universe,df_universe_name)
        self.write_xml(df_final,df_final_name)

        df_final = df_final["name"].value_counts()
        df_final = pd.DataFrame(df_final)
        df_final["structure_name"] = df_final.index
        df_final = df_final.reset_index(drop=True)
        df_final.rename(columns={"name" : "total_cells"}, inplace=True)

        df_final.to_csv(self.my_working_directory + "cells_" + self.channel_chosen + "_summarized_counts.csv",sep = ";")

        
        



    def cell_detection(self,flatfield_illumination=None,scaling_illumination="max", shape_background_x = 7, shape_background_y = 7, form_background = "Disk", execute_equalization = False, percentile_equalization_low = 0.5, percentile_equalization_high = 0.95, max_value_equalization = 1.5, selem_equalization_x = 200,selem_equalization_y = 200,selem_equalization_z = 5,spacing_equalization_x = 50,spacing_equalization_y = 50,spacing_equalization_z = 5, interpolate_equalization = 1, execute_dog_filter = False, shape_dog_filter_x = 6,shape_dog_filter_y = 6,shape_dog_filter_z = 6,sigma_dog_filter = None,sigma2_dog_filter = None, hmax_maxima_det = None, shape_maxima_det_x = 6, shape_maxima_det_y = 6, shape_maxima_det_z = 11, threshold_maxima_det = 297.380, measure_intensity_det = "Source", method_intensity_det = "mean", threshold_shape_det = 700, save_shape_det = True, amount_processes = 20,size_maximum = 20,size_minimum = 11, area_of_overlap = 10):

        #Coversion of illumination_correction integers to dictionairy entries of ClearMap
        if flatfield_illumination == 0:
            flatfield_illumination = None
        
        if scaling_illumination == 0:
            scaling_illumination = 'mean'
        elif scaling_illumination == 1:
            scaling_illumination = 'max'
        
        
        #Conversion of background correction values 
        shape_background_x = int(shape_background_x)
        shape_background_y = int(shape_background_y)
        
        if form_background == 0:
            form_background = 'Disk'
        elif form_background == 1:
            form_background = 'Sphere'
            
        
        
        #conversion of equalization values
        percentile_equalization_low = float(percentile_equalization_low)
        percentile_equalization_high = float(percentile_equalization_high)
        max_value_equalization = float(max_value_equalization)
        
        selem_equalization_x = int(selem_equalization_x)
        selem_equalization_y = int(selem_equalization_y)
        selem_equalization_z = int(selem_equalization_z)
        
        spacing_equalization_x = int(spacing_equalization_x)
        spacing_equalization_y = int(spacing_equalization_y)
        spacing_equalization_z = int(spacing_equalization_z)
  
        interpolate_equalization = int(interpolate_equalization)
        
        
        #conversion of dog filtering values
        shape_dog_filter_x = int(shape_dog_filter_x)
        shape_dog_filter_y = int(shape_dog_filter_y)
        shape_dog_filter_z = int(shape_dog_filter_z)
        
        if sigma_dog_filter == 'None':
            sigma_dog_filter = None
        else:
            sigma_dog_filter = float(sigma_dog_filter)
        
            
        if sigma2_dog_filter == 'None':
            sigma2_dog_filter = None
        else:
            sigma2_dog_filter = float(sigma2_dog_filter)
            
        
        #conversion of maxima detection values
        if hmax_maxima_det == 'None':
            hmax_maxima_det = None
        else:
            hmax_maxima_det = int(hmax_maxima_det)
            
        shape_maxima_det_x = int(shape_maxima_det_x)
        shape_maxima_det_y = int(shape_maxima_det_y)
        shape_maxima_det_z = int(shape_maxima_det_z)
        
        if threshold_maxima_det == 0:
            threshold_maxima_det = None
        elif threshold_maxima_det == 1:
            threshold_maxima_det = "background mean"
        elif threshold_maxima_det == 2:
            threshold_maxima_det = "total mean"
        
        #conversion of intensity detection values
        
        measure_intensity_det = ['source','illumination','background','equalized','dog'];
        
        if method_intensity_det == 0:
            method_intensity_det = 'mean'
        elif method_intensity_det == 1:
            method_intensity_det = 'max'
        
        #Conversion of Shape detection values
        threshold_shape_det = int(threshold_shape_det)
        
            



        cell_detection_parameter = cells.default_cell_detection_parameter.copy();

# Changes to default parameters

## Options illumination_correction
        #cell_detection_parameter['iullumination_correction'] = None; #Only to skip
        cell_detection_parameter['iullumination_correction']['flatfield'] = flatfield_illumination #A default flatfield is provided // Array or str with flatfield estimate
        cell_detection_parameter['iullumination_correction']['scaling'] = scaling_illumination # max','mean' or None Optional scaling after flat field correction // float
        #if save_illumination:
        #cell_detection_parameter['iullumination_correction']['save'] = self.ws.filename('cells', postfix = 'illumination_correction') #Save results of illum correction // str(path)
        #cell_detection_parameter['iullumination_correction']['verbose'] = True    

## Options in 'background_correction'
#cell_detection_parameter['background_correction'] = None; # Only to skip 
        cell_detection_parameter['background_correction']['shape'] =(shape_background_x,shape_background_y) #Tuple represents cell shape // tuple (int,int)
        cell_detection_parameter['background_correction']['form'] = form_background #'Sphere' #Describes cell shape, I didnt find an alternative to disk // str
        #if save_background:
        #cell_detection_parameter['background_correction']['save'] = self.ws.filename('cells', postfix = 'background_correction' ) #Save background removal results // str (path)
        #cell_detection_parameter['background_correction']['verbose'] = True

## Equalization
        #cell_detection_parameter['equalization']['percentile'] =(0.5,0.95) # Percentile with lower and mupper percentiles to estzimate equalization // tuple(float,float)
        #cell_detection_parameter['equalization']['max_value'] = 1.5 # Maximal intensity value in the equalized image. Height of value is subjective // float
        #cell_detection_parameter['equalization']['selem'] = (200,200,5) #Strucutral element size to estimate the percentiles // tuple(int, int, int)
        #cell_detection_parameter['equalization']['spacing'] = (50,50,5) #Spacing used to move the structural elements. Larger spacing speeds up processing but loss precision // tuple(?,?)
        #cell_detection_parameter['equalization']['interpolate'] = 1 #Order of the interpolation used in constructing the full background estimate. // int
        #cell_detection_parameter['equalization']['save'] = ws.filename('cells', postfix = 'equalization') # str (path)
        
        if execute_equalization == 1:
            cell_detection_parameter['equalization'] = dict(percentile = (percentile_equalization_low,percentile_equalization_high), max_value=max_value_equalization, selem = (selem_equalization_x,selem_equalization_y,selem_equalization_z),spacing = (spacing_equalization_x,spacing_equalization_y,spacing_equalization_z), save = None)#
        else:
            cell_detection_parameter['equalization'] = None
#c DoG Filter
        if execute_dog_filter == 1:
            cell_detection_parameter['dog_filter']['shape'] = (shape_dog_filter_x,shape_dog_filter_y,shape_dog_filter_z) # Shape of the filter, usually near cell size // tuple(int,int,int)
            cell_detection_parameter['dog_filter']['sigma'] = sigma_dog_filter # usually determined by shape, but is std inner gaussian //tuple(float,float)
            cell_detection_parameter['dog_filter']['sigma2'] = sigma2_dog_filter # usually determined by shape, but is std outer gaussian //tuple(float,float)
           # if save_dog_filter:
           #cell_detection_parameter['dog_filter']['save']= self.ws.filename('cells' , postfix = 'dog_filter') #str (path)
        else:
            cell_detection_parameter['dog_filter'] = None
## Maxima detection
        #io.delete_file(self.ws.filename('cells', postfix='maxima'))
        cell_detection_parameter['maxima_detection']['h_max'] = hmax_maxima_det #Height for the extended maxima. If None simple locasl maxima detection. //float // NOT WORKING SO FAR ? 
        cell_detection_parameter['maxima_detection']['shape'] = (shape_maxima_det_x,shape_maxima_det_y,shape_maxima_det_z) #Shape of the structural element. Near typical cell size. // tuple(int, int)
        # Idea is to take the mean of the values in each procedure + 2*std_deviation, to always predict a significant upregulation Z-test // Has to be implemented
        # We could also implement a filter function at that point, by overwriting data that is 4 std_dev away from the mean, whcih seems unrealistic
        cell_detection_parameter['maxima_detection']['threshold'] = None  #0.55 good value fter dog + equalizaziont for 3258  #5 good value after equalization for 3258 #250 Best so fat without equalization for 3258 # Only maxima above this threshold are detected. If None all are detected // float
        #cell_detection_parameter['maxima_detection']['save'] = self.ws.filename('cells', postfix = 'maxima') # str (path)
        #cell_detection_parameter['maxima_detection']['valid'] = True

## Intensity_detection
        cell_detection_parameter['intensity_detection']['measure'] = measure_intensity_det; #we decided to measure all intensities 
        cell_detection_parameter['intensity_detection']['method'] = method_intensity_det #{'max'|'min','mean'|'sum'} # Use method to measure intensity of the cell  
       # cell_detection_parameter['intensity_detection']['save'] = ws.filename('cells', postfix = 'intensity_detection') #// str (path)


## Shape_detection
        cell_detection_parameter['shape_detection']['threshold'] = threshold_shape_det;
        #cell_detection_parameter['shape_detection']['save'] = self.ws.filename('cells', postfix = 'shape_detection')

## Self edited threshold
        cell_detection_parameter['threshold'] = threshold_maxima_det

# Get an overview about the default processing parameters 
#hdict.pprint(cells.default_cell_detection_processing_parameter)

#cell_detection_parameter['maxima_detection']['save'] = ws.filename('cells', postfix='maxima')

#print(cell_detection_parameter)


        processing_parameter = cells.default_cell_detection_processing_parameter.copy();
        processing_parameter.update(
            processes = amount_processes, #15, #20,
            #optimization = True,
            size_max = size_maximum, #35 100
            size_min = size_minimum, #30 32
            overlap  = area_of_overlap, #10 30
            verbose = True #Set True if process needs to be investigated // Lead to the print of process checkpoints
            )

        cells.detect_cells(self.ws.filename('stitched_'+self.channel_chosen), self.ws.filename('cells', postfix='raw_'+self.channel_chosen),
                           cell_detection_parameter=cell_detection_parameter,
                           processing_parameter=processing_parameter)



    def filter_cells(self,filt_size = 20):
        
        thresholds = {'source':None,'size':(filt_size,None)}
        cells.filter_cells(self.ws.filename('cells', postfix = 'raw_'+self.channel_chosen),self.ws.filename('cells',postfix = 'filtered_'+self.channel_chosen),thresholds=thresholds)
        return



    def atlas_assignment(self):
        
        #sink_maxima = self.ws.filename('cells_', postfix = 'raw_'+self.channel_chosen)
        source = self.ws.filename('stitched_'+self.channel_chosen)
        sink_raw = self.ws.source('cells', postfix='raw_'+self.channel_chosen)


        self.filter_cells()

        # Assignment of the cells with filtered maxima
        # Filtered cell maxima are used to execute the alignment to the atlas
        source = self.ws.source('cells', postfix='filtered_'+ self.channel_chosen)


        # Didn't understand the functions so far. Seems like coordinates become transformed by each function and reassigned. 
        print("Transfromation\n")
        def transformation(coordinates):
            coordinates = res.resample_points(coordinates, sink=None,\
            orientation=None,source_shape=io.shape(self.ws.filename('stitched_'+self.channel_chosen)),sink_shape=io.shape(self.ws.filename('resampled_'+self.channel_chosen)));
            coordinates = elx.transform_points(coordinates, sink=None,transform_directory=self.my_working_directory +'/elastix_resampled_to_auto_'+self.channel_chosen,binary=True, indices=False);
            coordinates = elx.transform_points(coordinates, sink=None,transform_directory=self.my_working_directory +'/elastix_auto_to_reference_'+self.channel_chosen,binary=True, indices=False);
            return coordinates;

        # These are the initial coordinates originating in the file cells_filtered.npy containing the coordinates of the filtered maxima. 
        # Each coordinate of 3 dimensional space x,y,z  is written into a new numpy array. [[x1,y1,z1],[x2,y2,3],...,[x_last,y_last,z_last]] 
        coordinates = np.array([source[c] for c in 'xyz']).T;
        source = self.ws.source('cells', postfix='filtered_'+self.channel_chosen)



        # Coordinates become transformed by the above defined transformation function
        coordinates_transformed = transformation(coordinates);
        

        #for i in coordinates_transformed:
        #  new_coordinates = tuple(i);
        #  np.append(coordinates_transformed_tuple,new_coordinates)


            

        #Cell annotation 

        #Transformed coordinates are used as input to annotate cells by comparing with brain atlas

        #Due to a future warning occured coordinates_transformed was converterted from array[seq] to arr[tuple(seq)] as coordinates_transformed_tuple
        coordinates_transformed_tuple = np.array(tuple(coordinates_transformed))

        print("Label Point\n")
        label = ano.label_points(coordinates_transformed, key='order');
        print("Convert labeled points\n")
        names= ano.convert_label(label,key = 'order',value = 'name');
	

        #Save results
        coordinates_transformed.dtype=[(t,float) for t in ('xt','yt','zt')]
        nparray_label = np.array(label, dtype=[('order', int)]);
        nparray_names = np.array(names, dtype=[('name', 'S256')])

        
        import numpy.lib.recfunctions as rfn
        cells_data = rfn.merge_arrays([source[:], coordinates_transformed, nparray_label, nparray_names], flatten=True, usemask=False)
        io.write(self.ws.filename('cells', postfix = self.channel_chosen), cells_data)
        print("Cells data: \n",cells_data)
        
        #CSV export
        # Pandas was installed via pip, since np.savetxt had 
        csv_source = self.ws.source('cells', postfix = self.channel_chosen)
        
        # Define headers for pandas.Dataframe for csv export
        header = ', '.join([h for h in csv_source.dtype.names])
        
        # Conversion of cell data into pandas.DataFrame for csv export 
        cells_data_df = pd.DataFrame(cells_data, columns = [h for h in csv_source.dtype.names])
        
        # Getting rid of np_str_ artifacts in df[['name']]
        cells_data_df[['name']] = names
        
        # export CSV
        print("Exporting Cells to csv\n")
        cells_data_df.to_csv(self.ws.filename('cells', postfix = self.channel_chosen,extension='csv'), sep= ';');
 


        # ClearMap1.0 export
        # Export is not working so far: Error is "the magic string is not correct; expected b'\x93NUMPY, got b';x;y;z
        ClearMap1_source = self.ws.source('cells', postfix = self.channel_chosen);
        Clearmap1_format = {'points' : ['x', 'y', 'z'],'intensities' : ['source', 'dog', 'background', 'size'],'points_transformed' : ['xt', 'yt', 'zt']}
        for filename, names in Clearmap1_format.items():
            sink = self.ws.filename('cells', postfix=[self.channel_chosen,'_','ClearMap1', filename]);
            data = np.array([ClearMap1_source[name] if name in ClearMap1_source.dtype.names else np.full(ClearMap1_source.shape[0], np.nan) for name in names]);
            io.write(sink, data);

        self.process_cells_csv();
        return

    def voxelization(self):
        annotation_file, reference_file, distance_file=ano.prepare_annotation_files(
        slicing=(slice(None),slice(None),slice(0,256)), orientation=(1,-2,3),
        overwrite=False, verbose=True);
        source = self.ws.source('cells', postfix = self.channel_chosen)
        coordinates = np.array([source[n] for n in ['xt','yt','zt']]).T;
        intensities = source['source'];

        # %% Unweighted

        voxelization_parameter = dict(
          shape = io.shape(annotation_file),
          dtype = None,
          weights = None,
          method = 'sphere',
          radius = (7,7,7),
          kernel = None,
          processes = None,
          verbose = True
        )

        vox.voxelize(coordinates, sink=self.ws.filename('density', postfix='counts_'+ self.channel_chosen), **voxelization_parameter);



#########################################################################################################################################
#                                                                                                                                       #
#                                                                                                                                       #
#                                                                                                                                       #
#                                                                                                                                       #
#                                                   GUI SURFACE IMPLEMENTATION                                                          #
#                                                                                                                                       #
#                                                                                                                                       #
#                                                                                                                                       #
#                                                                                                                                       #
#########################################################################################################################################


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
        ws_path = QLineEdit()
        channel_button = QComboBox()
        channel_button.insertItem(0,"C01")
        channel_button.insertItem(1,"C02")
        set_ws = QPushButton("Set workspace")
        rename_button1 = QPushButton("Rename files in Auto")
        rename_button2 = QPushButton("Rename files in Signal C01")
        rename_button3 = QPushButton("Rename files in Signal C02")
        testdata = QComboBox()
        testdata.insertItem(0,"Border region")
        testdata.insertItem(1,"Background region")
        make_testdata = QPushButton("Make Testdata")
        debug_button = QPushButton("Test Mode")
        debug_button.setCheckable(True)
        


        ##
        inner_layout.addWidget(QLabel("<b>Set Workspace:</b>"),0,0)
        inner_layout.addWidget(QLabel("Input path of interest:"),1,0)
        inner_layout.addWidget(ws_path,1,1)
        inner_layout.addWidget(channel_button,1,2)
        inner_layout.addWidget(set_ws,1,3)
        inner_layout.addWidget(rename_button1,1,4)
        inner_layout.addWidget(rename_button2,1,5)
        inner_layout.addWidget(rename_button3,1,6)
        inner_layout.addWidget(QLabel("      "),2,0)
        inner_layout.addWidget(QLabel("<b>Testdata option:</b>"),3,0)
        inner_layout.addWidget(make_testdata,4,0)
        inner_layout.addWidget(testdata,4,1)
        inner_layout.addWidget(debug_button,5,0,5,4)

        #set_ws.clicked.connect(lambda: print("You"))
        #rename_button1.clicked.connect(lambda: print("HUII"))
       # debug_button.clicked.connect(lambda: print("HELLO"))


        set_ws.clicked.connect(lambda: self.init_workspace(ws_path.text(),channel_button.currentIndex()))
        #set_ws.clicked.connect(lambda: print("Workspace:", self.ws, "Folder: ",self.my_working_directory))
        rename_button1.clicked.connect(lambda: rename_files(_path = self.my_working_directory, extend='/Auto'))
        rename_button2.clicked.connect(lambda: rename_files(_path = self.my_working_directory, extend='/Signal/C01'))
        rename_button3.clicked.connect(lambda: rename_files(_path = self.my_working_directory, extend = '/Signal/C02'))
        make_testdata.clicked.connect(lambda: self.create_testdata(index = testdata.currentIndex()))
        debug_button.clicked.connect(self.change_debug)
        
        


        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab






    def resample_layout(self):
            
        tab = QWidget()
        outer_layout = QVBoxLayout()
        inner_layout = QGridLayout()
    


        ### Widgets Orientation variables

        orientation_x = QLineEdit("1")
        orientation_y = QLineEdit("2")
        orientation_z = QLineEdit("3")



        ### Widgets for source resolution variables

        source_res_x = QLineEdit("3.02")
        source_res_y = QLineEdit("3.02")
        source_res_z = QLineEdit("3")



        ### Widgets for sink resolution variables

        sink_res_x = QLineEdit("25")
        sink_res_y = QLineEdit("25")
        sink_res_z = QLineEdit("25")



        ### Widgets for auto_source resolution variables

        auto_source_res_x = QLineEdit("3.02")
        auto_source_res_y = QLineEdit("3.02")
        auto_source_res_z = QLineEdit("3")



        ### Widgets for auto_source resolution variables
        auto_sink_res_x = QLineEdit("25")
        auto_sink_res_y = QLineEdit("25")
        auto_sink_res_z = QLineEdit("25")



        ### Widgets for parameter saving and loading

        start_resampling_button = QPushButton("Resample")

        config_path = QLineEdit("Insert filename extension")
        load_config_button = QPushButton("Load parameters")
        save_config_button = QPushButton("Save parameters")
        
        '''
        # The variable list will be update with each Line EditEvent to quarantee an iinstant access to the parameter list
        resample_variable_list = []
        def refresh_variable_list():
            resample_variable_list = [source_res_x.text(),source_res_y.text(),source_res_z.text(),\
                sink_res_x.text(),sink_res_y.text(),sink_res_z.text(),\
                auto_source_res_x.text(), auto_source_res_y.text(), auto_source_res_z.text(),\
                auto_sink_res_x.text(), auto_sink_res_y.text(), auto_sink_res_z.text(),\
                orientation_x.text(),orientation_y.text(),orientation_z.text()]
            ### You can implement the overwrite of the resample config file here
            print(resample_variable_list)
            return resample_variable_list
        '''

        def save_config(save_path):
            if not os.path.exists(save_path):    
                print(save_path)
                resample_variable_list = [source_res_x.text(),source_res_y.text(),source_res_z.text(),\
                    sink_res_x.text(),sink_res_y.text(),sink_res_z.text(),\
                    auto_source_res_x.text(), auto_source_res_y.text(), auto_source_res_z.text(),\
                    auto_sink_res_x.text(), auto_sink_res_y.text(), auto_sink_res_z.text(),\
                    orientation_x.text(),orientation_y.text(),orientation_z.text()]
                #print(resample_variable_list)
                pd_df = pd.DataFrame([resample_variable_list], index = [1], columns = ["Source Resolution x", "Source Resolution y", "Source Resolution z","Sink Resolution x","Sink Resolution y","Sink Resolution z","Auto Source Resolution x",\
                    "Auto Source Resolution y","Auto Source Resolution z","Auto Sink Resolution x","Auto Sink Resolution y","Auto Sink Resolution z",\
                        "Orientation x","Orientation y", "Orientation z"])
                pd_df.to_csv(save_path)
            else:
                alert = QMessageBox()
                alert.setText("File already exists!")
                alert.exec()
        #resample_variable_list = refresh_variable_list()
        
        def load_config(load_path):
            if os.path.exists(load_path):    
                print(load_path)
                pd_df = pd.read_csv(load_path, header = 0)
                source_res_x.setText(str(pd_df["Source Resolution x"][0]))
                source_res_y.setText(str(pd_df["Source Resolution y"][0]))
                source_res_z.setText(str(pd_df["Source Resolution z"][0]))
                sink_res_x.setText(str(pd_df["Sink Resolution x"][0]))
                sink_res_y.setText(str(pd_df["Sink Resolution y"][0]))
                sink_res_z.setText(str(pd_df["Sink Resolution z"][0]))
                auto_source_res_x.setText(str(pd_df["Auto Source Resolution x"][0]))
                auto_source_res_y.setText(str(pd_df["Auto Source Resolution y"][0]))
                auto_source_res_z.setText(str(pd_df["Auto Source Resolution z"][0]))
                auto_sink_res_x.setText(str(pd_df["Auto Sink Resolution x"][0]))
                auto_sink_res_y.setText(str(pd_df["Auto Sink Resolution y"][0]))
                auto_sink_res_z.setText(str(pd_df["Auto Source Resolution z"][0]))
                orientation_x.setText(str(pd_df["Orientation x"][0]))
                orientation_y.setText(str(pd_df["Orientation y"][0]))
                orientation_z.setText(str(pd_df["Orientation z"][0]))
                #refresh_variable_list()
            else:
                alert = QMessageBox()
                alert.setText("Path does not exist!")
                alert.exec()    



        
        ### visualization of Widgets for resampling
        
        inner_layout.addWidget(QLabel("<b>Resample Paramter: <\b>"),0,0)
        inner_layout.addWidget(QLabel("Source Resolution: "),1,0)
        inner_layout.addWidget(QLabel("X:"),1,1)
        inner_layout.addWidget(source_res_x,1,2)
        inner_layout.addWidget(QLabel("Y:"),1,3)
        inner_layout.addWidget(source_res_y,1,4)
        inner_layout.addWidget(QLabel("Z:"),1,5)
        inner_layout.addWidget(source_res_z,1,6)

        inner_layout.addWidget(QLabel("Sink Resolution: "),2,0)
        inner_layout.addWidget(QLabel("X:"),2,1)
        inner_layout.addWidget(sink_res_x,2,2)
        inner_layout.addWidget(QLabel("Y:"),2,3)
        inner_layout.addWidget(sink_res_y,2,4)
        inner_layout.addWidget(QLabel("Z:"),2,5)
        inner_layout.addWidget(sink_res_z,2,6)


        inner_layout.addWidget(QLabel("     "),3,0)
        inner_layout.addWidget(QLabel("<b>Resample to Auto Paramter:</b>"),4,0)
        inner_layout.addWidget(QLabel("Source Resolution: "),5,0)
        inner_layout.addWidget(QLabel("X:"),5,1)
        inner_layout.addWidget(auto_source_res_x,5,2)
        inner_layout.addWidget(QLabel("Y:"),5,3)
        inner_layout.addWidget(auto_source_res_y,5,4)
        inner_layout.addWidget(QLabel("Z:"),5,5)
        inner_layout.addWidget(auto_source_res_z,5,6)

        inner_layout.addWidget(QLabel("Sink Resolution: "),6,0)
        inner_layout.addWidget(QLabel("X:"),6,1)
        inner_layout.addWidget(auto_sink_res_x,6,2)
        inner_layout.addWidget(QLabel("Y:"),6,3)
        inner_layout.addWidget(auto_sink_res_y,6,4)
        inner_layout.addWidget(QLabel("Z:"),6,5)
        inner_layout.addWidget(auto_sink_res_z,6,6)
        
        inner_layout.addWidget(QLabel("     "),7,0)
        inner_layout.addWidget(QLabel("Orientation: "),8,0)
        inner_layout.addWidget(QLabel("X:"),8,1)
        inner_layout.addWidget(orientation_x,8,2)
        inner_layout.addWidget(QLabel("Y:"),8,3)
        inner_layout.addWidget(orientation_y,8,4)
        inner_layout.addWidget(QLabel("Z:"),8,5)
        inner_layout.addWidget(orientation_z,8,6)

        inner_layout.addWidget(QLabel("    "),9,0)
        inner_layout.addWidget(config_path,10,0,10,5, alignment=Qt.AlignTop)
        inner_layout.addWidget(load_config_button,10,6)
        inner_layout.addWidget(save_config_button,10,7)
        inner_layout.addWidget(start_resampling_button,10,8)

        ###Signals and Slots connections for backend configuration 

        '''
        ## Every change in the different widgets is saved in a variable list
        orientation_x.textEdited.connect(refresh_variable_list)
        orientation_y.textEdited.connect(refresh_variable_list)
        orientation_z.textEdited.connect(refresh_variable_list)

        source_res_x.textEdited.connect(refresh_variable_list)
        source_res_y.textEdited.connect(refresh_variable_list)
        source_res_z.textEdited.connect(refresh_variable_list)

        sink_res_x.textEdited.connect(refresh_variable_list)
        sink_res_y.textEdited.connect(refresh_variable_list)
        sink_res_z.textEdited.connect(refresh_variable_list)

        auto_source_res_x.textEdited.connect(refresh_variable_list)
        auto_source_res_y.textEdited.connect(refresh_variable_list)
        auto_source_res_z.textEdited.connect(refresh_variable_list)

        auto_sink_res_x.textEdited.connect(refresh_variable_list)
        auto_sink_res_y.textEdited.connect(refresh_variable_list)
        auto_sink_res_z.textEdited.connect(refresh_variable_list)
        '''
        
        ## These two functions will load or save a variable list 
        load_config_button.pressed.connect(lambda: load_config(load_path = os.getcwd() + "/resampling_" + config_path.text() + ".csv"))
        save_config_button.pressed.connect(lambda: save_config(save_path = os.getcwd() + "/resampling_" + config_path.text() + ".csv"))
        start_resampling_button.clicked.connect(lambda: self.init_reference(source_res_x=float(source_res_x.text()), source_res_y=float(source_res_y.text())\
                                        ,source_res_z=float(source_res_z.text()),sink_res_x=float(sink_res_x.text()),sink_res_y=float(sink_res_y.text()),sink_res_z=float(sink_res_z.text())\
                                        ,auto_source_res_x=float(auto_source_res_x.text()),auto_source_res_y=float(auto_source_res_y.text()),auto_source_res_z=float(auto_source_res_z.text())\
                                        ,auto_sink_res_x=float(auto_sink_res_x.text()),auto_sink_res_y=float(auto_sink_res_y.text()),auto_sink_res_z=float(auto_sink_res_z.text()), orientation_x=int(orientation_x.text())\
                                        ,orientation_y=int(orientation_y.text()),orientation_z=int(orientation_z.text())))        



        outer_layout.addLayout(inner_layout)
        #outer_layout.addLayout(second_inner_layout)

        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab






    def cd_layout(self):
        tab = QWidget()
        outer_layout = QVBoxLayout()

        #Widgets for illumination correction
        flatfield_illumination = QComboBox()
        flatfield_illumination.insertItem(0,'None')
        scaling_illumination = QComboBox()
        scaling_illumination.insertItem(0,'mean')
        scaling_illumination.insertItem(1,'max')
        save_illumination = QCheckBox()         

        #Widgets for background correction
        shape_background_x = QLineEdit("7")
        shape_background_y = QLineEdit("7")
        form_background = QComboBox()
        form_background.insertItem(0,'Disk')
        form_background.insertItem(1,'Sphere')
        save_background = QCheckBox()

        #Widgets for equalization
        execute_equalization = QCheckBox()
        percentile_equalization_low = QLineEdit("0.5")
        percentile_equalization_high =  QLineEdit("0.95")
        max_value_equalization = QLineEdit("1.5")
        selem_equalization_x = QLineEdit("200")
        selem_equalization_y = QLineEdit("200")
        selem_equalization_z = QLineEdit("5")
        spacing_equalization_x = QLineEdit("50")
        spacing_equalization_y = QLineEdit("50")
        spacing_equalization_z = QLineEdit("5")
        interpolate_equalization = QLineEdit("1")
        save_equalization = QCheckBox()

        #Widgets for DoG filtering
        execute_dog_filter = QCheckBox()
        shape_dog_filter_x = QLineEdit("6")
        shape_dog_filter_y = QLineEdit("6")
        shape_dog_filter_z = QLineEdit("6")
        sigma_dog_filter = QLineEdit("None")
        sigma2_dog_filter = QLineEdit("None")
        save_dog_filter = QCheckBox()

        #Widgets for maxima detection
        hmax_maxima_det = QLineEdit("None")
        shape_maxima_det_x = QLineEdit("6")
        shape_maxima_det_y = QLineEdit("6")
        shape_maxima_det_z = QLineEdit("11")
        threshold_maxima_det = QComboBox()
        threshold_maxima_det.insertItem(0,"None")
        threshold_maxima_det.insertItem(1,"background mean")
        threshold_maxima_det.insertItem(2,"total mean")
        save_maxima_det = QCheckBox()         


        #widgets for intensity detection
        measure_intensity_det = QComboBox()
        measure_intensity_det.insertItem(0,"all")
        #measure_intensity_det.insertItem(1,"background")
        method_intensity_det = QComboBox()
        method_intensity_det.insertItem(0,"mean")
        method_intensity_det.insertItem(1,"max")
    

        #widgets for shape detection
        threshold_shape_det = QLineEdit("700")
        save_shape_det = QCheckBox()


        #widgets for cell detection functions and parameter loading
        detect_cells_button = QPushButton("Detect cells")
        atlas_assignment_button = QPushButton("Atlas assignment")
        voxelization_button = QPushButton("Voxelization")

        config_path = QLineEdit("Insert filename extension")
        load_config_button = QPushButton("Load parameters")
        save_config_button = QPushButton("Save parameters")

        #Widgets for processing paramteres
        amount_processes = QLineEdit('20')
        size_max = QLineEdit('20')
        size_min = QLineEdit('11')
        overlap = QLineEdit('10')


        def save_config(save_path):
            if not os.path.exists(save_path):
                cd_variable_list = [flatfield_illumination.currentIndex(),scaling_illumination.currentIndex(),shape_background_x.text(),shape_background_y.text(),\
                    form_background.currentIndex(),execute_equalization.isChecked(),percentile_equalization_low.text(),percentile_equalization_high.text(),max_value_equalization.text(),\
                        selem_equalization_x.text(),selem_equalization_y.text(),selem_equalization_z.text(),spacing_equalization_x.text(),\
                            spacing_equalization_y.text(),spacing_equalization_z.text(),interpolate_equalization.text(),execute_dog_filter.isChecked(),\
                                shape_dog_filter_x.text(),shape_dog_filter_y.text(),shape_dog_filter_z.text(),sigma_dog_filter.text(),sigma2_dog_filter.text(),\
                                    hmax_maxima_det.text(),shape_maxima_det_x.text(),shape_maxima_det_y.text(),shape_maxima_det_z.text(),\
                                            threshold_maxima_det.currentIndex(),measure_intensity_det.currentIndex(),method_intensity_det.currentIndex(),\
                                                threshold_shape_det.text(),amount_processes.text(),size_max.text(),size_min.text(),overlap.text()]           
                print(cd_variable_list)
                cd_columns = ["flatfield illumination","scaling illumination","shape background x","shape background y","form background index","execute eq","percentile eq low","percentile eq high",\
                    "max value eq","selem eq x","selem eq y","selem eq z", "spacing eq x","spacing eq y","spacing eq z","interpolate eq","execute dog",\
                        "shape dog x","shape dog y","shape dog z","sigma dog","sigma2 dog", "hmax maxima","shape maxima x","shape maxima y","shape maxima z",\
                            "threshold maxima","measure intensity", "method intensity det", "threshold shape det","amount processes","size max","size min",\
                                "overlap"]
                
                cd_df = pd.DataFrame([cd_variable_list], columns = cd_columns)
                cd_df.to_csv(save_path)
            else:
                alert = QMessageBox()
                alert.setText("File already exists!")
                alert.exec() 

        def load_config(load_path):
            if os.path.exists(load_path):
                cd_df = pd.read_csv(load_path, header = 0)
                flatfield_illumination.setCurrentIndex(cd_df["flatfield illumination"][0])
                scaling_illumination.setCurrentIndex(cd_df["scaling illumination"][0])
                shape_background_x.setText(str(cd_df["shape background x"][0]))
                shape_background_y.setText(str(cd_df["shape background y"][0]))
                form_background.setCurrentIndex(cd_df["form background index"][0])
                execute_equalization.setChecked(cd_df["execute eq"][0])
                percentile_equalization_low.setText(str(cd_df["percentile eq low"][0]))
                percentile_equalization_high.setText(str(cd_df["percentile eq high"][0]))
                max_value_equalization.setText(str(cd_df["max value eq"][0]))
                selem_equalization_x.setText(str(cd_df["selem eq x"][0]))
                selem_equalization_y.setText(str(cd_df["selem eq y"][0]))
                selem_equalization_z.setText(str(cd_df["selem eq z"][0]))
                spacing_equalization_x.setText(str(cd_df["spacing eq x"][0]))
                spacing_equalization_y.setText(str(cd_df["spacing eq y"][0]))
                spacing_equalization_z.setText(str(cd_df["spacing eq z"][0]))
                interpolate_equalization.setText(str(cd_df["interpolate eq"][0]))
                execute_dog_filter.setChecked(cd_df["execute dog"][0])
                shape_dog_filter_x.setText(str(cd_df["shape dog x"][0]))
                shape_dog_filter_y.setText(str(cd_df["shape dog y"][0]))
                shape_dog_filter_z.setText(str(cd_df["shape dog z"][0]))
                sigma_dog_filter.setText(str(cd_df["sigma dog"][0]))
                sigma2_dog_filter.setText(str(cd_df["sigma2 dog"][0]))
                hmax_maxima_det.setText(str(cd_df["hmax maxima"][0]))
                shape_maxima_det_x.setText(str(cd_df["shape maxima x"][0]))
                shape_maxima_det_y.setText(str(cd_df["shape maxima y"][0]))
                shape_maxima_det_z.setText(str(cd_df["shape maxima z"][0]))
                threshold_maxima_det.setCurrentIndex(cd_df["threshold maxima"][0])
                measure_intensity_det.setCurrentIndex(cd_df["measure intensity"][0])
                method_intensity_det.setCurrentIndex(cd_df["method intensity det"][0])
                threshold_shape_det.setText(str(cd_df["threshold shape det"][0]))
                amount_processes.setText(str(cd_df["amount processes"][0]))
                size_max.setText(str(cd_df["size max"][0]))
                size_min.setText(str(cd_df["size min"][0]))
                overlap.setText(str(cd_df["overlap"][0])) 
            else:
                alert = QMessageBox()
                alert.setText("File does not exist!")
                alert.exec()         



        #visualization for all variable features
        inner_layout1 = QGridLayout()
        inner_layout1.addWidget(QLabel("<b>Cell Detection Paramter:</b>"),0,0)

        #visualization for illumination correction
        inner_layout1.addWidget(QLabel("<b>Illumination correction: </b>"),1,0)
        inner_layout1.addWidget(QLabel("Flatfield: "),2,0)
        inner_layout1.addWidget(flatfield_illumination,2,1)
        inner_layout1.addWidget(QLabel("Scaling:"),3,0)
        inner_layout1.addWidget(scaling_illumination,3,1)
        #inner_layout1.addWidget(QLabel("Save: "),4,0)
        #inner_layout1.addWidget(save_illumination,4,1)

        #visualization of background correction
        inner_layout2 = QGridLayout()

        inner_layout2.addWidget(QLabel("<b>Background Correction:</b>"),1,0)
        inner_layout2.addWidget(QLabel("Shape:"),2,0)
        inner_layout2.addWidget(shape_background_x,2,1)
        inner_layout2.addWidget(shape_background_y,2,2)
        inner_layout2.addWidget(QLabel("Form:"),3,0)
        inner_layout2.addWidget(form_background,3,1)
        #inner_layout2.addWidget(QLabel("Save:"),4,0)
        #inner_layout2.addWidget(save_background,4,1)

        #visualization of equalization
        inner_layout3 = QGridLayout()

        inner_layout3.addWidget(QLabel("<b>Equalization:</b>"),1,0)
        inner_layout3.addWidget(QLabel("Perform equalization ?:"),2,0)
        inner_layout3.addWidget(execute_equalization,2,1)
        inner_layout3.addWidget(QLabel("Percentile:"),3,0)
        inner_layout3.addWidget(percentile_equalization_low,3,1)
        inner_layout3.addWidget(percentile_equalization_high,3,2)
        inner_layout3.addWidget(QLabel("Max Value:"),4,0)
        inner_layout3.addWidget(max_value_equalization,4,1)
        inner_layout3.addWidget(QLabel("Selem:"),5,0)
        inner_layout3.addWidget(selem_equalization_x,5,1)
        inner_layout3.addWidget(selem_equalization_y,5,2)
        inner_layout3.addWidget(selem_equalization_z,5,3)
        inner_layout3.addWidget(QLabel("Spacing:"),6,0)
        inner_layout3.addWidget(spacing_equalization_x,6,1)
        inner_layout3.addWidget(spacing_equalization_y,6,2)
        inner_layout3.addWidget(spacing_equalization_z,6,3)
        inner_layout3.addWidget(QLabel("Interpolate:"),7,0)
        inner_layout3.addWidget(interpolate_equalization,7,1)
        #inner_layout3.addWidget(QLabel("Save:"),8,0)
        #inner_layout3.addWidget(save_equalization,8,1)



        #visualization of dog filtering
        inner_layout4 = QGridLayout()

        inner_layout4.addWidget(QLabel("<b>DoG-Filtering:</b>"),1,0)
        inner_layout4.addWidget(QLabel("Execute DoG-Filtering?: "),2,0)
        inner_layout4.addWidget(execute_dog_filter,2,1)
        inner_layout4.addWidget(QLabel("Shape:"),3,0)
        inner_layout4.addWidget(shape_dog_filter_x,3,1)
        inner_layout4.addWidget(shape_dog_filter_y,3,2)
        inner_layout4.addWidget(shape_dog_filter_z,3,3)
        inner_layout4.addWidget(QLabel("Sigma:"),4,0)
        inner_layout4.addWidget(sigma_dog_filter,4,1)
        inner_layout4.addWidget(QLabel("Sigma2:"),5,0)
        inner_layout4.addWidget(sigma2_dog_filter,5,1)
        #inner_layout4.addWidget(QLabel("Save:"),6,0)
        #inner_layout4.addWidget(save_dog_filter,6,1)
    

        #visualization of maxima detection
        inner_layout5 = QGridLayout()

        inner_layout5.addWidget(QLabel("<b>Maxima Detection:</b>"),1,0)
        inner_layout5.addWidget(QLabel("H max:"),2,0)
        inner_layout5.addWidget(hmax_maxima_det,2,1)
        inner_layout5.addWidget(QLabel("Shape:"),3,0)
        inner_layout5.addWidget(shape_maxima_det_x,3,1)
        inner_layout5.addWidget(shape_maxima_det_y,3,2)
        inner_layout5.addWidget(shape_maxima_det_z,3,3)
        inner_layout5.addWidget(QLabel("Threshold:"),4,0)
        inner_layout5.addWidget(threshold_maxima_det,4,1)
        #inner_layout5.addWidget(QLabel("Save:"),5,0)
        #inner_layout5.addWidget(save_maxima_det,5,1)


        
        #visualization of intensity detection
        inner_layout6 = QGridLayout()

        inner_layout6.addWidget(QLabel("<b>Intensity Detection:</b>"),1,0)
        inner_layout6.addWidget(QLabel("Type of measure:"),2,0)
        inner_layout6.addWidget(measure_intensity_det,2,1)
        inner_layout6.addWidget(QLabel("Method of measure:"),3,0)
        inner_layout6.addWidget(method_intensity_det,3,1)


        #visualization of shape detection
        inner_layout7 = QGridLayout()

        inner_layout7.addWidget(QLabel("<b>Shape detection:</b>"),0,0)
        inner_layout7.addWidget(QLabel("Threshold:"),1,0)
        inner_layout7.addWidget(threshold_shape_det,1,1)
        #inner_layout7.addWidget(QLabel("Save:"),2,0)
        #inner_layout7.addWidget(save_shape_det,2,1)

        #visualization of Processing parameter widgets

        inner_layout8 = QGridLayout()

        inner_layout8.addWidget(QLabel("<b>Processing paramters:</b>"),0,0)
        inner_layout8.addWidget(QLabel("No. of parallel processes:"),1,0)
        inner_layout8.addWidget(amount_processes,1,1)
        inner_layout8.addWidget(QLabel("Size max:"),1,2)
        inner_layout8.addWidget(size_max,1,3)
        inner_layout8.addWidget(QLabel("Size min:"),1,4)
        inner_layout8.addWidget(size_min,1,4)
        inner_layout8.addWidget(QLabel("Overlap:"),1,5)
        inner_layout8.addWidget(overlap,1,6)


        #visualization of loading,saving and detection functions
        inner_layout9 = QHBoxLayout()

        inner_layout9.addWidget(config_path)
        inner_layout9.addWidget(load_config_button)
        inner_layout9.addWidget(save_config_button)
        inner_layout9.addWidget(detect_cells_button)
        inner_layout9.addWidget(atlas_assignment_button)
        inner_layout9.addWidget(voxelization_button)

        

        # Connection of signals and slots for cell detection

        load_config_button.clicked.connect(lambda: load_config(load_path = os.getcwd() + "/cell_detection_" + config_path.text() + ".csv"))
        save_config_button.clicked.connect(lambda: save_config(save_path = os.getcwd() + "/cell_detection_" + config_path.text() + ".csv"))
        
               

        detect_cells_button.clicked.connect(lambda: self.cell_detection(flatfield_illumination = flatfield_illumination.currentIndex(),scaling_illumination = scaling_illumination.currentIndex(),shape_background_x = shape_background_x.text(),shape_background_y = shape_background_y.text(),\
                    form_background = form_background.currentIndex(),execute_equalization= execute_equalization.isChecked(),percentile_equalization_low = percentile_equalization_low.text(),percentile_equalization_high = percentile_equalization_high.text(),max_value_equalization = max_value_equalization.text(),\
                        selem_equalization_x =  selem_equalization_x.text(),selem_equalization_y = selem_equalization_y.text(),selem_equalization_z = selem_equalization_z.text(),spacing_equalization_x = spacing_equalization_x.text(),\
                            spacing_equalization_y = spacing_equalization_y.text(),spacing_equalization_z = spacing_equalization_z.text(),interpolate_equalization = interpolate_equalization.text(),execute_dog_filter = execute_dog_filter.isChecked(),\
                                shape_dog_filter_x = shape_dog_filter_x.text(),shape_dog_filter_y = shape_dog_filter_y.text(),shape_dog_filter_z = shape_dog_filter_z.text(),sigma_dog_filter = sigma_dog_filter.text(),sigma2_dog_filter = sigma2_dog_filter.text(),\
                                    hmax_maxima_det = hmax_maxima_det.text(),shape_maxima_det_x = shape_maxima_det_x.text(),shape_maxima_det_y = shape_maxima_det_y.text(),shape_maxima_det_z = shape_maxima_det_z.text(),\
                                            threshold_maxima_det = threshold_maxima_det.currentIndex(),measure_intensity_det = measure_intensity_det.currentIndex(),method_intensity_det = method_intensity_det.currentIndex(),\
                                                threshold_shape_det = threshold_shape_det.text(),amount_processes = int(amount_processes.text()),size_maximum = int(size_max.text()),size_minimum = int(size_min.text()),area_of_overlap = int(overlap.text())))
        
        atlas_assignment_button.clicked.connect(lambda: self.atlas_assignment())
        voxelization_button.clicked.connect(lambda: self.voxelization())
        
        #inner_layout.addWidget(QPushButton("Second"))
        outer_layout.addLayout(inner_layout1)
        outer_layout.addLayout(inner_layout2)
        outer_layout.addLayout(inner_layout3)
        outer_layout.addLayout(inner_layout4)
        outer_layout.addLayout(inner_layout5)
        outer_layout.addLayout(inner_layout6)
        outer_layout.addLayout(inner_layout7)
        outer_layout.addLayout(inner_layout8)
        outer_layout.addLayout(inner_layout9)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab


        '''
    def visualization_layout(self):
        tab = QWidget()
        outer_layout = QVBoxLayout()

        open_napari = QPushButton("Open Napari")

        outer_layout.addWidget(open_napari)

        open_napari.clicked.connect(lambda: self.view_napari())


        tab.setLayout(outer_layout)
        return tab
        '''

        '''
        tab = QWidget()
        outer_layout = QVBoxLayout()
        
        ## Widgets for visualization methods provided by ClearMap

        # simple Visualization
        visualize_illumination_corr = QPushButton("Illumination correction results")
        visualize_background_corr = QPushButton("Background correction results")
        visualize_equalization = QPushButton("Equalization results")
        visualize_dog_filtering = QPushButton("DoG filtering results")
        visualize_maxima_detection = QPushButton("Maxima detection results")
        visualize_shape_detection = QPushButton("Shape detection results")


        # 3D Visualization
        cell_size = QLineEdit("20")
        visualize3D_raw = QPushButton("Raw data 3D results")
        visualize3D_filtered = QPushButton("Filtered data 3D results")

        # Histograms
        cell_size2 = QLineEdit("20")
        histograms_raw = QPushButton("Histogram raw data")
        histograms_filtered = QPushButton("Histogram filtered data")


        ## Widgets for own visualization methods
        
         
        ## visualization for simple visualization widgets
        inner_layout1 = QGridLayout()
        
        inner_layout1.addWidget(QLabel("<b>Visualize simple:</b>"),0,0)
        inner_layout1.addWidget(visualize_illumination_corr,1,0) 
        inner_layout1.addWidget(visualize_background_corr,2,0)
        inner_layout1.addWidget(visualize_equalization,3,0)
        inner_layout1.addWidget(visualize_dog_filtering,4,0)
        inner_layout1.addWidget(visualize_maxima_detection,5,0)
        inner_layout1.addWidget(visualize_shape_detection,6,0)


        inner_layout1.addWidget(QLabel("<b>Visualize 3D:</b>"),7,0)
        inner_layout1.addWidget(visualize3D_raw,8,0)
        inner_layout1.addWidget(QLabel("Size of filtered cells:"),9,0)
        inner_layout1.addWidget(cell_size,10,0)
        inner_layout1.addWidget(visualize3D_filtered,11,0)

        inner_layout1.addWidget(QLabel("<b>Histograms:"),12,0)
        inner_layout1.addWidget(histograms_raw,13,0)
        inner_layout1.addWidget(QLabel("Size of filtered cells:"),14,0)
        inner_layout1.addWidget(cell_size2,15,0)
        inner_layout1.addWidget(histograms_filtered,16,0)





        outer_layout.addLayout(inner_layout1)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab
        '''



    


    
if __name__ == "__main__":
    app = QApplication([])
    main_window = Main_Window()
    main_window.show()
    app.exec()











'''
main_window = QWidget()

menubar = QMenuBar()
outer_layout = QVBoxLayout()
stacked_layout = QHBoxLayout()
first = menubar.addAction("First")
second = menubar.addAction("Second")


top = QPushButton("Top")
stacked_layout.addWidget(menubar)
stacked_layout.addWidget(QLabel("Hello world!"))
stacked_layout.addWidget(top)


ok = QPushButton("Ok")
stacked_layout.addWidget(menubar)
stacked_layout.addWidget(ok)

#stacked_layout.addWidget(window1)
#stacked_layout.addWidget(window2)
outer_layout.addLayout(stacked_layout)
main_window.setLayout(outer_layout)

main_window.show()
'''

