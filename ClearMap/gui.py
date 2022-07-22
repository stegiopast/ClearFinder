from decimal import ROUND_FLOOR
from fileinput import filename
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import *
#from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

import os
import pathlib
import re
import string
import sys

from PyQt5.QtWidgets import QLineEdit
from pyparsing import empty

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats

from ClearMap.Environment import *
import numpy.lib.recfunctions as rfn
import napari

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

print(sys.version)

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

    #def plot(self):  
        # random data
    #    data = [random.random() for i in range(10)]

        # clearing old figure
    #    self.figure.clear()

        # create an axis
    #    ax = self.figure.add_subplot(111)

        # plot data
    #    ax.plot(data, '*-')

        # refresh canvas
    #    self.canvas.draw()

class RenameBox(QWidget):
    def __init__(self,
                 filenameToCheck: str,
                 position: int,
                 _path: str):
        super().__init__()
        self.path = _path
        self.position = position
        self.renameBox = None
        self.setWindowTitle("ClearMap2 GUI")
        self.filenameToCheck = filenameToCheck
        self.chosenChannel = "C01"
        self.isFirstUpdate = True
        self.shiftBar = QLineEdit("0")
        self.accept = QPushButton("Accept")
        self.reject = QPushButton("Reject and shift")
        self.quitRenaming = QPushButton("Quit Renaming")
        self.layout = QGridLayout()
        self.updateLayout()
        self.setLayout(self.layout)

    def updateLayout(self) -> QGridLayout:
        self.intShift = int(self.shiftBar.text())
        self.newPosition = self.position + self.intShift
        if self.newPosition >= 0:
            self.update(self.newPosition)
        else:
            self.newPosition = 0
            self.update(self.newPosition)
        print("Filename: ", self.filenameToCheck[self.position:len(self.filenameToCheck)])
        print("Current Filename: ", self.currentFilename)
        print(self.position)
        innerLayout = QGridLayout()
        innerLayout.addWidget(QLabel("Current output Filename:"), 0, 0)
        innerLayout.addWidget(QLabel(self.currentFilename), 0, 1)
        innerLayout.addWidget(QLabel("      "), 1, 0)
        innerLayout.addWidget(QLabel("Does filename not fit to template 0001_C01.tif - 9999_C01.tif ?"), 2, 0)
        innerLayout.addWidget(QLabel("Provide shift (+ and - allowed) and Reject:"), 3, 0)
        innerLayout.addWidget(self.shiftBar, 3, 1)
        innerLayout.addWidget(self.reject, 3, 2)
        innerLayout.addWidget(QLabel("      "), 4, 0)
        innerLayout.addWidget(QLabel("Does filename fit ?"), 5, 0)
        innerLayout.addWidget(QLabel("Press accept:"), 6, 0)
        innerLayout.addWidget(self.accept, 6, 1)
        innerLayout.addWidget(QLabel("      "), 7, 0)
        innerLayout.addWidget(QLabel("Doesn't the filename fit at all?"), 8, 0)
        innerLayout.addWidget(QLabel("Press Quit:"), 9, 0)
        innerLayout.addWidget(self.quitRenaming, 9, 1)

        self.deleteItemsOfLayout(self.layout)

        self.layout.addLayout(innerLayout, 0, 0)

        return self.layout

    def update(self, currentPosition: int) -> str:  #Searches for the desired pattern in filename, if not found directly (isFirstUpdate), the user needs to shift the string in the desired form
        self.position = currentPosition
        if self.isFirstUpdate:
            if (re.search(r'Z[0-9]{4}_C0+', self.filenameToCheck)):
                findPattern = re.search(r'Z[0-9]{4}_C0+', self.filenameToCheck)
                self.position = findPattern.span()[0] + 1

            elif (re.search(r'Z[0-9]{3}_C0+', self.filenameToCheck)):
                findPattern = re.search(r'Z[0-9]{3}_C0+', self.filenameToCheck)
                self.position = findPattern.span()[0] + 1

            self.isFirstUpdate = False

        self.currentFilename = self.filenameToCheck[self.position:len(self.filenameToCheck)]

    def deleteItemsOfLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteItemsOfLayout(item.layout())

    def perform_cut(self):  # Performs the renaming of the files
        print("path:", self.path)
        for file in pathlib.Path(self.path).iterdir():
            if file.is_file():
                old_name = file.stem + ".tif"
                new_name = old_name[self.position:len(old_name)]
                dir = file.parent

                newObj = re.match(r'^[0-9]{3}_', new_name)
                if newObj:
                    new_name = "Z0" + new_name
                else:
                    newObj = re.match(r'[0-9]', new_name)
                    if newObj:
                        new_name = "Z" + new_name
                print(new_name)
                file.rename(pathlib.Path(dir, new_name))


