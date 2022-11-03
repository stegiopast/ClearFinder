import utils

## Contains all features of the grouping and normalization tab

def create_tracking_list(dataframe: utils.pd.DataFrame) -> utils.pd.DataFrame:
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

    df = utils.np.array([trackedlevels, correspondingLevel], dtype=object)
    df = utils.np.transpose(df)
    df = utils.pd.DataFrame(data=df,
                        columns=["TrackedWay",
                                "CorrespondingLevel"])
    return df

"""
Input: pd.Dataframe (mouse_ontology.csv) , trackedList (pd.Dataframe from create_tracking_list), and the length of the pd.Dataframe
Creates a Template-Resultframe, which can be used for every sample
Cols: Region, trackedWay, CorrespondingLevel, RegionCellCount, RegionCellCountSummedUp
"""
def create_result_frame(df, trackedList):
    resultframe = utils.np.array([list(df["name"]),  # Takes all important Brain Regions in first Col
                            trackedList["TrackedWay"],
                            trackedList["CorrespondingLevel"],
                            [0 for x in range(trackedList.shape[0])],  # Sets the count of each Brain Region to 0
                            [0 for x in range(trackedList.shape[0])]])  # Creates a column for normalized Values
    resultframe = utils.np.transpose(resultframe)
    resultframe = utils.pd.DataFrame(data=resultframe,
                                columns=["Region",
                                        "TrackedWay",
                                        "CorrespondingLevel",
                                        "RegionCellCount",
                                        "RegionCellCountSummedUp"])

    resultframe["RegionCellCount"] = utils.pd.to_numeric(resultframe["RegionCellCount"])
    resultframe["RegionCellCountSummedUp"] = utils.pd.to_numeric(resultframe["RegionCellCountSummedUp"])

    return resultframe

"""
df = summarized_counts
reference = mouse_ontology.csv as pd.Dataframe
trackedLevels = pd.Dataframe of the tracked regions and corresponding Levels

Output: The Template-Resultframe from (create_result_frame) but filled with values of the cellcount of each region
"""
def analyse_csv(df: utils.pd.DataFrame,reference_df: utils.pd.DataFrame, trackedLevels: list, choice: str, my_working_directory: str) -> utils.pd.DataFrame:
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
    resultframe = create_result_frame(reference_df, trackedLevels)

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
            samplename = utils.os.path.basename(my_working_directory)
            filename = my_working_directory + "/" + samplename + "_unmapped_regions.csv"

            with open(filename, "a+") as KeyError_file:
                KeyError_file.write(str(name) + ";" + str(df.iloc[i][total_cells]) + "\n")
            utils.continuetraining_layout

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
def process_cells_csv(my_working_directory):
    df_filename = "/analysis/summary.csv"
    df_name = my_working_directory + df_filename
    df = utils.pd.read_csv(df_name, header=0)
    df_final_filename = "/analysis/cells_final.csv"
    df_final_name = my_working_directory + df_final_filename
    df_final = df[df["structure_name"] != "universe"]
    df_final = df_final[df_final["structure_name"] != "No label"]
    df_final.to_csv(df_final_name, sep=";")
    #Counts abundancy in different brain regions
    df_final = utils.pd.DataFrame(df_final)
    #Writes a final csv with single cell counts
    df_final.to_csv(my_working_directory + "/analysis/cells_summarized_counts.csv", sep=";")

"""
calls the analyse_csv Function to actually create the embedded_ontology.csv which is needed from each sample for the analysis
"""
def embeded_ontology(choice, my_working_directory):
    # Reads ontology file holding the reference region dictionairy
    reference_df = utils.pd.read_csv(str(utils.os.path.dirname(utils.os.path.realpath(utils.sys.argv[0]))) + "/ontology_mouse.csv",
                            # Current Refernce Dataframe for mapping
                            # File which stores all important Brain Regions (Atlas?)
                            sep=";",  # Separator
                            header=0,  # Header
                            index_col=0)  # Index Col

    #Creates a mask table with all regions abundant in the ontology file for comparibility
    # Additionally allt the structural abundancies between regions of different hierarchy become recorded in form of id- and structurename arrays
    trackedLevels = create_tracking_list(reference_df)

    #Reads the cell detection csv on a single cell basis (coordinates, transformed coordinates and regionname)
    df = utils.pd.read_csv(my_working_directory + "/analysis/cells_summarized_counts.csv", header=0, sep=";")

    samplename = utils.os.path.basename(my_working_directory)
    new_df = analyse_csv(df,reference_df, trackedLevels, choice, my_working_directory)
    new_df_name = my_working_directory + "/" + samplename + "_embedded_ontology.csv"
    new_df.to_csv(new_df_name, sep=";", index=0)
    return

