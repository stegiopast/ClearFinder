import utils

def createTrackingList(dataframe: utils.pd.DataFrame) -> utils.pd.DataFrame:
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

#Input: pd.Dataframe (mouse_ontology.csv) , trackedList (pd.Dataframe from createTrackingList), and the length of the pd.Dataframe
#Creates a Template-Resultframe, which can be used for every sample
#Cols: Region, trackedWay, CorrespondingLevel, RegionCellCount, RegionCellCountSummedUp
"""
def createResultframe(df, trackedList):
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
#df = summarized_counts
#reference = mouse_ontology.csv as pd.Dataframe
#trackedLevels = pd.Dataframe of the tracked regions and corresponding Levels

#Output: The Template-Resultframe from (createResultframe) but filled with values of the cellcount of each region
"""
def analyse_csv(df: utils.pd.DataFrame,reference_df: utils.pd.DataFrame, trackedLevels: list, myWorkingDirectory: str) -> utils.pd.DataFrame:
    total_cellcount = int(df["total_cells"].sum())  # get total cellcount for reference
    df["name"] = df["structure_name"]

    #Reference_df_ID becomes copied twice to allow O(1) access to "id" or "name" as index of reference_frame
    reference_df_ID = reference_df.set_index(reference_df["id"])
    reference_df_Name = reference_df.set_index(reference_df["name"])

    #Creation of a template resultframe including all regions and a fusion of ontology_csv and trackedLevels mask,
    # all entries in RegionCellCount and RegionCellCountSummedUp are initialized as 0
    resultframe = createResultframe(reference_df, trackedLevels)

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
            samplename = utils.os.path.basename(myWorkingDirectory)
            filename = myWorkingDirectory + "/" + samplename + "_unmapped_regions.csv"

            with open(filename, "a+") as KeyError_file:
                KeyError_file.write(str(name) + ";" + str(df.iloc[i]["total_cells"]) + "\n")
            continue

        temp_name = df_temp["name"] #Name of current region
        index_outerCount = resultframe.index[resultframe["Region"] == temp_name] # Find index in resultframe where current region occurs
        cellcountRegion = df[df["structure_name"] == resultframe["Region"][index_outerCount[0]]][
            "total_cells"].sum()  # Cell counts in current region become saved as integer
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
#Converts a CSV to a XML File, for visualization in napari
"""
def writeXml(df:utils.pd.DataFrame, pathname:str, filename:str):
    df = utils.pd.DataFrame(df)
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
def write_transformed_xml(dataframe: utils.pd.DataFrame, pathname:str, filename:str):
    df = utils.pd.DataFrame(dataframe)
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
#Calls the writeXML-Function to actually transfer certain CSV Files to XML
"""
def processCellsCsv(self):
    pathname2xmlfolder = self.myWorkingDirectory + "/" + self.chosenChannel + "xmlFiles"
    if not utils.os.path.exists(pathname2xmlfolder):
        utils.os.makedirs(self.myWorkingDirectory + "/" + self.chosenChannel + "xmlFiles")

    df_filename = "/cells_" + self.chosenChannel + ".csv"
    df_name = self.myWorkingDirectory + df_filename
    df = utils.pd.read_csv(df_name, header=0, sep=";")

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
    p1 = utils.Process(target=self.writeXml, args=(df, pathname2xmlfolder, df_filename))
    p1.start()
    p2 = utils.Process(target=self.writeXml, args=(df_no_label, pathname2xmlfolder, df_no_label_filename))
    p2.start()
    p3 = utils.Process(target=self.writeXml, args=(df_universe, pathname2xmlfolder, df_universe_filename))
    p3.start()
    p4 = utils.Process(target=self.writeXml, args=(df_final, pathname2xmlfolder, df_final_filename))
    p4.start()
    p5 = utils.Process(target=self.write_transformed_xml, args=(df_final, pathname2xmlfolder, df_final_transformed_filename))
    p5.start()

    #Counts abundancy in different brain regions
    df_final = df_final["name"].value_counts()
    df_final = utils.pd.DataFrame(df_final)

    #Creates column structure name with region names
    df_final["structure_name"] = df_final.index
    df_final = df_final.reset_index(drop=True)

    #Writes a final csv with single cell counts
    df_final.rename(columns={"name": "total_cells"}, inplace=True)
    df_final.to_csv(self.myWorkingDirectory + "/cells_" + self.chosenChannel + "_summarized_counts.csv", sep=";")



"""
#calls the analyse_csv Function to actually create the embedded_ontology.csv which is needed from each sample for the analysis
"""
def embedOntology():
    # Reads ontology file holding the reference region dictionairy
    reference_df = utils.pd.read_csv("ontology_mouse.csv",
                               # Current Refernce Dataframe for mapping
                               # File which stores all important Brain Regions (Atlas?)
                               sep=";",  # Separator
                               header=0,  # Header
                               index_col=0)  # Index Col

    #Creates a mask table with all regions abundant in the ontology file for comparibility
    # Additionally allt the structural abundancies between regions of different hierarchy become recorded in form of id- and structurename arrays
    trackedLevels = createTrackingList(reference_df)

    #Reads the cell detection csv on a single cell basis (coordinates, transformed coordinates and regionname)
    df = utils.pd.read_csv(myWorkingDirectory + "/cells_" + chosenChannel + "_summarized_counts.csv", header=0, sep=";")

    samplename = utils.os.path.basename(myWorkingDirectory)
    new_df = analyse_csv(df,reference_df, trackedLevels)
    new_df_name = myWorkingDirectory + "/" + samplename + "_" + chosenChannel + "_embedded_ontology.csv"
    new_df.to_csv(new_df_name, sep=";", index=0)
    return





class Cell_Detection:

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
                       #threshold_maxima_det=297.380,
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

        #if threshold_maxima_det == 0:
        threshold_maxima_det = None
        #elif threshold_maxima_det == 1:
        #    threshold_maxima_det = "background mean"
        #elif threshold_maxima_det == 2:
        #    threshold_maxima_det = "total mean"

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
        #Philipp: auskommentiert von cell_detection_parameter
        #cell_detection_parameter['maxima_detection']['threshold'] = None  # 0.55 good value fter dog + equalizaziont for 3258  #5 good value after equalization for 3258 #250 Best so fat without equalization for 3258 # Only maxima above this threshold are detected. If None all are detected // float

        ## Intensity_detection
        cell_detection_parameter['intensity_detection']['measure'] = measure_intensity_det;  # we decided to measure all intensities
        cell_detection_parameter['intensity_detection']['method'] = method_intensity_det  # {'max'|'min','mean'|'sum'} # Use method to measure intensity of the cell

        ## Shape_detection
        cell_detection_parameter['shape_detection']['threshold'] = threshold_shape_det;

        ## Self edited threshold
        #cell_detection_parameter['threshold'] = threshold_maxima_det

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
    #ClearMap-Code +
    #ProcessCellsCsv +
    #embedOntology
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
            coordinates = utils.res.resample_points(coordinates,
                                              sink=None,
                                              orientation=None,
                                              source_shape=utils.io.shape(self.ws.filename('stitched_' + self.chosenChannel)),
                                              sink_shape=utils.io.shape(self.ws.filename('resampled_' + self.chosenChannel)))

            coordinates = utils.elx.transform_points(coordinates,
                                               sink=None,
                                               transform_directory=self.myWorkingDirectory + '/elastix_resampled_to_auto_' + self.chosenChannel,
                                               binary=True,
                                               indices=False)

            coordinates = utils.elx.transform_points(coordinates,
                                               sink=None,
                                               transform_directory=self.myWorkingDirectory + '/elastix_auto_to_reference_' + self.chosenChannel,
                                               binary=True,
                                               indices=False)
            return coordinates

        # These are the initial coordinates originating in the file cells_filtered.npy containing the coordinates of the filtered maxima.
        # Each coordinate of 3 dimensional space x,y,z  is written into a new numpy array. [[x1,y1,z1],[x2,y2,3],...,[x_last,y_last,z_last]]
        coordinates = utils.np.array([source[c] for c in 'xyz']).T
        source = self.ws.source('cells', postfix='filtered_' + self.chosenChannel)

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
        nparray_label = utils.np.array(label, dtype=[('order', int)]);
        nparray_names = utils.np.array(names, dtype=[('name', 'S256')])

        import numpy.lib.recfunctions as rfn
        cells_data = rfn.merge_arrays([source[:], coordinates_transformed,nparray_label, nparray_names],
                                      flatten=True,
                                      usemask=False)

        utils.io.write(self.ws.filename('cells', postfix=self.chosenChannel), cells_data)
        print("Cells data: \n", cells_data)

        # CSV export
        # Pandas was installed via pip, since np.savetxt had
        csv_source = self.ws.source('cells', postfix=self.chosenChannel)

        # Define headers for pandas.Dataframe for csv export
        header = ', '.join([h for h in csv_source.dtype.names])

        # Conversion of cell data into pandas.DataFrame for csv export
        cells_data_df = utils.pd.DataFrame(cells_data, columns=[h for h in csv_source.dtype.names])

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
            data = utils.np.array([ClearMap1_source[name] if name in ClearMap1_source.dtype.names else np.full(ClearMap1_source.shape[0], np.nan) for name in names])
            utils.io.write(sink, data)

        self.processCellsCsv()
        self.embedOntology()
        return

    def voxelization(self):
        annotation_file, reference_file, distance_file = utils.ano.prepare_annotation_files(slicing=(slice(None),
                                                                                               slice(None),
                                                                                               slice(0, 256)),
                                                                                      orientation=(1, -2, 3),
                                                                                      overwrite=False,
                                                                                      verbose=True)
        source = self.ws.source('cells', postfix=self.chosenChannel)
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
                     sink=self.ws.filename('density', postfix='counts_' + self.chosenChannel),
                     **voxelization_parameter)