class Main_Window(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClearMap2 GUI")
        layout = QVBoxLayout()
        self.setLayout(layout)
        tabs = QTabWidget()
        tabs.addTab(self.rename_layout(), "Determine Path | Rename Path")
        tabs.addTab(self.resample_layout(), "Resampling | Alignment")
        tabs.addTab(self.cd_layout(), "Cell Detection")
        tabs.addTab(self.preanalysis_layout(), "Grouping and Normalization")
        tabs.addTab(self.analysis_layout(),"Analysis and Plots")
        layout.addWidget(tabs)
        self.debug = False

    """
    Initialize Workspace, WorkingDirectory and Channel of Analysis
    """
    def initWorkspace(self, path='/home/cellfinder_data', channel=0):
        if channel == 0:
            channelStr = "C01"
        elif channel == 1:
            channelStr = "C02"
        self.chosenChannel = channelStr
        myWorkingDirectory = path

        if os.path.exists(myWorkingDirectory):
            #myWorkingDirectory is the base directory <- alles relativ dazu
            expression_raw = 'Signal/' + channelStr + '/Z<Z,4>_' + channelStr + '.tif'  # applies for example : "Z0001_C01.tif, Z0023..."
            expression_auto = 'Auto/Z<Z,4>_' + 'C01' + '.tif'
            ws = wsp.Workspace('CellMap', directory=myWorkingDirectory);
            ws.update(raw_C01='Signal/C01/Z<Z,4>_C01.tif',
                      raw_C02='Signal/C02/Z<Z,4>_C02.tif',
                      stitched_C01='stitched_C01.npy',
                      stitched_C02='stitched_C02.npy',
                      resampled_C01='resampled_C01.tif',
                      resampled_C02='resampled_C02.tif')
            if self.chosenChannel == "C01":
                ws.update(raw_C01=expression_raw, autofluorescence=expression_auto)
            if self.chosenChannel == "C02":
                ws.update(raw_C02=expression_raw, autofluorescence=expression_auto)

            if os.path.exists(myWorkingDirectory + '/stitched_' + self.chosenChannel + '.tif'):
                expressionStitched = 'stitched_' + self.chosenChannel + '.npy'
                if self.chosenChannel == "C01":
                    ws.update(stitched_C01=expressionStitched)
                if self.chosenChannel == "C02":
                    ws.upate(stitched_C02=expressionStitched)

            if os.path.exists(myWorkingDirectory + '/resampled_' + self.chosenChannel + '.tif'):
                expression_resampled = 'resampled_' + self.chosenChannel + '.tif'
                if self.chosenChannel == "C01":
                    ws.update(resampled_C01=expression_resampled)
                if self.chosenChannel == "C02":
                    ws.update(resampled_C02=expression_resampled)
            ws.info()
            print(ws.filename('cells', postfix='raw_C01'))
            self.ws = ws
            self.myWorkingDirectory = myWorkingDirectory

            print("Worksapce: ", self.ws)
            print("Working dir:", self.myWorkingDirectory)
            print("Channel chosen:", self.chosenChannel)
            return [ws, myWorkingDirectory]
        else:
            print("Path does not exist!")

    def createTestdata(self, index: int):
        if index == 0:
            slicing = (slice(700, 816), slice(1300, 1500), slice(1100, 1130));
            self.ws.create_debug('stitched_' + self.chosenChannel, slicing=slicing);

        elif index == 1:
            slicing = (slice(500, 616), slice(1100, 1300), slice(1100, 1130));
            self.ws.create_debug('stitched_' + self.chosenChannel, slicing=slicing);
        else:
            pass

    def startDebug(self):
        self.ws.debug = True;

    def endDebug(self):
        self.ws.debug = False;

    def changeDebug(self):
        if self.debug == False:
            self.ws.debug = True
            self.debug = True
        else:
            self.ws.debug = False
            self.debug = False
        print(self.ws.info())


    """
    In ResampleTab of GUI;
    Takes Resolution Parameter and Resamples the files 
    ClearMap Code
    """

    def initReference(self, # Default values of resolution Todo: See also belonging QWidget for default values?
                      source_res_x=3.02,
                      source_res_y=3.02,
                      source_res_z=3,
                      sink_res_x=10,
                      sink_res_y=10,
                      sink_res_z=10,
                      auto_source_res_x=3.02,
                      auto_source_res_y=3.02,
                      auto_source_res_z=3,
                      auto_sink_res_x=25,
                      auto_sink_res_y=25,
                      auto_sink_res_z=25,
                      orientation_x=1,
                      orientation_y=2,
                      orientation_z=3):

        if not os.path.exists(self.myWorkingDirectory + "/elastix_resampled_to_auto_" + self.chosenChannel):
            os.mkdir(self.myWorkingDirectory + "/elastix_resampled_to_auto_" + self.chosenChannel)
        else:
            print(self.myWorkingDirectory + "/elastix_resampled_to_auto_" + self.chosenChannel + " already exists\n")

        if not os.path.exists(self.myWorkingDirectory + "/elastix_auto_to_reference_" + self.chosenChannel):
            os.mkdir(self.myWorkingDirectory + "/elastix_auto_to_reference_" + self.chosenChannel)
        else:
            print(self.myWorkingDirectory + "/elastix_auto_to_reference_" + self.chosenChannel + " already exists\n")

        resourcesDirectory = settings.resources_path
        annotation_file, reference_file, distance_file = ano.prepare_annotation_files(slicing=(slice(None),
                                                                                               slice(None),
                                                                                               slice(0,640)),
                                                                                      orientation=(orientation_x, orientation_y, orientation_z),
                                                                                      overwrite=False,
                                                                                      verbose=True);

        align_channels_affine_file = io.join(resourcesDirectory, 'Alignment/align_affine.txt')
        align_reference_affine_file = io.join(resourcesDirectory, 'Alignment/align_affine.txt')
        align_reference_bspline_file = io.join(resourcesDirectory, 'Alignment/align_bspline.txt')

        resample_parameter = {"source_resolution": (source_res_x, source_res_y, source_res_z),  # Resolution of your own files!
                              "sink_resolution": (sink_res_x, sink_res_y, sink_res_z),
                              "processes": 4,
                              "verbose": True};

        source = self.ws.source('raw_' + self.chosenChannel);
        sink = self.ws.filename('stitched_' + self.chosenChannel);
        io.convert(source, sink, verbose=True)

        res.resample(self.ws.filename('stitched_' + self.chosenChannel),
                     sink=self.ws.filename('resampled_' + self.chosenChannel), **resample_parameter)

        resample_parameter_auto = {"source_resolution": (auto_source_res_x, auto_source_res_y, auto_source_res_z),
                                   "sink_resolution": (auto_sink_res_x, auto_sink_res_y, auto_sink_res_z),
                                   "processes": 4,
                                   "verbose": True};

        res.resample(self.ws.filename('autofluorescence'),
                     sink=self.ws.filename('resampled_' + self.chosenChannel,postfix='autofluorescence'),
                     **resample_parameter_auto)

        align_channels_parameter = {
            # moving and reference images
            "moving_image": self.ws.filename('resampled_' + self.chosenChannel, postfix='autofluorescence'),
            "fixed_image": self.ws.filename('resampled_' + self.chosenChannel),

            # elastix parameter files for alignment
            "affine_parameter_file": align_channels_affine_file,
            "bspline_parameter_file": None,

            # directory of the alig'/home/nicolas.renier/Documents/ClearMap_Ressources/Par0000affine.txt',nment result
            # "result_directory" :  "/raid/CellRegistration_Margaryta/ClearMap1_2/ClearMap2/elastix_resampled_to_auto"
            "result_directory": self.myWorkingDirectory + "/elastix_resampled_to_auto_" + self.chosenChannel
        };

        # erstes algnment sollte klappen!
        elx.align(**align_channels_parameter);

        align_reference_parameter = {
            # moving and reference images
            "moving_image": reference_file,
            "fixed_image": self.ws.filename('resampled_' + self.chosenChannel, postfix='autofluorescence'),

            # elastix parameter files for alignment
            "affine_parameter_file": align_reference_affine_file,
            "bspline_parameter_file": align_reference_bspline_file,
            # directory of the alignment result
            "result_directory": self.myWorkingDirectory + "/elastix_auto_to_reference_" + self.chosenChannel
        };

        # dimensionsfehler möglicherweise
        elx.align(**align_reference_parameter);
        return

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
    def analyse_csv(self,df: pd.DataFrame,reference_df: pd.DataFrame, trackedLevels: list) -> pd.DataFrame:
        total_cellcount = int(df["total_cells"].sum())  # get total cellcount for reference
        df["name"] = df["structure_name"]
        reference_df_ID = reference_df.set_index(reference_df["id"])
        reference_df_Name = reference_df.set_index(reference_df["name"])

        resultframe = self.createResultframe(reference_df, trackedLevels) # Todo: Schauen ob alles läuft und umbenennen, damit klarer wird was getan wird
        for i in range(len(df.iloc[:, 0])):  # Iterates over all entries in summary.csv
            name = df.iloc[i]["name"]  # get the Name of the Region at current index
            print(name)
            try:
                df_temp = reference_df_Name.loc[name]
            except KeyError:
                samplename = self.myWorkingDirectory[-4:]
                filename = self.myWorkingDirectory + "/" + samplename + "_unmapped_regions.csv" #Todo: Passt das, sollte jetzt nicht mehr in Analysis Output sondern in SampleFolder greschrieben werden
        
                with open(filename, "a+") as KeyError_file:
                    KeyError_file.write(str(name) + ";" + str(df.iloc[i]["total_cells"]) + "\n")
                continue
            temp_name = df_temp["name"]
            index_outerCount = resultframe.index[resultframe["Region"] == temp_name]
            cellcountRegion = df[df["structure_name"] == resultframe["Region"][index_outerCount[0]]][
                "total_cells"].sum()  # Hier mit temp_name arbeiten
            resultframe.loc[index_outerCount[0], "RegionCellCount"] += cellcountRegion
            resultframe.loc[index_outerCount[0], "RegionCellCountSummedUp"] += cellcountRegion
            if not df_temp.empty:
                while (int(df_temp["st_level"]) >= 0):
                    if (int(df_temp["st_level"]) == 0):
                        break  # index of Brain_structure of parent_ID is taken
                    df_temp = reference_df_ID.loc[int(df_temp["parent_structure_id"])]
                    temp_name = df_temp["name"]
                    index_innerCount = resultframe.index[resultframe["Region"] == temp_name]
                    resultframe.loc[index_innerCount[0], "RegionCellCountSummedUp"] += cellcountRegion

        return resultframe

    """
    Converts a CSV to a XML File, for visualization in napari
    """
    def writeXml(self, df:pd.DataFrame, pathname:str, filename:str):
        df = pd.DataFrame(df)
        filename = filename[0:-3] + "xml"
        row_counter = 1
        dfLength = len(df)
        with open(pathname+filename, "a") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<CellCounter_Marker_File>\n')
            file.write('  <Image_Properties>\n')
            file.write('    <Image_Filename>placeholder.tif</Image_Filename>\n')
            file.write('  </Image_Properties>\n')
            file.write('  <Marker_Data>\n')
            file.write('    <Current_Type>1</Current_Type>\n')
            file.write('    <Marker_Type>\n')
            file.write('      <Type>1</Type>\n')
            for i in range(len(df.iloc[:, 0])):
                row_counter = row_counter + 1
                if (row_counter % 10000 == 0):
                    print(str(row_counter), "/", str(dfLength), " lines are processes")
                file.write('      <Marker>\n')
                file.write('        <MarkerX>' + str(df.iloc[i, :].x) + '</MarkerX>\n')
                file.write('        <MarkerY>' + str(df.iloc[i, :].y) + '</MarkerY>\n')
                file.write('        <MarkerZ>' + str(df.iloc[i, :].z) + '</MarkerZ>\n')
                file.write('      </Marker>\n')
            file.write('    </Marker_Type>\n')
            file.write('  </Marker_Data>\n')
            file.write('</CellCounter_Marker_File>\n')


    """

    """
    def write_transformed_xml(self, dataframe: pd.DataFrame, pathname:str, filename:str):
        df = pd.DataFrame(dataframe)
        filename = filename[0:-3] + "xml"
        with open(pathname+filename, "a") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<CellCounter_Marker_File>\n')
            file.write('  <Image_Properties>\n')
            file.write('    <Image_Filename>placeholder.tif</Image_Filename>\n')
            file.write('  </Image_Properties>\n')
            file.write('  <Marker_Data>\n')
            file.write('    <Current_Type>1</Current_Type>\n')
            file.write('    <Marker_Type>\n')
            file.write('      <Type>1</Type>\n')
            for i in (range(len(df.iloc[:, 0]))):
                file.write('      <Marker>\n')
                file.write('        <MarkerX>' + str(df.iloc[i, :].xt) + '</MarkerX>\n')
                file.write('        <MarkerY>' + str(df.iloc[i, :].yt) + '</MarkerY>\n')
                file.write('        <MarkerZ>' + str(df.iloc[i, :].zt) + '</MarkerZ>\n')
                file.write('      </Marker>\n')
            file.write('    </Marker_Type>\n')
            file.write('  </Marker_Data>\n')
            file.write('</CellCounter_Marker_File>\n')

    """
    Calls the writeXML-Function to actually transfer certain CSV Files to XML
    """
    def processCellsCsv(self):
        pathname2xmlfolder = self.myWorkingDirectory + "/" + self.chosenChannel + "xmlFiles"
        if not os.path.exists(pathname2xmlfolder):
            os.makedirs(self.myWorkingDirectory + "/" + self.chosenChannel + "xmlFiles")

        df_filename = "/cells_" + self.chosenChannel + ".csv"
        df_name = self.myWorkingDirectory + df_filename
        df = pd.read_csv(df_name, header=0, sep=";")

        df_no_label_filename = "/cells_" + self.chosenChannel + "_no_label.csv"
        df_no_label_name = self.myWorkingDirectory + df_no_label_filename
        df_no_label = df[df["name"] == "No label"]
        df_no_label.to_csv(df_no_label_name, sep=";")

        df_universe_filename = "/cells_" + self.chosenChannel + "_universe.csv"
        df_universe_name = self.myWorkingDirectory + df_universe_filename
        df_universe = df[df["name"] == "universe"]
        df_universe.to_csv(df_universe_name, sep=";")

        df_final_filename = "/cells_" + self.chosenChannel + "_final.csv"
        df_final_name = self.myWorkingDirectory + df_final_filename
        df_final = df[df["name"] != "universe"]
        df_final = df_final[df_final["name"] != "No label"]
        df_final.to_csv(df_final_name, sep=";")


        df_final_transformed_filename = "/cells_" + self.chosenChannel + "_transformed_final.csv"


        # Multiprocessing the convertion from CSV to XML
        p1 = Process(target=self.writeXml, args=(df, pathname2xmlfolder, df_filename))
        p1.start()
        p2 = Process(target=self.writeXml, args=(df_no_label, pathname2xmlfolder, df_no_label_filename))
        p2.start()
        p3 = Process(target=self.writeXml, args=(df_universe, pathname2xmlfolder, df_universe_filename))
        p3.start()
        p4 = Process(target=self.writeXml, args=(df_final, pathname2xmlfolder, df_final_filename))
        p4.start()
        p5 = Process(target=self.write_transformed_xml, args=(df_final, pathname2xmlfolder, df_final_transformed_filename))
        p5.start()

        df_final = df_final["name"].value_counts()
        df_final = pd.DataFrame(df_final)
        df_final["structure_name"] = df_final.index
        df_final = df_final.reset_index(drop=True)
        df_final.rename(columns={"name": "total_cells"}, inplace=True)

        df_final.to_csv(self.myWorkingDirectory + "/cells_" + self.chosenChannel + "_summarized_counts.csv", sep=";")



    """
    calls the analyse_csv Function to actually create the embedded_ontology.csv which is needed from each sample for the analysis
    """
    def embedOntology(self):
        reference_df = pd.read_csv("/home/clearmap_data/ClearMap/ontology_mouse.csv",
                               # Current Refernce Dataframe for mapping
                               # File which stores all important Brain Regions (Atlas?)
                               sep=";",  # Separator
                               header=0,  # Header
                               index_col=0)  # Index Col

        trackedLevels = self.createTrackingList(reference_df)
        df = pd.read_csv(self.myWorkingDirectory + "/cells_" + self.chosenChannel + "_summarized_counts.csv", header=0, sep=";")

        samplename = self.myWorkingDirectory[-4:]
        new_df = self.analyse_csv(df,reference_df, trackedLevels)
        new_df_name = self.myWorkingDirectory + "/" + samplename + "_" + self.chosenChannel + "_embedded_ontology.csv"
        new_df.to_csv(new_df_name, sep=";", index=0)
        return


    """
    ClearMap Code
    """
    def cell_detection(self,    # Defaul Parameter of CellDetectionTab
                       flatfield_illumination=None,
                       scaling_illumination="max",
                       shape_background_x=7,
                       shape_background_y=7,
                       form_background="Disk",
                       execute_equalization=False,
                       percentile_equalization_low=0.5,
                       percentile_equalization_high=0.95,
                       max_value_equalization=1.5,
                       selem_equalization_x=200,
                       selem_equalization_y=200,
                       selem_equalization_z=5,
                       spacing_equalization_x=50,
                       spacing_equalization_y=50,
                       spacing_equalization_z=5,
                       interpolate_equalization=1,
                       execute_dog_filter=False,
                       shape_dog_filter_x=6,
                       shape_dog_filter_y=6,
                       shape_dog_filter_z=6,
                       sigma_dog_filter=None,
                       sigma2_dog_filter=None,
                       hmax_maxima_det=None,
                       shape_maxima_det_x=6,
                       shape_maxima_det_y=6,
                       shape_maxima_det_z=11,
                       threshold_maxima_det=297.380,
                       measure_intensity_det="Source",
                       method_intensity_det="mean",
                       threshold_shape_det=200,             # Todo: Change Default to 200? If yes see also belonging QWidget
                       save_shape_det=True,
                       amount_processes=10,
                       size_maximum=20,
                       size_minimum=11,
                       area_of_overlap=10):

        # Coversion of illumination_correction integers to dictionairy entries of ClearMap
        if flatfield_illumination == 0:
            flatfield_illumination = None

        if scaling_illumination == 0:
            scaling_illumination = 'mean'
        elif scaling_illumination == 1:
            scaling_illumination = 'max'

        # Conversion of background correction values
        shape_background_x = int(shape_background_x)
        shape_background_y = int(shape_background_y)

        if form_background == 0:
            form_background = 'Disk'
        elif form_background == 1:
            form_background = 'Sphere'

        # conversion of equalization values
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

        # conversion of dog filtering values
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

        # conversion of maxima detection values
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

        # conversion of intensity detection values
        measure_intensity_det = ['source', 'illumination', 'background', 'equalized', 'dog'];

        if method_intensity_det == 0:
            method_intensity_det = 'mean'
        elif method_intensity_det == 1:
            method_intensity_det = 'max'

        # Conversion of Shape detection values
        threshold_shape_det = int(threshold_shape_det)
        cell_detection_parameter = cells.default_cell_detection_parameter.copy();

        ## Options illumination_correction
        cell_detection_parameter['iullumination_correction']['flatfield'] = flatfield_illumination  # A default flatfield is provided // Array or str with flatfield estimate
        cell_detection_parameter['iullumination_correction']['scaling'] = scaling_illumination  # max','mean' or None Optional scaling after flat field correction // float

        ## Options in 'background_correction'
        cell_detection_parameter['background_correction']['shape'] = (shape_background_x, shape_background_y)  # Tuple represents cell shape // tuple (int,int)
        cell_detection_parameter['background_correction']['form'] = form_background  # 'Sphere' #Describes cell shape, I didnt find an alternative to disk // str

        if execute_equalization == 1:
            cell_detection_parameter['equalization'] = dict(percentile=(percentile_equalization_low, percentile_equalization_high),
                                                            max_value=max_value_equalization,
                                                            selem=(selem_equalization_x, selem_equalization_y, selem_equalization_z),
                                                            spacing=(spacing_equalization_x, spacing_equalization_y, spacing_equalization_z),
                                                            save=None)
        else:
            cell_detection_parameter['equalization'] = None
        # c DoG Filter
        if execute_dog_filter == 1:
            cell_detection_parameter['dog_filter']['shape'] = (shape_dog_filter_x,
                                                               shape_dog_filter_y,
                                                               shape_dog_filter_z)  # Shape of the filter, usually near cell size // tuple(int,int,int)
            cell_detection_parameter['dog_filter']['sigma'] = sigma_dog_filter  # usually determined by shape, but is std inner gaussian //tuple(float,float)
            cell_detection_parameter['dog_filter']['sigma2'] = sigma2_dog_filter  # usually determined by shape, but is std outer gaussian //tuple(float,float)
        else:
            cell_detection_parameter['dog_filter'] = None
        ## Maxima detection
        cell_detection_parameter['maxima_detection']['h_max'] = hmax_maxima_det  # Height for the extended maxima. If None simple locasl maxima detection. //float // NOT WORKING SO FAR ?
        cell_detection_parameter['maxima_detection']['shape'] = (shape_maxima_det_x,
                                                                 shape_maxima_det_y,
                                                                 shape_maxima_det_z)  # Shape of the structural element. Near typical cell size. // tuple(int, int)
        # Idea is to take the mean of the values in each procedure + 2*std_deviation, to always predict a significant upregulation Z-test // Has to be implemented
        # We could also implement a filter function at that point, by overwriting data that is 4 std_dev away from the mean, whcih seems unrealistic
        cell_detection_parameter['maxima_detection']['threshold'] = None  # 0.55 good value fter dog + equalizaziont for 3258  #5 good value after equalization for 3258 #250 Best so fat without equalization for 3258 # Only maxima above this threshold are detected. If None all are detected // float

        ## Intensity_detection
        cell_detection_parameter['intensity_detection']['measure'] = measure_intensity_det;  # we decided to measure all intensities
        cell_detection_parameter['intensity_detection']['method'] = method_intensity_det  # {'max'|'min','mean'|'sum'} # Use method to measure intensity of the cell

        ## Shape_detection
        cell_detection_parameter['shape_detection']['threshold'] = threshold_shape_det;

        ## Self edited threshold
        cell_detection_parameter['threshold'] = threshold_maxima_det

        processing_parameter = cells.default_cell_detection_processing_parameter.copy();
        processing_parameter.update(processes=amount_processes,  # 15, #20,
                                    #optimization = True,  #Todo: Why commented?
                                    size_max=size_maximum,  # 35 100
                                    size_min=size_minimum,  # 30 32
                                    overlap=area_of_overlap,  # 10 30
                                    verbose=True)  # Set True if process needs to be investigated // Lead to the print of process checkpoints

        cells.detect_cells(self.ws.filename('stitched_' + self.chosenChannel),
                           self.ws.filename('cells', postfix='raw_' + self.chosenChannel),
                           cell_detection_parameter=cell_detection_parameter,
                           processing_parameter=processing_parameter)

    def filter_cells(self, filt_size=20):

        thresholds = {'source': None, 'size': (filt_size, None)}
        cells.filter_cells(self.ws.filename('cells', postfix='raw_' + self.chosenChannel),
                           self.ws.filename('cells', postfix='filtered_' + self.chosenChannel),
                           thresholds=thresholds)
        return

    """
    ClearMap-Code +
    ProcessCellsCsv +
    embedOntology
    """
    def atlas_assignment(self):
        # sink_maxima = self.ws.filename('cells_', postfix = 'raw_'+self.channel_chosen)
        source = self.ws.filename('stitched_' + self.chosenChannel)
        sink_raw = self.ws.source('cells', postfix='raw_' + self.chosenChannel)

        self.filter_cells()

        # Assignment of the cells with filtered maxima
        # Filtered cell maxima are used to execute the alignment to the atlas
        source = self.ws.source('cells', postfix='filtered_' + self.chosenChannel)

        # Didn't understand the functions so far. Seems like coordinates become transformed by each function and reassigned.
        print("Transfromation\n")

        def transformation(coordinates):
            coordinates = res.resample_points(coordinates,
                                              sink=None,
                                              orientation=None,
                                              source_shape=io.shape(self.ws.filename('stitched_' + self.chosenChannel)),
                                              sink_shape=io.shape(self.ws.filename('resampled_' + self.chosenChannel)))

            coordinates = elx.transform_points(coordinates,
                                               sink=None,
                                               transform_directory=self.myWorkingDirectory + '/elastix_resampled_to_auto_' + self.chosenChannel,
                                               binary=True,
                                               indices=False)

            coordinates = elx.transform_points(coordinates,
                                               sink=None,
                                               transform_directory=self.myWorkingDirectory + '/elastix_auto_to_reference_' + self.chosenChannel,
                                               binary=True,
                                               indices=False)
            return coordinates

        # These are the initial coordinates originating in the file cells_filtered.npy containing the coordinates of the filtered maxima.
        # Each coordinate of 3 dimensional space x,y,z  is written into a new numpy array. [[x1,y1,z1],[x2,y2,3],...,[x_last,y_last,z_last]]
        coordinates = np.array([source[c] for c in 'xyz']).T
        source = self.ws.source('cells', postfix='filtered_' + self.chosenChannel)

        # Coordinates become transformed by the above defined transformation function
        coordinates_transformed = transformation(coordinates)

        # Cell annotation
        # Transformed coordinates are used as input to annotate cells by comparing with brain atlas
        # Due to a future warning occured coordinates_transformed was converterted from array[seq] to arr[tuple(seq)] as coordinates_transformed_tuple
        coordinates_transformed_tuple = np.array(tuple(coordinates_transformed))

        print("Label Point\n")
        label = ano.label_points(coordinates_transformed, key='order')
        print("Convert labeled points\n")
        names = ano.convert_label(label, key='order', value='name')

        # Save results
        coordinates_transformed.dtype = [(t, float) for t in ('xt', 'yt', 'zt')]
        nparray_label = np.array(label, dtype=[('order', int)]);
        nparray_names = np.array(names, dtype=[('name', 'S256')])

        import numpy.lib.recfunctions as rfn
        cells_data = rfn.merge_arrays([source[:], coordinates_transformed,nparray_label, nparray_names],
                                      flatten=True,
                                      usemask=False)

        io.write(self.ws.filename('cells', postfix=self.chosenChannel), cells_data)
        print("Cells data: \n", cells_data)

        # CSV export
        # Pandas was installed via pip, since np.savetxt had
        csv_source = self.ws.source('cells', postfix=self.chosenChannel)

        # Define headers for pandas.Dataframe for csv export
        header = ', '.join([h for h in csv_source.dtype.names])

        # Conversion of cell data into pandas.DataFrame for csv export
        cells_data_df = pd.DataFrame(cells_data, columns=[h for h in csv_source.dtype.names])

        # Getting rid of np_str_ artifacts in df[['name']]
        cells_data_df[['name']] = names

        # export CSV
        print("Exporting Cells to csv\n")
        cells_data_df.to_csv(self.ws.filename('cells', postfix=self.chosenChannel, extension='csv'), sep=';');

        # ClearMap1.0 export
        # Export is not working so far: Error is "the magic string is not correct; expected b'\x93NUMPY, got b';x;y;z
        ClearMap1_source = self.ws.source('cells', postfix=self.chosenChannel)
        Clearmap1_format = {'points': ['x', 'y', 'z'],
                            'intensities': ['source', 'dog', 'background', 'size'],
                            'points_transformed': ['xt', 'yt', 'zt']}

        for filename, names in Clearmap1_format.items():
            sink = self.ws.filename('cells', postfix=[self.chosenChannel, '_', 'ClearMap1', filename])
            data = np.array([ClearMap1_source[name] if name in ClearMap1_source.dtype.names else np.full(ClearMap1_source.shape[0], np.nan) for name in names])
            io.write(sink, data)

        self.processCellsCsv()
        self.embedOntology()
        return

    def voxelization(self):
        annotation_file, reference_file, distance_file = ano.prepare_annotation_files(slicing=(slice(None),
                                                                                               slice(None),
                                                                                               slice(0, 256)),
                                                                                      orientation=(1, -2, 3),
                                                                                      overwrite=False,
                                                                                      verbose=True)
        source = self.ws.source('cells', postfix=self.chosenChannel)
        coordinates = np.array([source[n] for n in ['xt', 'yt', 'zt']]).T
        intensities = source['source']

        # %% Unweighted
        voxelization_parameter = dict(shape=io.shape(annotation_file),
                                      dtype=None,
                                      weights=None,
                                      method='sphere',
                                      radius=(7, 7, 7),
                                      kernel=None,
                                      processes=None,
                                      verbose=True)

        vox.voxelize(coordinates,
                     sink=self.ws.filename('density', postfix='counts_' + self.chosenChannel),
                     **voxelization_parameter)

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

        def choose_sample():
            path = QFileDialog.getExistingDirectory(self, "Choose sample data folder")
            if path != ('', ''):
                ws_path.setText(path)
            else:
                ws_path.setText("")

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

                    string_pos = 0

                    self.rename_box = RenameBox(first_filename, string_pos, i)
                    self.rename_box.show()


                    self.rename_box.reject.clicked.connect(self.rename_box.updateLayout)
                    self.rename_box.reject.clicked.connect(self.rename_box.repaint)


                    self.rename_box.accept.clicked.connect(self.rename_box.perform_cut)
                    self.rename_box.accept.clicked.connect(self.rename_box.close)

                    # Next line is implemented to quit the application in case a renaming is not possible.
                    # self.rename_box.quit_renaming.clicked.connect(lambda: self.rename_box.update(False,4000000))
                    self.rename_box.quitRenaming.clicked.connect(self.rename_box.close)

            else:
                alert = QMessageBox()
                alert.setText("Path does not exist!")
                alert.exec()

        tab = QWidget()
        outer_layout = QVBoxLayout()
        inner_layout = QGridLayout()

        ## Widget for input path
        ws_path = QLineEdit("")
        choose_workspacedir_button = QPushButton("Pick Workspace Directory")

        channel_button = QComboBox()
        channel_button.insertItem(0, "C01")
        channel_button.insertItem(1, "C02")
        set_ws = QPushButton("Set workspace")
        rename_button1 = QPushButton("Rename files in Auto")
        rename_button2 = QPushButton("Rename files in Signal C01")
        rename_button3 = QPushButton("Rename files in Signal C02")
        testdata = QComboBox()
        testdata.insertItem(0, "Border region")
        testdata.insertItem(1, "Background region")
        make_testdata = QPushButton("Make Testdata")
        debug_button = QPushButton("Test Mode")
        debug_button.setCheckable(True)

        ##
        inner_layout.addWidget(QLabel("<b>Set Workspace:</b>"), 0, 0)
        inner_layout.addWidget(QLabel("Input path of interest:"), 1, 0)
        inner_layout.addWidget(ws_path, 1, 1)
        inner_layout.addWidget(choose_workspacedir_button, 1, 2)
        inner_layout.addWidget(channel_button, 1, 3)
        inner_layout.addWidget(set_ws, 1, 4)
        inner_layout.addWidget(rename_button1, 1, 5)
        inner_layout.addWidget(rename_button2, 1, 6)
        inner_layout.addWidget(rename_button3, 1, 7)
        inner_layout.addWidget(QLabel("      "), 2, 0)
        inner_layout.addWidget(QLabel("<b>Testdata option:</b>"), 3, 0)
        inner_layout.addWidget(make_testdata, 4, 0)
        inner_layout.addWidget(testdata, 4, 1)
        inner_layout.addWidget(debug_button, 5, 0, 5, 4)

        choose_workspacedir_button.clicked.connect(lambda: choose_sample())
        set_ws.clicked.connect(lambda: self.initWorkspace(ws_path.text(), channel_button.currentIndex()))
        rename_button1.clicked.connect(lambda: rename_files(_path=self.myWorkingDirectory, extend='/Auto'))
        rename_button2.clicked.connect(lambda: rename_files(_path=self.myWorkingDirectory, extend='/Signal/C01'))
        rename_button3.clicked.connect(lambda: rename_files(_path=self.myWorkingDirectory, extend='/Signal/C02'))
        make_testdata.clicked.connect(lambda: self.createTestdata(index=testdata.currentIndex()))
        debug_button.clicked.connect(self.changeDebug)

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
        source_res_x: QLineEdit = QLineEdit("3.02")
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

        def save_config(save_path):
            if not os.path.exists(save_path):
                print(save_path)
                resample_variable_list = [source_res_x.text(),
                                          source_res_y.text(),
                                          source_res_z.text(),
                                          sink_res_x.text(),
                                          sink_res_y.text(),
                                          sink_res_z.text(),
                                          auto_source_res_x.text(),
                                          auto_source_res_y.text(),
                                          auto_source_res_z.text(),
                                          auto_sink_res_x.text(),
                                          auto_sink_res_y.text(),
                                          auto_sink_res_z.text(),
                                          orientation_x.text(),
                                          orientation_y.text(),
                                          orientation_z.text()]

                pd_df = pd.DataFrame([resample_variable_list],
                                     index=[1],
                                     columns=["Source Resolution x",
                                              "Source Resolution y",
                                              "Source Resolution z",
                                              "Sink Resolution x",
                                              "Sink Resolution y",
                                              "Sink Resolution z",
                                              "Auto Source Resolution x",
                                              "Auto Source Resolution y",
                                              "Auto Source Resolution z",
                                              "Auto Sink Resolution x",
                                              "Auto Sink Resolution y",
                                              "Auto Sink Resolution z",
                                              "Orientation x",
                                              "Orientation y",
                                              "Orientation z"])
                pd_df.to_csv(save_path)
            else:
                alert = QMessageBox()
                alert.setText("File already exists!")
                alert.exec()

        def load_config(load_path):
            if os.path.exists(load_path):
                print(load_path)
                pd_df = pd.read_csv(load_path, header=0)
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

            else:
                alert = QMessageBox()
                alert.setText("Path does not exist!")
                alert.exec()

                ### visualization of Widgets for resampling

        inner_layout.addWidget(QLabel("<b>Resample Paramter: <\b>"), 0, 0)
        inner_layout.addWidget(QLabel("Source Resolution: "), 1, 0)
        inner_layout.addWidget(QLabel("X:"), 1, 1)
        inner_layout.addWidget(source_res_x, 1, 2)
        inner_layout.addWidget(QLabel("Y:"), 1, 3)
        inner_layout.addWidget(source_res_y, 1, 4)
        inner_layout.addWidget(QLabel("Z:"), 1, 5)
        inner_layout.addWidget(source_res_z, 1, 6)

        inner_layout.addWidget(QLabel("Sink Resolution: "), 2, 0)
        inner_layout.addWidget(QLabel("X:"), 2, 1)
        inner_layout.addWidget(sink_res_x, 2, 2)
        inner_layout.addWidget(QLabel("Y:"), 2, 3)
        inner_layout.addWidget(sink_res_y, 2, 4)
        inner_layout.addWidget(QLabel("Z:"), 2, 5)
        inner_layout.addWidget(sink_res_z, 2, 6)

        inner_layout.addWidget(QLabel("     "), 3, 0)
        inner_layout.addWidget(QLabel("<b>Resample to Auto Paramter:</b>"), 4, 0)
        inner_layout.addWidget(QLabel("Source Resolution: "), 5, 0)
        inner_layout.addWidget(QLabel("X:"), 5, 1)
        inner_layout.addWidget(auto_source_res_x, 5, 2)
        inner_layout.addWidget(QLabel("Y:"), 5, 3)
        inner_layout.addWidget(auto_source_res_y, 5, 4)
        inner_layout.addWidget(QLabel("Z:"), 5, 5)
        inner_layout.addWidget(auto_source_res_z, 5, 6)

        inner_layout.addWidget(QLabel("Sink Resolution: "), 6, 0)
        inner_layout.addWidget(QLabel("X:"), 6, 1)
        inner_layout.addWidget(auto_sink_res_x, 6, 2)
        inner_layout.addWidget(QLabel("Y:"), 6, 3)
        inner_layout.addWidget(auto_sink_res_y, 6, 4)
        inner_layout.addWidget(QLabel("Z:"), 6, 5)
        inner_layout.addWidget(auto_sink_res_z, 6, 6)

        inner_layout.addWidget(QLabel("     "), 7, 0)
        inner_layout.addWidget(QLabel("Orientation: "), 8, 0)
        inner_layout.addWidget(QLabel("X:"), 8, 1)
        inner_layout.addWidget(orientation_x, 8, 2)
        inner_layout.addWidget(QLabel("Y:"), 8, 3)
        inner_layout.addWidget(orientation_y, 8, 4)
        inner_layout.addWidget(QLabel("Z:"), 8, 5)
        inner_layout.addWidget(orientation_z, 8, 6)

        inner_layout.addWidget(QLabel("    "), 9, 0)
        inner_layout.addWidget(config_path, 10, 0, 10, 5, alignment=Qt.AlignTop)
        inner_layout.addWidget(load_config_button, 10, 6)
        inner_layout.addWidget(save_config_button, 10, 7)
        inner_layout.addWidget(start_resampling_button, 10, 8)

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
        load_config_button.pressed.connect(lambda: load_config(load_path=os.getcwd() + "/resampling_" + config_path.text() + ".csv"))
        save_config_button.pressed.connect(lambda: save_config(save_path=os.getcwd() + "/resampling_" + config_path.text() + ".csv"))
        start_resampling_button.clicked.connect(lambda: self.initReference(source_res_x=float(source_res_x.text()),
                                                                           source_res_y=float(source_res_y.text()),
                                                                           source_res_z=float(source_res_z.text()),
                                                                           sink_res_x=float(sink_res_x.text()),
                                                                           sink_res_y=float(sink_res_y.text()),
                                                                           sink_res_z=float(sink_res_z.text()),
                                                                           auto_source_res_x=float(auto_source_res_x.text()),
                                                                           auto_source_res_y=float(auto_source_res_y.text()),
                                                                           auto_source_res_z=float(auto_source_res_z.text()),
                                                                           auto_sink_res_x=float(auto_sink_res_x.text()),
                                                                           auto_sink_res_y=float(auto_sink_res_y.text()),
                                                                           auto_sink_res_z=float(auto_sink_res_z.text()),
                                                                           orientation_x=int(orientation_x.text()),
                                                                           orientation_y=int(orientation_y.text()),
                                                                           orientation_z=int(orientation_z.text())))

        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab

    def cd_layout(self):
        tab = QWidget()
        outer_layout = QVBoxLayout()

        # Widgets for illumination correction
        flatfield_illumination = QComboBox()
        flatfield_illumination.insertItem(0, 'None')
        scaling_illumination = QComboBox()
        scaling_illumination.insertItem(0, 'mean')
        scaling_illumination.insertItem(1, 'max')
        save_illumination = QCheckBox()

        # Widgets for background correction
        shape_background_x = QLineEdit("7")
        shape_background_y = QLineEdit("7")
        form_background = QComboBox()
        form_background.insertItem(0, 'Disk')
        form_background.insertItem(1, 'Sphere')
        save_background = QCheckBox()

        # Widgets for equalization
        execute_equalization = QCheckBox()
        percentile_equalization_low = QLineEdit("0.5")
        percentile_equalization_high = QLineEdit("0.95")
        max_value_equalization = QLineEdit("1.5")
        selem_equalization_x = QLineEdit("200")
        selem_equalization_y = QLineEdit("200")
        selem_equalization_z = QLineEdit("5")
        spacing_equalization_x = QLineEdit("50")
        spacing_equalization_y = QLineEdit("50")
        spacing_equalization_z = QLineEdit("5")
        interpolate_equalization = QLineEdit("1")
        save_equalization = QCheckBox()

        # Widgets for DoG filtering
        execute_dog_filter = QCheckBox()
        shape_dog_filter_x = QLineEdit("6")
        shape_dog_filter_y = QLineEdit("6")
        shape_dog_filter_z = QLineEdit("6")
        sigma_dog_filter = QLineEdit("None")
        sigma2_dog_filter = QLineEdit("None")
        save_dog_filter = QCheckBox()

        # Widgets for maxima detection
        hmax_maxima_det = QLineEdit("None")
        shape_maxima_det_x = QLineEdit("6")
        shape_maxima_det_y = QLineEdit("6")
        shape_maxima_det_z = QLineEdit("11")
        threshold_maxima_det = QComboBox()
        threshold_maxima_det.insertItem(0, "None")
        threshold_maxima_det.insertItem(1, "background mean")
        threshold_maxima_det.insertItem(2, "total mean")
        save_maxima_det = QCheckBox()

        # widgets for intensity detection
        measure_intensity_det = QComboBox()
        measure_intensity_det.insertItem(0, "all")
        # measure_intensity_det.insertItem(1,"background")
        method_intensity_det = QComboBox()
        method_intensity_det.insertItem(0, "mean")
        method_intensity_det.insertItem(1, "max")

        # widgets for shape detection
        threshold_shape_det = QLineEdit("200")
        save_shape_det = QCheckBox()

        # widgets for cell detection functions and parameter loading
        detect_cells_button = QPushButton("Detect cells")
        atlas_assignment_button = QPushButton("Atlas assignment")
        voxelization_button = QPushButton("Voxelization")

        config_path = QLineEdit("Insert filename extension")
        load_config_button = QPushButton("Load parameters")
        save_config_button = QPushButton("Save parameters")

        # Widgets for processing paramteres
        amount_processes = QLineEdit('10')
        size_max = QLineEdit('20')
        size_min = QLineEdit('11')
        overlap = QLineEdit('10')

        def save_config(save_path):
            if not os.path.exists(save_path):
                cd_variable_list = [flatfield_illumination.currentIndex(),
                                    scaling_illumination.currentIndex(),
                                    shape_background_x.text(),
                                    shape_background_y.text(),
                                    form_background.currentIndex(),
                                    execute_equalization.isChecked(),
                                    percentile_equalization_low.text(),
                                    percentile_equalization_high.text(),
                                    max_value_equalization.text(),
                                    selem_equalization_x.text(),
                                    selem_equalization_y.text(),
                                    selem_equalization_z.text(),
                                    spacing_equalization_x.text(),
                                    spacing_equalization_y.text(),
                                    spacing_equalization_z.text(),
                                    interpolate_equalization.text(),
                                    execute_dog_filter.isChecked(),
                                    shape_dog_filter_x.text(),
                                    shape_dog_filter_y.text(),
                                    shape_dog_filter_z.text(),
                                    sigma_dog_filter.text(),
                                    sigma2_dog_filter.text(),
                                    hmax_maxima_det.text(),
                                    shape_maxima_det_x.text(),
                                    shape_maxima_det_y.text(),
                                    shape_maxima_det_z.text(),
                                    threshold_maxima_det.currentIndex(),
                                    measure_intensity_det.currentIndex(),
                                    method_intensity_det.currentIndex(),
                                    threshold_shape_det.text(),
                                    amount_processes.text(),
                                    size_max.text(),
                                    size_min.text(),
                                    overlap.text()]
                print(cd_variable_list)
                cd_columns = ["flatfield illumination",
                              "scaling illumination",
                              "shape background x",
                              "shape background y",
                              "form background index",
                              "execute eq",
                              "percentile eq low",
                              "percentile eq high",
                              "max value eq",
                              "selem eq x",
                              "selem eq y",
                              "selem eq z",
                              "spacing eq x",
                              "spacing eq y",
                              "spacing eq z",
                              "interpolate eq",
                              "execute dog",
                              "shape dog x",
                              "shape dog y",
                              "shape dog z",
                              "sigma dog",
                              "sigma2 dog",
                              "hmax maxima",
                              "shape maxima x",
                              "shape maxima y",
                              "shape maxima z",
                              "threshold maxima",
                              "measure intensity",
                              "method intensity det",
                              "threshold shape det",
                              "amount processes",
                              "size max",
                              "size min",
                              "overlap"]

                cd_df = pd.DataFrame([cd_variable_list], columns=cd_columns)
                cd_df.to_csv(save_path)
            else:
                alert = QMessageBox()
                alert.setText("File already exists!")
                alert.exec()

        def load_config(load_path):
            if os.path.exists(load_path):
                cd_df = pd.read_csv(load_path, header=0)
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

                # visualization for all variable features

        inner_layout1 = QGridLayout()
        inner_layout1.addWidget(QLabel("<b>Cell Detection Paramter:</b>"), 0, 0)

        # visualization for illumination correction
        inner_layout1.addWidget(QLabel("<b>Illumination correction: </b>"), 1, 0)
        inner_layout1.addWidget(QLabel("Flatfield: "), 2, 0)
        inner_layout1.addWidget(flatfield_illumination, 2, 1)
        inner_layout1.addWidget(QLabel("Scaling:"), 3, 0)
        inner_layout1.addWidget(scaling_illumination, 3, 1)
        # inner_layout1.addWidget(QLabel("Save: "),4,0)
        # inner_layout1.addWidget(save_illumination,4,1)

        # visualization of background correction
        inner_layout2 = QGridLayout()

        inner_layout2.addWidget(QLabel("<b>Background Correction:</b>"), 1, 0)
        inner_layout2.addWidget(QLabel("Shape:"), 2, 0)
        inner_layout2.addWidget(shape_background_x, 2, 1)
        inner_layout2.addWidget(shape_background_y, 2, 2)
        inner_layout2.addWidget(QLabel("Form:"), 3, 0)
        inner_layout2.addWidget(form_background, 3, 1)
        # inner_layout2.addWidget(QLabel("Save:"),4,0)
        # inner_layout2.addWidget(save_background,4,1)

        # visualization of equalization
        inner_layout3 = QGridLayout()

        inner_layout3.addWidget(QLabel("<b>Equalization:</b>"), 1, 0)
        inner_layout3.addWidget(QLabel("Perform equalization ?:"), 2, 0)
        inner_layout3.addWidget(execute_equalization, 2, 1)
        inner_layout3.addWidget(QLabel("Percentile:"), 3, 0)
        inner_layout3.addWidget(percentile_equalization_low, 3, 1)
        inner_layout3.addWidget(percentile_equalization_high, 3, 2)
        inner_layout3.addWidget(QLabel("Max Value:"), 4, 0)
        inner_layout3.addWidget(max_value_equalization, 4, 1)
        inner_layout3.addWidget(QLabel("Selem:"), 5, 0)
        inner_layout3.addWidget(selem_equalization_x, 5, 1)
        inner_layout3.addWidget(selem_equalization_y, 5, 2)
        inner_layout3.addWidget(selem_equalization_z, 5, 3)
        inner_layout3.addWidget(QLabel("Spacing:"), 6, 0)
        inner_layout3.addWidget(spacing_equalization_x, 6, 1)
        inner_layout3.addWidget(spacing_equalization_y, 6, 2)
        inner_layout3.addWidget(spacing_equalization_z, 6, 3)
        inner_layout3.addWidget(QLabel("Interpolate:"), 7, 0)
        inner_layout3.addWidget(interpolate_equalization, 7, 1)
        # inner_layout3.addWidget(QLabel("Save:"),8,0)
        # inner_layout3.addWidget(save_equalization,8,1)

        # visualization of dog filtering
        inner_layout4 = QGridLayout()

        inner_layout4.addWidget(QLabel("<b>DoG-Filtering:</b>"), 1, 0)
        inner_layout4.addWidget(QLabel("Execute DoG-Filtering?: "), 2, 0)
        inner_layout4.addWidget(execute_dog_filter, 2, 1)
        inner_layout4.addWidget(QLabel("Shape:"), 3, 0)
        inner_layout4.addWidget(shape_dog_filter_x, 3, 1)
        inner_layout4.addWidget(shape_dog_filter_y, 3, 2)
        inner_layout4.addWidget(shape_dog_filter_z, 3, 3)
        inner_layout4.addWidget(QLabel("Sigma:"), 4, 0)
        inner_layout4.addWidget(sigma_dog_filter, 4, 1)
        inner_layout4.addWidget(QLabel("Sigma2:"), 5, 0)
        inner_layout4.addWidget(sigma2_dog_filter, 5, 1)
        # inner_layout4.addWidget(QLabel("Save:"),6,0)
        # inner_layout4.addWidget(save_dog_filter,6,1)

        # visualization of maxima detection
        inner_layout5 = QGridLayout()

        inner_layout5.addWidget(QLabel("<b>Maxima Detection:</b>"), 1, 0)
        inner_layout5.addWidget(QLabel("H max:"), 2, 0)
        inner_layout5.addWidget(hmax_maxima_det, 2, 1)
        inner_layout5.addWidget(QLabel("Shape:"), 3, 0)
        inner_layout5.addWidget(shape_maxima_det_x, 3, 1)
        inner_layout5.addWidget(shape_maxima_det_y, 3, 2)
        inner_layout5.addWidget(shape_maxima_det_z, 3, 3)
        inner_layout5.addWidget(QLabel("Threshold:"), 4, 0)
        inner_layout5.addWidget(threshold_maxima_det, 4, 1)
        # inner_layout5.addWidget(QLabel("Save:"),5,0)
        # inner_layout5.addWidget(save_maxima_det,5,1)

        # visualization of intensity detection
        inner_layout6 = QGridLayout()

        inner_layout6.addWidget(QLabel("<b>Intensity Detection:</b>"), 1, 0)
        inner_layout6.addWidget(QLabel("Type of measure:"), 2, 0)
        inner_layout6.addWidget(measure_intensity_det, 2, 1)
        inner_layout6.addWidget(QLabel("Method of measure:"), 3, 0)
        inner_layout6.addWidget(method_intensity_det, 3, 1)

        # visualization of shape detection
        inner_layout7 = QGridLayout()

        inner_layout7.addWidget(QLabel("<b>Shape detection:</b>"), 0, 0)
        inner_layout7.addWidget(QLabel("Threshold:"), 1, 0)
        inner_layout7.addWidget(threshold_shape_det, 1, 1)
        # inner_layout7.addWidget(QLabel("Save:"),2,0)
        # inner_layout7.addWidget(save_shape_det,2,1)

        # visualization of Processing parameter widgets

        inner_layout8 = QGridLayout()

        inner_layout8.addWidget(QLabel("<b>Processing paramters:</b>"), 0, 0)
        inner_layout8.addWidget(QLabel("No. of parallel processes:"), 1, 0)
        inner_layout8.addWidget(amount_processes, 1, 1)
        inner_layout8.addWidget(QLabel("Size max:"), 1, 2)
        inner_layout8.addWidget(size_max, 1, 3)
        inner_layout8.addWidget(QLabel("Size min:"), 1, 4)
        inner_layout8.addWidget(size_min, 1, 4)
        inner_layout8.addWidget(QLabel("Overlap:"), 1, 5)
        inner_layout8.addWidget(overlap, 1, 6)

        # visualization of loading,saving and detection functions
        inner_layout9 = QHBoxLayout()

        inner_layout9.addWidget(config_path)
        inner_layout9.addWidget(load_config_button)
        inner_layout9.addWidget(save_config_button)
        inner_layout9.addWidget(detect_cells_button)
        inner_layout9.addWidget(atlas_assignment_button)
        inner_layout9.addWidget(voxelization_button)

        # Connection of signals and slots for cell detection

        load_config_button.clicked.connect(
            lambda: load_config(load_path=os.getcwd() + "/cell_detection_" + config_path.text() + ".csv"))
        save_config_button.clicked.connect(
            lambda: save_config(save_path=os.getcwd() + "/cell_detection_" + config_path.text() + ".csv"))

        detect_cells_button.clicked.connect(
            lambda: self.cell_detection(flatfield_illumination=flatfield_illumination.currentIndex(),
                                        scaling_illumination=scaling_illumination.currentIndex(),
                                        shape_background_x=shape_background_x.text(),
                                        shape_background_y=shape_background_y.text(),
                                        form_background=form_background.currentIndex(),
                                        execute_equalization=execute_equalization.isChecked(),
                                        percentile_equalization_low=percentile_equalization_low.text(),
                                        percentile_equalization_high=percentile_equalization_high.text(),
                                        max_value_equalization=max_value_equalization.text(),
                                        selem_equalization_x=selem_equalization_x.text(),
                                        selem_equalization_y=selem_equalization_y.text(),
                                        selem_equalization_z=selem_equalization_z.text(),
                                        spacing_equalization_x=spacing_equalization_x.text(),
                                        spacing_equalization_y=spacing_equalization_y.text(),
                                        spacing_equalization_z=spacing_equalization_z.text(),
                                        interpolate_equalization=interpolate_equalization.text(),
                                        execute_dog_filter=execute_dog_filter.isChecked(),
                                        shape_dog_filter_x=shape_dog_filter_x.text(),
                                        shape_dog_filter_y=shape_dog_filter_y.text(),
                                        shape_dog_filter_z=shape_dog_filter_z.text(),
                                        sigma_dog_filter=sigma_dog_filter.text(),
                                        sigma2_dog_filter=sigma2_dog_filter.text(),
                                        hmax_maxima_det=hmax_maxima_det.text(),
                                        shape_maxima_det_x=shape_maxima_det_x.text(),
                                        shape_maxima_det_y=shape_maxima_det_y.text(),
                                        shape_maxima_det_z=shape_maxima_det_z.text(),
                                        threshold_maxima_det=threshold_maxima_det.currentIndex(),
                                        measure_intensity_det=measure_intensity_det.currentIndex(),
                                        method_intensity_det=method_intensity_det.currentIndex(),
                                        threshold_shape_det=threshold_shape_det.text(),
                                        amount_processes=int(amount_processes.text()),
                                        size_maximum=int(size_max.text()), size_minimum=int(size_min.text()),
                                        area_of_overlap=int(overlap.text())))

        atlas_assignment_button.clicked.connect(lambda: self.atlas_assignment())
        voxelization_button.clicked.connect(lambda: self.voxelization())

        # inner_layout.addWidget(QPushButton("Second"))
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
        
        inner_layout2.addWidget(QFrame())
        inner_layout2.addWidget(QLabel("<b>Log Transformation</b>"))
        
        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(QLabel("Normalization"))
        inner_layout2.addWidget(choose_normalization_ComboBox)

        
        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(QLabel("Choose log transformation or None"))
        inner_layout2.addWidget(choose_log_transformation_ComboBox)
        

        
        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(QLabel("Filter for level in hierarchical structure"))
        inner_layout2.addWidget(filter_level_ComboBox)



        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(QLabel("                                          "))
        inner_layout2.addWidget(QLabel("Filter for a region and it's subregions"))
        inner_layout2.addWidget(filter_region_LineEdit)


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

                if filter_level_ComboBox.currentText() != "None":
                    level = int(filter_level_ComboBox.currentText())
                    information = pd.read_csv(final_output_directory.text() + "/list_information.csv", sep = ";",index_col = 0)
                    index_list = []
                    for i,val in enumerate(information["CorrespondingLevel"]):
                        array = eval(val)
                        if level == array[0]:
                            index_list.append(i)

                    df_abs = df_abs.iloc[index_list,:]
                    df_hier_abs = df_hier_abs.iloc[index_list,:]

                    df_abs_filename = "level_" + str(level) + "_" + df_abs_filename
                    df_hier_abs_filename = "level_" + str(level) + "_" + df_hier_abs_filename

                if filter_region_LineEdit.text() != "":
                    region = filter_region_LineEdit.text()
                    information = pd.read_csv(final_output_directory.text() + "/list_information.csv", sep = ";",index_col = 0)
                    if region in information["TrackedWay"]:
                        index_list = []
                        for i,val in enumerate(information["TrackedWay"]):
                            if region in val:
                                index_list.append(i)  


                        df_abs = df_abs.iloc[index_list,:]
                        df_hier_abs = df_hier_abs.iloc[index_list,:]

                        df_abs_filename = "region_" + str(region) + "_" + df_abs_filename
                        df_hier_abs_filename = "level_" + str(region) + "_" + df_hier_abs_filename
                    else:
                        alert = QMessageBox()
                        alert.setText("Region does not exist in ontology file! Please check if Region is written in the correct way!")
                        alert.exec()
                        return


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
        create_vol_plot = QPushButton("Volcano Plot")
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

        inner_layout3.addWidget(QLabel("<b>Volcano Plot</b>"))
        inner_layout3.addWidget(create_vol_plot)
        inner_layout3.addStretch()

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
            
            




        def volcano():
            pass

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
            pass 
        
        


 
        return tab
               

        """
        def createHeatmap(path2file: str):
            dataframe = pd.read_csv(path2file, header=0, sep=";")
            dataframe = dataframe.iloc[:, 1:]
            if not os.path.exists(result_dir.text() + "/AnalysisOutput"):
                os.makedirs(result_dir.text() + "/AnalysisOutput")

            if not result_dir.text():
                alert = QMessageBox()
                alert.setText("Please load a existing directory!")
                alert.exec()
                return

            if brainregion.text():
                print("Filtering Region")
                dataframe = filterDatasetByRegion(dataframe, brainregion.text())

            if dataframe.empty:
                alert = QMessageBox()
                alert.setText("After filtering the region the dataframe it is empty! - Try other filters")
                alert.exec()
                return

            if struc_level.text():
                print("Filtering Level")
                dataframe = filterDatasetByLevel(dataframe, int(struc_level.text()))

            if dataframe.empty:
                alert = QMessageBox()
                alert.setText("After filtering the level the dataframe it is empty! - Try other filters")
                alert.exec()
                return

            regions = dataframe["Region"].to_numpy()

            if CountsOrSummedCounts.currentText() == "Raw_Counts":
                startindex = 3
                endindex = 3 + int((dataframe.shape[1] - 3) / 2)

            elif CountsOrSummedCounts.currentText() == "Summed_Counts":
                startindex = 3 + int((dataframe.shape[1] - 3) / 2)
                endindex = dataframe.shape[1]

            sns.heatmap(dataframe.iloc[:, startindex:endindex], yticklabels=regions, annot=False)
            plt.title(brainregion.text())
            plt.savefig(result_dir.text() + "/AnalysisOutput/"+brainregion.text()+"_"+CountsOrSummedCounts.currentText()+"_Lv"+struc_level.text()+".png", bbox_inches='tight')
            plt.clf()
            print("FERTIG!")

        def createHeatmapZScores(path2file: str):
            df = pd.read_csv(path2file, header=0, sep=";")
            df = df.iloc[:, 1:]
            if not os.path.exists(result_dir.text() + "/AnalysisOutput"):
                os.makedirs(result_dir.text() + "/AnalysisOutput")

            if not result_dir.text():
                alert = QMessageBox()
                alert.setText("Please load a existing directory!")
                alert.exec()
                return

            if not struc_level.text() and not brainregion.text():
                alert = QMessageBox()
                alert.setText("No filter was entered, are you sure to continue without a filter?")  : Make Yes/No Dialog
                alert.exec()

            if brainregion.text():
                print("Filtering Region")
                df = filterDatasetByRegion(df, brainregion.text())

            if df.empty:
                alert = QMessageBox()
                alert.setText("After filtering the region the dataframe it is empty! - Try other filters")
                alert.exec()
                return

            if struc_level.text():
                print("Filtering Level")
                df = filterDatasetByLevel(df, int(struc_level.text()))

            if df.empty:
                alert = QMessageBox()
                alert.setText("After filtering the level the dataframe it is empty! - Try other filters")
                alert.exec()
                return

            regions = df["Region"].to_numpy()

            if CountsOrSummedCounts.currentText() == "Raw_Counts":
                startindex = 3
                endindex = 3 + int((df.shape[1] - 3) / 2)

            elif CountsOrSummedCounts.currentText() == "Summed_Counts":
                startindex = 3 + int((df.shape[1] - 3) / 2)
                endindex = df.shape[1]

            mean = pd.DataFrame(df.iloc[:, startindex:endindex].mean(axis=1))
            stdd = pd.DataFrame(df.iloc[:, startindex:endindex].std(axis=1))
            
            print(mean)
            print(stdd)

            df = df.iloc[:,startindex:endindex]

            cols = list(df.columns)
            index = len(cols)
            print(cols)
            for col in cols[0:index]:
                print(col)
                col_zscore = col + "_ZScore"
                heatmapdata_zscore = []
                for i in range(len(df[col])):
                    zscore_temp = (df[col].iloc[i] - mean.iloc[i, 0]) / stdd.iloc[i, 0]
                    heatmapdata_zscore.append(zscore_temp)
                df[col_zscore] = heatmapdata_zscore

            # df.to_csv(result_dir.text() + "/AnalysisOutput" + "/Test.csv")

            #if CountsOrSummedCounts.currentText() == "Raw_Counts":
            #    startindex = int((df.shape[1]) / 2)
            #    endindex = startindex + int((df.shape[1]) / 4)

            #elif CountsOrSummedCounts.currentText() == "Summed_Counts":
            #    startindex = int((df.shape[1]) / 2) + int((df.shape[1]) / 4)
            #    endindex = df.shape[1]
            startindex =int((df.shape[1]) / 2)
            endindex = df.shape[1]

            sns.heatmap(df.iloc[:, startindex:endindex], yticklabels=regions, annot=False)
            plt.title(brainregion.text())
            plt.savefig(result_dir.text() + "/AnalysisOutput/"+brainregion.text()+"_ZScore_"+CountsOrSummedCounts.currentText()+"_Lv"+struc_level.text()+".png", bbox_inches='tight')
            plt.clf()

            return

        def createBoxplot(path2file: str):
            dataframe = pd.read_csv(path2file, header=0, sep=";")
            dataframe = dataframe.iloc[:, 1:]

            if CountsOrSummedCounts.currentText() == "Raw_Counts":
                startindex = 3
                endindex = 3 + int((dataframe.shape[1] - 3) / 2)

            elif CountsOrSummedCounts.currentText() == "Summed_Counts":
                startindex = 3 + int((dataframe.shape[1] - 3) / 2)
                endindex = dataframe.shape[1]

            sample_names = list(dataframe.iloc[:, startindex:endindex].columns)
            metadata_list = pd.read_csv(result_dir.text()+"/metadata.csv", header=0, sep=";") : Metadata
            for i in sample_names:
                cpm_name = i + "_processed"
                dataframe[cpm_name] = dataframe[i]

            conditions = metadata_list["condition"].unique()

            for i in conditions:
                array_of_means = []
                array_of_stdd = []
                array_of_medians = []
                array_of_single_values = []
                metadata_list_tmp = metadata_list[metadata_list["condition"] == i]
                for j in range(len(dataframe)):
                    array_of_cpms = []
                    array_of_condition_samples = []
                    for k in range(len(dataframe.iloc[0, :])):
                        print(dataframe.columns[k])
                        print(list([str(i) + "_processed" for i in list(metadata_list_tmp["sample"])]))
                        if dataframe.columns[k] in list(
                                [str(i) + "_processed" for i in list(metadata_list_tmp["sample"])]):
                            array_of_cpms.append(dataframe.iloc[j, k])
                            array_of_condition_samples.append(dataframe.columns[k])
                    mean = np.mean(array_of_cpms)
                    stdd = np.std(array_of_cpms)
                    med = np.median(array_of_cpms)
                    array_of_means.append(mean)
                    array_of_stdd.append(stdd)
                    array_of_medians.append(med)
                    array_of_single_values.append(array_of_cpms)
                dataframe[str(i) + "_mean"] = array_of_means
                dataframe[str(i) + "_stdd"] = array_of_stdd
                dataframe[str(i) + "_med"] = array_of_medians
                dataframe[str(i) + "_single_values"] = array_of_single_values
            # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
            #    print(dataframe)

            desired_region = brainregion.text()
            chosen_data = dataframe[dataframe["Region"] == desired_region]

            array_for_boxplots = []

            for i in conditions:
                spread = list(chosen_data[str(i) + "_single_values"])

                data = np.concatenate(spread)
                array_for_boxplots.append(data)

            df_boxplot = pd.DataFrame()
            for val, i in enumerate(conditions):
                method = "absolute"
                region_name = brainregion.text()
                df_tmp = pd.DataFrame({method: array_for_boxplots[val]})
                df_tmp["condition"] = i
                df_boxplot = pd.concat([df_boxplot, df_tmp])
                fig, ax = plt.subplots()
                ax = sns.boxplot(x="condition", y=method, data=df_boxplot)
                ax = sns.swarmplot(x="condition", y=method, data=df_boxplot, color=".25")
                region_name = str(region_name).replace(" ", "")
                region_name = str(region_name).replace("/", "")
                plt.title(brainregion.text())
            plt.savefig(result_dir.text() + "/AnalysisOutput/"+brainregion.text()+"_BoxPlot_"+CountsOrSummedCounts.currentText()+"_Lv"+struc_level.text()+".png", bbox_inches='tight')


        def createVolcanoPlot(path2file: str):
            dataframe = pd.read_csv(path2file, header=0, sep=";")
            dataframe = dataframe.iloc[:, 1:]
            index = 3 + ((dataframe.shape[1] - 3) / 2)
            sample_names = list(dataframe.iloc[:, 3:int(index)].columns)
            print(sample_names)
            metadata_list = pd.read_csv(result_dir.text()+"/metadata.csv", header=0, sep=";")

            analysis_folders = getFilenames(result_dir.text())
            doi = pd.read_csv(analysis_folders[0], header=0, sep=";")

            dataframe = dataframe.dropna()
            for i in sample_names:
                cpm_name = i + "_cpm"

                divisor = float(dataframe.loc[dataframe["Region"] == "root", i])
                dataframe[cpm_name] = (dataframe[i] / divisor) * 1000000

            conditions = metadata_list["condition"].unique()

            for i in conditions:
                array_of_means = []
                metadata_list_tmp = metadata_list[metadata_list["condition"] == i]
                for j in range(len(dataframe)):
                    sum = 0
                    number_of_samples = 0
                    for k in range(len(dataframe.iloc[0, :])):
                        if dataframe.columns[k] in list([str(i) + "_cpm" for i in list(metadata_list_tmp["sample"])]):
                            sum = sum + float(dataframe.iloc[j, k])
                            number_of_samples = number_of_samples + 1
                    mean = sum / number_of_samples
                    array_of_means.append(mean)
                dataframe[i] = array_of_means

            dataframe["Change"] = dataframe[conditions[1]] / dataframe[conditions[0]]
            dataframe = dataframe[dataframe[conditions[0]] > 0]
            dataframe = dataframe[dataframe[conditions[1]] > 0]
            dataframe = dataframe.sort_values(by="Change", ascending=False)

            mean_change = dataframe["Change"].mean()
            stdd_change = dataframe["Change"].std()

            dataframe["Change_z_score"] = (dataframe["Change"] - mean_change) / stdd_change
            z_score = np.array(dataframe["Change_z_score"])
            p_values = scipy.stats.norm.sf(abs(z_score))
            dataframe["Change_pvalue"] = p_values
            dataframe["Change_pvalue_significant"] = dataframe["Change_pvalue"] < 0.05

            dataframe = dataframe.sort_values(by="Change_pvalue")
            print(dataframe)

            if filter != "":
                contains_substring_list = []
                for i in list(dataframe["Region"]):
                    is_in = False
                    for j in doi:
                        if i == j:
                            is_in = True
                            break
                    if is_in:
                        contains_substring_list.append(True)
                    else:
                        contains_substring_list.append(False)
                dataframe = dataframe.loc[contains_substring_list, :]
                print("Length new df after filter:\n", len(dataframe))

            marking_array = []
            for val, i in enumerate(list(dataframe["Change"])):
                if val < 4:
                    marking_array.append(True)
                else:
                    marking_array.append(False)

            dataframe["to_label"] = marking_array

            fig, ax = plt.subplots()
            ax.scatter(np.log2(dataframe["Change"]), -np.log10(dataframe["Change_pvalue"]),
                       c=dataframe["Change_pvalue_significant"],
                       cmap="jet")

            x = list(np.log2(dataframe["Change"]))
            y = list(-np.log10(dataframe["Change_pvalue"]))

            regions = []
            for val, j in enumerate(list(dataframe["Region"])):
                if list(dataframe["to_label"])[val]:
                    regions.append(j)
                    # print(j)
                else:
                    regions.append("")

            for i, txt in enumerate(regions):
                ax.annotate(txt, (x[i], y[i]), ha="center", va="bottom", size="6")

            plt.xlim((-3, 3))
            plt.title() 
            plt.show()

            return
            """

        


if __name__ == "__main__":
    app = QApplication([])
    main_window = Main_Window()
    main_window.show()
    app.exec()