def assignment(choice, wd):
    process_cells_csv(wd)
    embeded_ontology(choice,wd)
    return

class CellDetection:
    def detect_cells(self,_number_of_free_cpus=4,
                          _n_sds_above_mean_thresh=10,
                          _trained_model="",
                          _soma_diameter=16,
                          _xy_cell_size=6,
                          _z_cell_size=6,
                          _gaussian_filter=0.2,
                          _orientation = "asl",
                          _batch_size = 256,):

        ##Basic comman for cellfinder
        if self.my_working_directory != "":
            basic_string = "cellfinder "
            if self.channel_chosen != "":
                filepath = self.my_working_directory + "/Signal/" + str(self.channel_chosen)
            else:
                filepath = self.my_working_directory + "/Signal"

            if utils.os.path.exists(self.my_working_directory +"/" + self.channel_chosen + "_voxel_size_signal"):

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
                    if utils.os.path.exists(_trained_model):
                        trained_model_string = "--trained-model " + _trained_model + " "
                    else:
                        trained_model_string = ""
                        alert = utils.QMessageBox()
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
                utils.os.system(final_string)
            else:
                alert = utils.QMessageBox()
                alert.setText("Please perform Preprocessing first!")
                alert.exec()
        else:
            self.warning_ws()

class CellDetectionLayout:
    def cd_layout(self):
        """Celldetection Layout"""
        tab = utils.QWidget()
        outer_layout = utils.QVBoxLayout()
        inner_layout = utils.QGridLayout()

        ### Widgets for technical Technical Settings
        n_cpus = utils.QLineEdit("4")

        ### Widgets for Parameters
        n_sds_above_mean = utils.QLineEdit("10")
        soma_diameter = utils.QLineEdit("16")
        xy_cell_size = utils.QLineEdit("6")
        z_cell_size = utils.QLineEdit("6")
        gaussian_filter = utils.QLineEdit("0.2")

        ### Widget for trained model
        path = ""
        trained_model = utils.QLabel()
        choose_model_button = utils.QPushButton("Choose model")

        def choose_model():
            """Selecting a training model"""
            path = utils.QFileDialog.getOpenFileName(self, "Choose a Model file (.h5)")
            if path != ('', ''):
                trained_model.setText(str(path[0]))
            else:
                trained_model.setText('')

        ### Widget for orientation
        orientation = utils.QLineEdit("asl")

        ## Widget for starting cell detection
        start_CellDetection_button = utils.QPushButton("Start Cell Detection")

        ## Widget for saving | loading settings
        config_path = utils.QLineEdit("Insert filename extension")
        load_config_button = utils.QPushButton("Load parameters")
        save_config_button = utils.QPushButton("Safe parameters")

        ## Widget for embedding summary.csv in hierarchical dataframe
        choose_structure = utils.QComboBox()
        choose_structure.insertItem(0, "Whole brain")
        choose_structure.insertItem(1, "Left hemisphere")
        choose_structure.insertItem(0, "Right hemisphere")

        assignment_button = utils.QPushButton("Embed Ontology")

        ### Visualization of Widgets for cell detection tab on GUI
        inner_layout.addWidget(utils.QLabel("Number of cpus available:"),1,0)
        inner_layout.addWidget(n_cpus,1,1)
        inner_layout.addWidget(utils.QLabel(" "),2,0)
        inner_layout.addWidget(utils.QLabel("Lower Boundary measured in number of standarddeviations above mean illumination:"),3,0)
        inner_layout.addWidget(n_sds_above_mean,3,1)
        inner_layout.addWidget(utils.QLabel("Mean soma diamter:"),4,0)
        inner_layout.addWidget(soma_diameter,4,1)
        inner_layout.addWidget(utils.QLabel("Mean cell size in xy plane:"),5,0)
        inner_layout.addWidget(xy_cell_size,5,1)
        inner_layout.addWidget(utils.QLabel("Mean cell size in z plane:"),6,0)
        inner_layout.addWidget(z_cell_size,6,1)
        inner_layout.addWidget(utils.QLabel("Gaussian Filter:"),7,0)
        inner_layout.addWidget(gaussian_filter,7,1)
        inner_layout.addWidget(utils.QLabel("Custom pretrained model:"),8,0)
        inner_layout.addWidget(trained_model,8,1)
        inner_layout.addWidget(choose_model_button,8,2)
        inner_layout.addWidget(utils.QLabel("Choose brain orientation (anterior/posterior,superior/inferior,left/right)"),9,0)
        inner_layout.addWidget(orientation,9,1)

        inner_layout.addWidget(config_path,10,0)
        inner_layout.addWidget(load_config_button,10,1)
        inner_layout.addWidget(save_config_button,10,2)
        inner_layout.addWidget(start_CellDetection_button,10,3)

        inner_layout.addWidget(choose_structure,11,0)
        inner_layout.addWidget(assignment_button,11,1)

        def save_config(save_path):
            if not utils.os.path.exists(save_path):
                print(save_path)
                resample_variable_list = [n_cpus.text(),
                                          n_sds_above_mean.text(),
                                          soma_diameter.text(),
                                          xy_cell_size.text(),
                                          z_cell_size.text(),
                                          gaussian_filter.text(),
                                          trained_model.text(),
                                          orientation.text()]

                pd_df = utils.pd.DataFrame([resample_variable_list],
                                     index = [1],
                                     columns = ["Number of CPUs", "Number SDS above mean",
                                                "Soma Diameter", "XY Plane Cell Size",
                                                "Z Plane Cell Size","Gaussian Filter",
                                                "Trained Model","Orientation"])
                pd_df.to_csv(save_path)
            else:
                alert = utils.QMessageBox()
                alert.setText("File already exists!")
                alert.exec()

        def load_config(load_path):
            if utils.os.path.exists(load_path):
                print(load_path)
                pd_df = utils.pd.read_csv(load_path, header = 0)
                n_cpus.setText(str(pd_df["Number of CPUs"][0]))
                n_sds_above_mean.setText(str(pd_df["Number SDS above mean"][0]))
                soma_diameter.setText(str(pd_df["Soma Diameter"][0]))
                xy_cell_size.setText(str(pd_df["XY Plane Cell Size"][0]))
                z_cell_size.setText(str(pd_df["Z Plane Cell Size"][0]))
                gaussian_filter.setText(str(pd_df["Gaussian Filter"][0]))
                trained_model.setText(str(pd_df["Trained Model"][0]))
                orientation.setText(str(pd_df["Orientation"][0]))
            else:
                alert = utils.QMessageBox()
                alert.setText("Path does not exist!")
                alert.exec()

       ### Connection of Widgets with CellDetection functions
        load_config_button.pressed.connect(lambda: load_config(load_path = utils.os.getcwd() + "/CellDetection_" + config_path.text() + ".csv"))
        save_config_button.pressed.connect(lambda: save_config(save_path = utils.os.getcwd() + "/CellDetection_" + config_path.text() + ".csv"))

        start_CellDetection_button.clicked.connect(lambda: self.detect_cells(_number_of_free_cpus=int(n_cpus.text()),
                                                                              _n_sds_above_mean_thresh=int(n_sds_above_mean.text()),
                                                                              _trained_model=str(trained_model.text()),
                                                                              _soma_diameter=int(soma_diameter.text()),
                                                                              _xy_cell_size=int(xy_cell_size.text()),
                                                                              _z_cell_size=int(z_cell_size.text()),
                                                                              _gaussian_filter=float(gaussian_filter.text()),
                                                                              _orientation = str(orientation.text())))

        choose_model_button.clicked.connect(lambda: choose_model())
        assignment_button.clicked.connect(lambda: assignment(choice=str(choose_structure.currentText()),wd=self.my_working_directory))

        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab
