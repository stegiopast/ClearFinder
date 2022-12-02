import utils


def create_tracking_list(dataframe: utils.pd.DataFrame) -> utils.pd.DataFrame:
    reference_df_id = dataframe.set_index(dataframe["id"])
    reference_df_name = dataframe.set_index(dataframe["name"])

    trackedlevels = [[] for x in range(dataframe.shape[0])]
    corresponding_level = [[] for x in range(dataframe.shape[0])]

    for i in range(len(dataframe)):
        name = dataframe.iloc[i, 4]  # iterate over all rows of "names'
        df_temp = reference_df_name.loc[name]
        temp_name = df_temp["name"]

        trackedlevels[i].append(temp_name)
        corresponding_level[i].append(int(df_temp["st_level"]))
        if not df_temp.empty:
            while int(df_temp["st_level"]) >= 0:
                if int(df_temp["st_level"]) == 0:
                    break
                df_temp = reference_df_id.loc[int(df_temp["parent_structure_id"])]
                temp_name = df_temp["name"]
                trackedlevels[i].append(temp_name)
                corresponding_level[i].append(int(df_temp["st_level"]))

    df = utils.np.array([trackedlevels, corresponding_level], dtype=object)

    df = utils.np.transpose(df)

    df = utils.pd.DataFrame(data=df,
                      columns=["TrackedWay",
                               "CorrespondingLevel"])
    return df

"""
#Input: pd.Dataframe (mouse_ontology.csv) , tracked_list (pd.Dataframe from create_tracking_list), and the length of the pd.Dataframe
#Creates a Template-Resultframe, which can be used for every sample
#Cols: Region, trackedWay, CorrespondingLevel, RegionCellCount, RegionCellCountSummedUp
"""
def create_resultframe(df, tracked_list):
    resultframe = utils.np.array([list(df["name"]),  # Takes all important Brain Regions in first Col
                            tracked_list["TrackedWay"],
                            tracked_list["CorrespondingLevel"],
                            [0 for x in range(tracked_list.shape[0])],  # Sets the count of each Brain Region to 0
                            [0 for x in range(tracked_list.shape[0])]])  # Creates a column for normalized Values
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
#df = summarized_counts
#reference = mouse_ontology.csv as pd.Dataframe
#tracked_levels = pd.Dataframe of the tracked regions and corresponding Levels

#Output: The Template-Resultframe from (create_resultframe) but filled with values of the cellcount of each region
"""
def analyse_csv(df: utils.pd.DataFrame,reference_df: utils.pd.DataFrame, tracked_levels: list, my_working_directory: str) -> utils.pd.DataFrame:
    total_cellcount = int(df["total_cells"].sum())  # get total cellcount for reference
    df["name"] = df["structure_name"]

    #Reference_df_ID becomes copied twice to allow O(1) access to "id" or "name" as index of reference_frame
    reference_df_id = reference_df.set_index(reference_df["id"])
    reference_df_name = reference_df.set_index(reference_df["name"])

    #Creation of a template resultframe including all regions and a fusion of ontology_csv and tracked_levels mask,
    # all entries in RegionCellCount and RegionCellCountSummedUp are initialized as 0
    resultframe = create_resultframe(reference_df, tracked_levels)

    # Loop Iterates over all entries in summary.csv and tries to embed them into resultframe
    # For each entry in summary.csv the parent_id will iteratively indentify the parent structure of this entry
    # and sum these entries up, until the root is reached. In that way the cellcounts become summarized over all brain regions in different hierarchies
    for i in range(len(df.iloc[:, 0])):
        name = df.iloc[i]["name"]  # get the Name of the Region at current index
        print(name)

        # Structures like "No label" and "universe" are not part of ontology.csv and therefore will be removed with this try nd except function
        try:
            df_temp = reference_df_name.loc[name]
        except KeyError:
            samplename = utils.os.path.basename(my_working_directory)
            filename = my_working_directory + "/" + samplename + "_unmapped_regions.csv"

            with open(filename, "a+") as key_error_file:
                key_error_file.write(str(name) + ";" + str(df.iloc[i]["total_cells"]) + "\n")
            continue

        temp_name = df_temp["name"] #Name of current region
        index_outer_count = resultframe.index[resultframe["Region"] == temp_name] # Find index in resultframe where current region occurs
        cell_count_region = df[df["structure_name"] == resultframe["Region"][index_outer_count[0]]][
            "total_cells"].sum()  # Cell counts in current region become saved as integer
        resultframe.loc[index_outer_count[0], "RegionCellCount"] += cell_count_region #Cell count for structure in current iteration is written into resultframe
        resultframe.loc[index_outer_count[0], "RegionCellCountSummedUp"] += cell_count_region #Cell count for structure in current iteration is written into resultframe
        if not df_temp.empty:
            while int(df_temp["st_level"]) >= 0:
                if int(df_temp["st_level"]) == 0:
                    break  # While loop breaks if root structure is reached in hierarchical tree
                df_temp = reference_df_id.loc[int(df_temp["parent_structure_id"])] # Temporary dataframe of parent region
                temp_name = df_temp["name"] #Update name of parent region
                index_inner_count = resultframe.index[resultframe["Region"] == temp_name]
                resultframe.loc[index_inner_count[0], "RegionCellCountSummedUp"] += cell_count_region # Add cell count of leaf structure to parent structure
    return resultframe

"""
#Converts a CSV to a XML File, for visualization in napari
"""
def write_xml(df_non_cells:utils.pd.DataFrame,df_cells: utils.pd.DataFrame, pathname:str, filename:str):
    df_non_cells = utils.pd.DataFrame(df_non_cells)
    df_cells = utils.pd.DataFrame(df_cells)
    filename = filename[0:-3] + "xml"
    row_counter = 1
    row_counter2 = 1
    df_non_cells_length = len(df_non_cells)
    df_cells_length = len(df_cells)
    with open(pathname+filename, "w") as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write('<CellCounter_Marker_File>\n')
        file.write('  <Image_Properties>\n')
        file.write('    <Image_Filename>placeholder.tif</Image_Filename>\n')
        file.write('  </Image_Properties>\n')
        file.write('  <Marker_Data>\n')
        file.write('    <Current_Type>1</Current_Type>\n')
        file.write('    <Marker_Type>\n')
        file.write('      <Type>1</Type>\n')
        for i in range(len(df_non_cells.iloc[:, 0])):
            row_counter = row_counter + 1
            if row_counter % 10000 == 0:
                print(str(row_counter), "/", str(df_non_cells_length), " lines are processed")
            file.write('      <Marker>\n')
            file.write('        <MarkerX>' + str(df_non_cells.iloc[i, :].x) + '</MarkerX>\n')
            file.write('        <MarkerY>' + str(df_non_cells.iloc[i, :].y) + '</MarkerY>\n')
            file.write('        <MarkerZ>' + str(df_non_cells.iloc[i, :].z) + '</MarkerZ>\n')
            file.write('      </Marker>\n')
        file.write('    </Marker_Type>\n')
        file.write('    <Marker_Type>\n')
        file.write('      <Type>2</Type>\n')
        for i in range(len(df_cells.iloc[:, 0])):
            row_counter2 = row_counter2 + 1
            if row_counter2 % 10000 == 0:
                print(str(row_counter2), "/", str(df_cells_length), " lines are processed")
            file.write('      <Marker>\n')
            file.write('        <MarkerX>' + str(df_cells.iloc[i, :].x) + '</MarkerX>\n')
            file.write('        <MarkerY>' + str(df_cells.iloc[i, :].y) + '</MarkerY>\n')
            file.write('        <MarkerZ>' + str(df_cells.iloc[i, :].z) + '</MarkerZ>\n')
            file.write('      </Marker>\n')
        file.write('    </Marker_Type>\n')
        file.write('  </Marker_Data>\n')
        file.write('</CellCounter_Marker_File>\n')



def write_transformed_xml(df_non_cells: utils.pd.DataFrame,df_cells: utils.pd.DataFrame, pathname:str, filename:str):
    df_non_cells = utils.pd.DataFrame(df_non_cells)
    df_cells = utils.pd.DataFrame(df_cells)
    filename = filename[0:-3] + "xml"
    row_counter = 1
    row_counter2 = 1
    df_non_cells_length = len(df_non_cells)
    df_cells_length = len(df_cells)
    with open(pathname+filename, "w") as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write('<CellCounter_Marker_File>\n')
        file.write('  <Image_Properties>\n')
        file.write('    <Image_Filename>placeholder.tif</Image_Filename>\n')
        file.write('  </Image_Properties>\n')
        file.write('  <Marker_Data>\n')
        file.write('    <Current_Type>1</Current_Type>\n')
        file.write('    <Marker_Type>\n')
        file.write('      <Type>1</Type>\n')
        for i in range(len(df_non_cells.iloc[:, 0])):
            row_counter = row_counter + 1
            if row_counter % 10000 == 0:
                print(str(row_counter), "/", str(df_non_cells_length), " lines are processed")
            file.write('      <Marker>\n')
            file.write('        <MarkerX>' + str(df_non_cells.iloc[i, :].xt) + '</MarkerX>\n')
            file.write('        <MarkerY>' + str(df_non_cells.iloc[i, :].yt) + '</MarkerY>\n')
            file.write('        <MarkerZ>' + str(df_non_cells.iloc[i, :].zt) + '</MarkerZ>\n')
            file.write('      </Marker>\n')
        file.write('    </Marker_Type>\n')
        file.write('    <Marker_Type>\n')
        file.write('      <Type>2</Type>\n')
        for i in range(len(df_cells.iloc[:, 0])):
            row_counter2 = row_counter2 + 1
            if row_counter2 % 10000 == 0:
                print(str(row_counter2), "/", str(df_cells_length), " lines are processed")
            file.write('      <Marker>\n')
            file.write('        <MarkerX>' + str(df_cells.iloc[i, :].xt) + '</MarkerX>\n')
            file.write('        <MarkerY>' + str(df_cells.iloc[i, :].yt) + '</MarkerY>\n')
            file.write('        <MarkerZ>' + str(df_cells.iloc[i, :].zt) + '</MarkerZ>\n')
            file.write('      </Marker>\n')
        file.write('    </Marker_Type>\n')
        file.write('  </Marker_Data>\n')
        file.write('</CellCounter_Marker_File>\n')

"""
#Calls the writeXML-Function to actually transfer certain CSV Files to XML
"""
def process_cells_csv(my_working_directory, chosen_channel):
    pathname2xmlfolder = my_working_directory + "/" + chosen_channel + "xmlFiles"
    if not utils.os.path.exists(pathname2xmlfolder):
        utils.os.makedirs(my_working_directory + "/" + chosen_channel + "xmlFiles")

    df_filename = "/cells_" + chosen_channel + ".csv"
    df_name = my_working_directory + df_filename
    df = utils.pd.read_csv(df_name, header=0, sep=";")

    df_no_label_filename = "/cells_" + chosen_channel + "_no_label.csv"
    df_no_label = df[df["name"] == "No label"]


    df_universe_filename = "/cells_" + chosen_channel + "_universe.csv"
    df_universe = df[df["name"] == "universe"]


    df_universe_plus_no_label_filename = "/non_cells_" + chosen_channel + ".csv"
    df_universe_plus_no_label_name = my_working_directory + df_universe_plus_no_label_filename
    df_universe_plus_no_label = utils.pd.concat([df_no_label,df_universe], axis=0)
    df_universe_plus_no_label.to_csv(df_universe_plus_no_label_name)

    
    df_final = df[df["name"] != "universe"]
    df_final = df_final[df_final["name"] != "No label"]


    df_final_filename = "/cell_classification_" + chosen_channel + ".csv"
    df_final_transformed_filename = "/cell_classification_" + chosen_channel + "_transformed.csv"


    # Multiprocessing the convertion from CSV to XML
    p1 = utils.Process(target=write_xml, args=(df_universe_plus_no_label, df_final, pathname2xmlfolder, df_final_filename))
    p1.start()
    p2 = utils.Process(target=write_transformed_xml, args=(df_universe_plus_no_label, df_final, pathname2xmlfolder, df_final_transformed_filename))
    p2.start()

    #Counts abundancy in different brain regions
    df_final = df_final["name"].value_counts()
    df_final = utils.pd.DataFrame(df_final)

    #Creates column structure name with region names
    df_final["structure_name"] = df_final.index
    df_final = df_final.reset_index(drop=True)

    #Writes a final csv with single cell counts
    df_final.rename(columns={"name": "total_cells"}, inplace=True)
    df_final.to_csv(my_working_directory + "/cells_" + chosen_channel + "_summarized_counts.csv", sep=";")

"""
#calls the analyse_csv Function to actually create the embedded_ontology.csv which is needed from each sample for the analysis
"""
#check from where workinDir and chosen channel is coming from
def embed_ontology(my_working_directory, chosen_channel):
    # Reads ontology file holding the reference region dictionairy
    reference_df = utils.pd.read_csv("ontology_mouse.csv",
                               # Current Refernce Dataframe for mapping
                               # File which stores all important Brain Regions (Atlas?)
                               sep=";",  # Separator
                               header=0,  # Header
                               index_col=0)  # Index Col

    #Creates a mask table with all regions abundant in the ontology file for comparibility
    # Additionally allt the structural abundancies between regions of different hierarchy become recorded in form of id- and structurename arrays
    tracked_levels = create_tracking_list(reference_df)

    #Reads the cell detection csv on a single cell basis (coordinates, transformed coordinates and regionname)
    df = utils.pd.read_csv(my_working_directory + "/cells_" + chosen_channel + "_summarized_counts.csv", header=0, sep=";")

    samplename = utils.os.path.basename(my_working_directory)
    new_df = analyse_csv(df,reference_df, tracked_levels, my_working_directory)
    new_df_name = my_working_directory + "/" + samplename + "_" + chosen_channel + "_embedded_ontology.csv"
    new_df.to_csv(new_df_name, sep=";", index=0)
    return


class CellDetection:
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
                       measure_intensity_det="Source",
                       method_intensity_det="mean",
                       threshold_shape_det=200,
                       save_shape_det=True,
                       amount_processes=10,
                       size_maximum=20,
                       size_minimum=11,
                       area_of_overlap=10,
                       ): 

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

        threshold_maxima_det = None

        # conversion of intensity detection values
        measure_intensity_det = ['source', 'illumination', 'background', 'equalized', 'dog']

        if method_intensity_det == 0:
            method_intensity_det = 'mean'
        elif method_intensity_det == 1:
            method_intensity_det = 'max'

        # Conversion of Shape detection values
        threshold_shape_det = int(threshold_shape_det)
        cell_detection_parameter = utils.cells.default_cell_detection_parameter.copy()

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

        ## Intensity_detection
        cell_detection_parameter['intensity_detection']['measure'] = measure_intensity_det  # we decided to measure all intensities
        cell_detection_parameter['intensity_detection']['method'] = method_intensity_det  # {'max'|'min','mean'|'sum'} # Use method to measure intensity of the cell

        ## Shape_detection
        cell_detection_parameter['shape_detection']['threshold'] = threshold_shape_det

        ## Self edited threshold
        #cell_detection_parameter['threshold'] = threshold_maxima_det

        processing_parameter = utils.cells.default_cell_detection_processing_parameter.copy()
        processing_parameter.update(processes=amount_processes,  # 15, #20,
                                    #optimization = True,  #Todo: Why commented?
                                    size_max=size_maximum,  # 35 100
                                    size_min=size_minimum,  # 30 32
                                    overlap=area_of_overlap,  # 10 30
                                    verbose=True)  # Set True if process needs to be investigated // Lead to the print of process checkpoints

        if self.ws == None:
            alert = utils.QMessageBox()
            alert.setText("You did not choose a workspace yet!")
            alert.exec()
            return


        utils.cells.detect_cells(self.ws.filename('stitched_' + self.chosen_channel),
                           self.ws.filename('cells', postfix='raw_' + self.chosen_channel),
                           cell_detection_parameter=cell_detection_parameter,
                           processing_parameter=processing_parameter)


    def filter_cells(self, filt_size=20):

        thresholds = {'source': None, 'size': (filt_size, None)}
        utils.cells.filter_cells(self.ws.filename('cells', postfix='raw_' + self.chosen_channel),
                           self.ws.filename('cells', postfix='filtered_' + self.chosen_channel),
                           thresholds=thresholds)


    """
    #ClearMap-Code +
    #ProcessCellsCsv +
    #embed_ontology
    """
    def atlas_assignment(self):
        if self.ws == None:
            alert = utils.QMessageBox()
            alert.setText("You did not choose a workspace yet!")
            alert.exec()
            return
        # sink_maxima = self.ws.filename('cells_', postfix = 'raw_'+self.channel_chosen)
        source = self.ws.filename('stitched_' + self.chosen_channel)
        sink_raw = self.ws.source('cells', postfix='raw_' + self.chosen_channel)

        self.filter_cells()

        # Assignment of the cells with filtered maxima
        # Filtered cell maxima are used to execute the alignment to the atlas
        source = self.ws.source('cells', postfix='filtered_' + self.chosen_channel)

        # Didn't understand the functions so far. Seems like coordinates become transformed by each function and reassigned.
        print("Transfromation\n")

        def transformation(coordinates):
            coordinates = utils.res.resample_points(coordinates,
                                              sink=None,
                                              orientation=None,
                                              source_shape=utils.io.shape(self.ws.filename('stitched_' + self.chosen_channel)),
                                              sink_shape=utils.io.shape(self.ws.filename('resampled_' + self.chosen_channel)))

            coordinates = utils.elx.transform_points(coordinates,
                                               sink=None,
                                               transform_directory=self.my_working_directory + '/elastix_resampled_to_auto_' + self.chosen_channel,
                                               binary=True,
                                               indices=False)

            coordinates = utils.elx.transform_points(coordinates,
                                               sink=None,
                                               transform_directory=self.my_working_directory + '/elastix_auto_to_reference_' + self.chosen_channel,
                                               binary=True,
                                               indices=False)
            return coordinates

        # These are the initial coordinates originating in the file cells_filtered.npy containing the coordinates of the filtered maxima.
        # Each coordinate of 3 dimensional space x,y,z  is written into a new numpy array. [[x1,y1,z1],[x2,y2,3],...,[x_last,y_last,z_last]]
        coordinates = utils.np.array([source[c] for c in 'xyz']).T
        source = self.ws.source('cells', postfix='filtered_' + self.chosen_channel)

        # Coordinates become transformed by the above defined transformation function
        coordinates_transformed = transformation(coordinates)

        # Cell annotation
        # Transformed coordinates are used as input to annotate cells by comparing with brain atlas
        # Due to a future warning occured coordinates_transformed was converterted from array[seq] to arr[tuple(seq)] as coordinates_transformed_tuple
        coordinates_transformed_tuple = utils.np.array(tuple(coordinates_transformed))

        print("Label Point\n")
        label = utils.ano.label_points(coordinates_transformed, key='order')
        print("Convert labeled points\n")
        names = utils.ano.convert_label(label, key='order', value='name')

        # Save results
        coordinates_transformed.dtype = [(t, float) for t in ('xt', 'yt', 'zt')]
        nparray_label = utils.np.array(label, dtype=[('order', int)])
        nparray_names = utils.np.array(names, dtype=[('name', 'S256')])

        import numpy.lib.recfunctions as rfn
        cells_data = rfn.merge_arrays([source[:], coordinates_transformed,nparray_label, nparray_names],
                                      flatten=True,
                                      usemask=False)

        utils.io.write(self.ws.filename('cells', postfix=self.chosen_channel), cells_data)
        print("Cells data: \n", cells_data)

        # CSV export
        # Pandas was installed via pip, since np.savetxt had
        csv_source = self.ws.source('cells', postfix=self.chosen_channel)

        # Define headers for pandas.Dataframe for csv export
        header = ', '.join([h for h in csv_source.dtype.names])

        # Conversion of cell data into pandas.DataFrame for csv export
        cells_data_df = utils.pd.DataFrame(cells_data, columns=[h for h in csv_source.dtype.names])

        # Getting rid of np_str_ artifacts in df[['name']]
        cells_data_df[['name']] = names

        # export CSV
        print("Exporting Cells to csv\n")
        cells_data_df.to_csv(self.ws.filename('cells', postfix=self.chosen_channel, extension='csv'), sep=';')

        # ClearMap1.0 export
        # Export is not working so far: Error is "the magic string is not correct; expected b'\x93NUMPY, got b';x;y;z
        ClearMap1_source = self.ws.source('cells', postfix=self.chosen_channel)
        Clearmap1_format = {'points': ['x', 'y', 'z'],
                            'intensities': ['source', 'dog', 'background', 'size'],
                            'points_transformed': ['xt', 'yt', 'zt']}

        for filename, names in Clearmap1_format.items():
            sink = self.ws.filename('cells', postfix=[self.chosen_channel, '_', 'ClearMap1', filename])
            data = utils.np.array([ClearMap1_source[name] if name in ClearMap1_source.dtype.names else utils.np.full(ClearMap1_source.shape[0], utils.np.nan) for name in names])
            utils.io.write(sink, data)

        process_cells_csv(self.my_working_directory,self.chosen_channel)
        embed_ontology(self.my_working_directory,self.chosen_channel)
        return


    def voxelization(self):
        
        if self.ws == None:
            alert = utils.QMessageBox()
            alert.setText("You did not choose a workspace yet!")
            alert.exec()
            return

        annotation_file, reference_file, distance_file = utils.ano.prepare_annotation_files(slicing=(slice(None),
                                                                                               slice(None),
                                                                                               slice(0, 256)),
                                                                                      orientation=(1, -2, 3),
                                                                                      overwrite=False,
                                                                                      verbose=True)
        source = self.ws.source('cells', postfix=self.chosen_channel)
        coordinates = utils.np.array([source[n] for n in ['xt', 'yt', 'zt']]).T
        intensities = source['source']

        # %% Unweighted
        voxelization_parameter = dict(shape=utils.io.shape(annotation_file),
                                      dtype=None,
                                      weights=None,
                                      method='sphere',
                                      radius=(7, 7, 7),
                                      kernel=None,
                                      processes=None,
                                      verbose=True)

        utils.vox.voxelize(coordinates,
                     sink=self.ws.filename('density', postfix='counts_' + self.chosen_channel),
                     **voxelization_parameter)


class Cell_Detection_Layout:
    def cd_layout(self):
        tab = utils.QWidget()
        outer_layout = utils.QVBoxLayout()

        # Widgets for illumination correction
        flatfield_illumination = utils.QComboBox()
        flatfield_illumination.insertItem(0, 'None')
        scaling_illumination = utils.QComboBox()
        scaling_illumination.insertItem(0, 'mean')
        scaling_illumination.insertItem(1, 'max')
        save_illumination = utils.QCheckBox()

        # Widgets for background correction
        shape_background_x = utils.QLineEdit("7")
        shape_background_y = utils.QLineEdit("7")
        form_background = utils.QComboBox()
        form_background.insertItem(0, 'Disk')
        form_background.insertItem(1, 'Sphere')
        save_background = utils.QCheckBox()

        # Widgets for equalization
        execute_equalization = utils.QCheckBox()
        percentile_equalization_low = utils.QLineEdit("0.05")
        percentile_equalization_high = utils.QLineEdit("0.95")
        max_value_equalization = utils.QLineEdit("1.5")
        selem_equalization_x = utils.QLineEdit("200")
        selem_equalization_y = utils.QLineEdit("200")
        selem_equalization_z = utils.QLineEdit("5")
        spacing_equalization_x = utils.QLineEdit("50")
        spacing_equalization_y = utils.QLineEdit("50")
        spacing_equalization_z = utils.QLineEdit("5")
        interpolate_equalization = utils.QLineEdit("1")
        save_equalization = utils.QCheckBox()

        # Widgets for DoG filteringcell
        execute_dog_filter = utils.QCheckBox()
        shape_dog_filter_x = utils.QLineEdit("6")
        shape_dog_filter_y = utils.QLineEdit("6")
        shape_dog_filter_z = utils.QLineEdit("6")
        sigma_dog_filter = utils.QLineEdit("None")
        sigma2_dog_filter = utils.QLineEdit("None")
        save_dog_filter = utils.QCheckBox()

        # Widgets for maxima detection
        hmax_maxima_det = utils.QLineEdit("None")
        shape_maxima_det_x = utils.QLineEdit("6")
        shape_maxima_det_y = utils.QLineEdit("6")
        shape_maxima_det_z = utils.QLineEdit("11")

        # widgets for intensity detection
        measure_intensity_det = utils.QComboBox()
        measure_intensity_det.insertItem(0, "all")
        # measure_intensity_det.insertItem(1,"background")
        method_intensity_det = utils.QComboBox()
        method_intensity_det.insertItem(0, "mean")
        method_intensity_det.insertItem(1, "max")

        # widgets for shape detection
        threshold_shape_det = utils.QLineEdit("200")
        save_shape_det = utils.QCheckBox()

        # widgets for cell detection functions and parameter loading
        detect_cells_button = utils.QPushButton("Detect cells")
        atlas_assignment_button = utils.QPushButton("Atlas assignment")
        voxelization_button = utils.QPushButton("Voxelization")

        config_path = utils.QLineEdit("Insert filename extension")
        load_config_button = utils.QPushButton("Load parameters")
        save_config_button = utils.QPushButton("Save parameters")

        # Widgets for processing paramteres
        amount_processes = utils.QLineEdit('10')
        size_max = utils.QLineEdit('20')
        size_min = utils.QLineEdit('11')
        overlap = utils.QLineEdit('10')


        def save_config(save_path):
            if not utils.os.path.exists(save_path):
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
                                    #threshold_maxima_det.currentIndex(),
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

                cd_df = utils.pd.DataFrame([cd_variable_list], columns=cd_columns)
                cd_df.to_csv(save_path)
            else:
                alert = utils.QMessageBox()
                alert.setText("File already exists!")
                alert.exec()


        def load_config(load_path):
            if utils.os.path.exists(load_path):
                cd_df = utils.pd.read_csv(load_path, header=0)
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
                #threshold_maxima_det.setCurrentIndex(cd_df["threshold maxima"][0])
                measure_intensity_det.setCurrentIndex(cd_df["measure intensity"][0])
                method_intensity_det.setCurrentIndex(cd_df["method intensity det"][0])
                threshold_shape_det.setText(str(cd_df["threshold shape det"][0]))
                amount_processes.setText(str(cd_df["amount processes"][0]))
                size_max.setText(str(cd_df["size max"][0]))
                size_min.setText(str(cd_df["size min"][0]))
                overlap.setText(str(cd_df["overlap"][0]))
            else:
                alert = utils.QMessageBox()
                alert.setText("File does not exist!")
                alert.exec()


        # visualization for all variable features
        inner_layout1 = utils.QGridLayout()
        inner_layout1.addWidget(utils.QLabel("<b>Cell Detection Paramter:</b>"), 0, 0)
        
        # visualization for illumination correction
        inner_layout1.addWidget(utils.QLabel("<b>Illumination correction: </b>"), 1, 0)
        inner_layout1.addWidget(utils.QLabel("Flatfield: "), 2, 0)
        inner_layout1.addWidget(flatfield_illumination, 2, 1)
        inner_layout1.addWidget(utils.QLabel("Scaling:"), 3, 0)
        inner_layout1.addWidget(scaling_illumination, 3, 1)

        # visualization of background correction
        inner_layout2 = utils.QGridLayout()
        inner_layout2.addWidget(utils.QLabel("<b>Background Correction:</b>"), 1, 0)
        inner_layout2.addWidget(utils.QLabel("Shape:"), 2, 0)
        inner_layout2.addWidget(shape_background_x, 2, 1)
        inner_layout2.addWidget(shape_background_y, 2, 2)
        inner_layout2.addWidget(utils.QLabel("Form:"), 3, 0)
        inner_layout2.addWidget(form_background, 3, 1)

        # visualization of equalization
        inner_layout3 = utils.QGridLayout()
        inner_layout3.addWidget(utils.QLabel("<b>Equalization:</b>"), 1, 0)
        inner_layout3.addWidget(utils.QLabel("Perform equalization ?:"), 2, 0)
        inner_layout3.addWidget(execute_equalization, 2, 1)
        inner_layout3.addWidget(utils.QLabel("Percentile:"), 3, 0)
        inner_layout3.addWidget(percentile_equalization_low, 3, 1)
        inner_layout3.addWidget(percentile_equalization_high, 3, 2)
        inner_layout3.addWidget(utils.QLabel("Max Value:"), 4, 0)
        inner_layout3.addWidget(max_value_equalization, 4, 1)
        inner_layout3.addWidget(utils.QLabel("Selem:"), 5, 0)
        inner_layout3.addWidget(selem_equalization_x, 5, 1)
        inner_layout3.addWidget(selem_equalization_y, 5, 2)
        inner_layout3.addWidget(selem_equalization_z, 5, 3)
        inner_layout3.addWidget(utils.QLabel("Spacing:"), 6, 0)
        inner_layout3.addWidget(spacing_equalization_x, 6, 1)
        inner_layout3.addWidget(spacing_equalization_y, 6, 2)
        inner_layout3.addWidget(spacing_equalization_z, 6, 3)
        inner_layout3.addWidget(utils.QLabel("Interpolate:"), 7, 0)
        inner_layout3.addWidget(interpolate_equalization, 7, 1)

        # visualization of dog filtering
        inner_layout4 = utils.QGridLayout()
        inner_layout4.addWidget(utils.QLabel("<b>DoG-Filtering:</b>"), 1, 0)
        inner_layout4.addWidget(utils.QLabel("Execute DoG-Filtering?: "), 2, 0)
        inner_layout4.addWidget(execute_dog_filter, 2, 1)
        inner_layout4.addWidget(utils.QLabel("Shape:"), 3, 0)
        inner_layout4.addWidget(shape_dog_filter_x, 3, 1)
        inner_layout4.addWidget(shape_dog_filter_y, 3, 2)
        inner_layout4.addWidget(shape_dog_filter_z, 3, 3)
        inner_layout4.addWidget(utils.QLabel("Sigma:"), 4, 0)
        inner_layout4.addWidget(sigma_dog_filter, 4, 1)
        inner_layout4.addWidget(utils.QLabel("Sigma2:"), 5, 0)
        inner_layout4.addWidget(sigma2_dog_filter, 5, 1)

        # visualization of maxima detection
        inner_layout5 = utils.QGridLayout()
        inner_layout5.addWidget(utils.QLabel("<b>Maxima Detection:</b>"), 1, 0)
        inner_layout5.addWidget(utils.QLabel("H max:"), 2, 0)
        inner_layout5.addWidget(hmax_maxima_det, 2, 1)
        inner_layout5.addWidget(utils.QLabel("Shape:"), 3, 0)
        inner_layout5.addWidget(shape_maxima_det_x, 3, 1)
        inner_layout5.addWidget(shape_maxima_det_y, 3, 2)
        inner_layout5.addWidget(shape_maxima_det_z, 3, 3)

        # visualization of intensity detection
        inner_layout6 = utils.QGridLayout()
        inner_layout6.addWidget(utils.QLabel("<b>Intensity Detection:</b>"), 1, 0)
        inner_layout6.addWidget(utils.QLabel("Type of measure:"), 2, 0)
        inner_layout6.addWidget(measure_intensity_det, 2, 1)
        inner_layout6.addWidget(utils.QLabel("Method of measure:"), 3, 0)
        inner_layout6.addWidget(method_intensity_det, 3, 1)

        # visualization of shape detection
        inner_layout7 = utils.QGridLayout()
        inner_layout7.addWidget(utils.QLabel("<b>Shape detection:</b>"), 0, 0)
        inner_layout7.addWidget(threshold_shape_det, 1, 1)

        # visualization of Processing parameter widgets
        inner_layout8 = utils.QGridLayout()
        inner_layout8.addWidget(utils.QLabel("<b>Processing paramters:</b>"), 0, 0)
        inner_layout8.addWidget(utils.QLabel("No. of parallel processes:"), 1, 0)
        inner_layout8.addWidget(amount_processes, 1, 1)
        inner_layout8.addWidget(utils.QLabel("Size max:"), 1, 2)
        inner_layout8.addWidget(size_max, 1, 3)
        inner_layout8.addWidget(utils.QLabel("Size min:"), 1, 4)
        inner_layout8.addWidget(size_min, 1, 4)
        inner_layout8.addWidget(utils.QLabel("Overlap:"), 1, 5)
        inner_layout8.addWidget(overlap, 1, 6)

        # visualization of loading,saving and detection functions
        inner_layout9 = utils.QHBoxLayout()
        inner_layout9.addWidget(config_path)
        inner_layout9.addWidget(load_config_button)
        inner_layout9.addWidget(save_config_button)
        inner_layout9.addWidget(detect_cells_button)
        inner_layout9.addWidget(atlas_assignment_button)
        inner_layout9.addWidget(voxelization_button)

        # Connection of signals and slots for cell detection
        load_config_button.clicked.connect(
            lambda: load_config(load_path = utils.os.getcwd() + "/cell_detection_" + config_path.text() + ".csv"))
        save_config_button.clicked.connect(
            lambda: save_config(save_path =utils.os.getcwd() + "/cell_detection_" + config_path.text() + ".csv"))
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
                                        measure_intensity_det=measure_intensity_det.currentIndex(),
                                        method_intensity_det=method_intensity_det.currentIndex(),
                                        threshold_shape_det=threshold_shape_det.text(),
                                        amount_processes=int(amount_processes.text()),
                                        size_maximum=int(size_max.text()), size_minimum=int(size_min.text()),
                                        area_of_overlap=int(overlap.text())))

        atlas_assignment_button.clicked.connect(lambda: self.atlas_assignment())
        voxelization_button.clicked.connect(lambda: self.voxelization())

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
