import utils


def create_tracking_list(dataframe: utils.pd.DataFrame) -> utils.pd.DataFrame:
    """
    Generates a tracking list of hierarchical levels for each entry in the input dataframe.

    This function creates two lists for each entry in the dataframe:
    - `TrackedWay`: Contains the hierarchical path of `name` values for each row, following
      the `parent_structure_id` field up through the hierarchy until reaching the top level.
    - `CorrespondingLevel`: Contains the corresponding structural levels (`st_level`) for each entry
      in the `TrackedWay` list.

    Parameters:
    -----------
    dataframe : utils.pd.DataFrame
        Input DataFrame containing the hierarchical data. It should contain the columns:
        - `id`: Unique identifier for each row.
        - `name`: Name of the structure/entry.
        - `st_level`: Structural level, where 0 indicates the top level.
        - `parent_structure_id`: ID of the parent structure.

    Returns:
    --------
    utils.pd.DataFrame
        A DataFrame with two columns:
        - `TrackedWay`: List of names representing the hierarchical path for each entry.
        - `CorrespondingLevel`: List of structural levels for each entry in the `TrackedWay`.

    Example:
    --------
    Given a dataframe with columns `id`, `name`, `st_level`, and `parent_structure_id`, the
    function will return a new dataframe with each row representing the traced path of names
    and levels from each entry up to the top level in the hierarchy.
    """
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

def create_resultframe(df: utils.pd.DataFrame, tracked_list: utils.pd.DataFrame) -> utils.pd.DataFrame:
    """
    Creates a template result DataFrame for tracking brain region data in samples.

    This function generates a result DataFrame to serve as a template for tracking brain region 
    cell counts in each sample, structured with columns relevant for hierarchical brain region 
    information and count tracking. The DataFrame contains initial counts of zero and can be 
    populated with actual sample data.

    Parameters:
    -----------
    df : utils.pd.DataFrame
        Input DataFrame (e.g., loaded from `mouse_ontology.csv`) containing brain region names 
        in a `name` column.

    tracked_list : utils.pd.DataFrame
        DataFrame generated from `create_tracking_list`, containing two columns:
        - `TrackedWay`: List of hierarchical brain region names for each region.
        - `CorrespondingLevel`: List of structural levels associated with each entry in `TrackedWay`.

    Returns:
    --------
    utils.pd.DataFrame
        A template result DataFrame with the following columns:
        - `Region`: Name of the brain region.
        - `TrackedWay`: Hierarchical path of names for each brain region.
        - `CorrespondingLevel`: Corresponding structural level for each entry in `TrackedWay`.
        - `RegionCellCount`: Count of cells in each region, initialized to 0.
        - `RegionCellCountSummedUp`: Summed-up cell count for each region and its hierarchy, initialized to 0.

    Example:
    --------
    Given a brain region DataFrame (`df`) and the tracked list DataFrame from `create_tracking_list`, 
    this function creates a result frame that can be filled with sample-specific data in the columns 
    `RegionCellCount` and `RegionCellCountSummedUp`.
    """
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

def analyse_csv(df: utils.pd.DataFrame,reference_df: utils.pd.DataFrame, tracked_levels: list, my_working_directory: str) -> utils.pd.DataFrame:
    """
    Analyzes brain region data from a sample DataFrame, summarizing cell counts across hierarchical brain regions.

    This function processes a DataFrame containing cell count information for different brain regions. 
    Using a reference DataFrame with hierarchical information, it generates a result DataFrame with 
    cumulative cell counts for each region, allowing for hierarchical summarization. Unmapped regions are 
    saved to a separate CSV file in the working directory.

    Parameters:
    -----------
    df : utils.pd.DataFrame
        Input DataFrame containing cell count data for each brain region in the sample. 
        Expected columns include:
        - `structure_name`: Name of the brain region.
        - `total_cells`: Total number of cells in the region.

    reference_df : utils.pd.DataFrame
        DataFrame containing reference brain region information, including hierarchical structure.
        Expected columns include:
        - `id`: Unique identifier for each region.
        - `name`: Name of the brain region.
        - `st_level`: Structural level in the hierarchy.
        - `parent_structure_id`: ID of the parent region.

    tracked_levels : list
        List of tracked hierarchical levels for each brain region, created by `create_tracking_list`.

    my_working_directory : str
        Path to the working directory where unmapped regions will be saved as a CSV file.

    Returns:
    --------
    utils.pd.DataFrame
        A DataFrame (`resultframe`) with columns:
        - `Region`: Brain region name.
        - `TrackedWay`: List of hierarchical names from the region up to the root.
        - `CorrespondingLevel`: List of corresponding levels for each tracked name.
        - `RegionCellCount`: Total cell count for each region.
        - `RegionCellCountSummedUp`: Summed cell count, including counts from subregions in the hierarchy.

    Process:
    --------
    1. Initializes a result DataFrame with hierarchical information using `create_resultframe`.
    2. Iterates over each entry in `df` to match and embed cell counts into `resultframe`.
    3. For each region, adds cell counts to parent regions recursively until the root region is reached.
    4. Saves unmapped regions (not in `reference_df`) to a separate CSV file in `my_working_directory`.

    Example:
    --------
    This function can be used to generate cumulative cell count data for brain regions in a hierarchical 
    structure, helping to analyze the distribution of cells across different levels in the ontology.
    """
    print("-------------------DF HEAD---------------------------",df.head())
    total_cellcount = int(df["total_cells"].sum())  # get total cellcount for reference
    print("total_cellcount!!! ", total_cellcount)
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
            filename = f"{my_working_directory}/{samplename}_unmapped_regions.csv"

            with open(filename, "a+") as key_error_file:
                total_cells = str(df.iloc[i]["total_cells"])
                key_error_file.write(f"{str(name)};{total_cells}\n")
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

def write_xml(df_non_cells:utils.pd.DataFrame,df_cells: utils.pd.DataFrame, pathname:str, filename:str) -> None:
    """
    Writes cell and non-cell marker data from DataFrames to an XML file in a specified format.

    This function generates an XML file containing coordinates for cell and non-cell markers. 
    The XML is structured according to a specific schema, with separate marker types for cells 
    and non-cells, including 3D coordinates (X, Y, Z) for each marker. The function also prints 
    progress messages for every 10,000 entries processed in each DataFrame.

    Parameters:
    -----------
    df_non_cells : utils.pd.DataFrame
        DataFrame containing non-cell marker coordinates, expected to have columns:
        - `x`: X-coordinate of the marker.
        - `y`: Y-coordinate of the marker.
        - `z`: Z-coordinate of the marker.

    df_cells : utils.pd.DataFrame
        DataFrame containing cell marker coordinates, expected to have columns:
        - `x`: X-coordinate of the marker.
        - `y`: Y-coordinate of the marker.
        - `z`: Z-coordinate of the marker.

    pathname : str
        Directory path where the XML file will be saved.

    filename : str
        Base filename for the XML file. The function modifies this to have an `.xml` extension.

    Returns:
    --------
    None
        Writes the output directly to an XML file in the specified directory.

    Process:
    --------
    1. Initializes an XML structure with header and image properties.
    2. Writes marker data from `df_non_cells` as `<Marker>` elements under `<Type>1</Type>`.
    3. Writes marker data from `df_cells` as `<Marker>` elements under `<Type>2</Type>`.
    4. Adds progress output for every 10,000 markers processed to monitor large DataFrame handling.

    Example:
    --------
    Given DataFrames `df_non_cells` and `df_cells` with appropriate coordinate columns, 
    this function creates an XML file with markers categorized by type, useful for 
    applications needing spatial tracking of cell markers.
    """
    df_non_cells = utils.pd.DataFrame(df_non_cells)
    df_cells = utils.pd.DataFrame(df_cells)
    filename = f"{filename[0:-3]}xml"
    row_counter = 1
    row_counter2 = 1
    df_non_cells_length = len(df_non_cells)
    df_cells_length = len(df_cells)
    with open(f"{pathname}{filename}", "w") as file:
        file.write(f"<?xml version='1.0' encoding='UTF-8'?>\n")
        file.write("<CellCounter_Marker_File>\n")
        file.write("  <Image_Properties>\n")
        file.write("    <Image_Filename>placeholder.tif</Image_Filename>\n")
        file.write("  </Image_Properties>\n")
        file.write("  <Marker_Data>\n")
        file.write("    <Current_Type>1</Current_Type>\n")
        file.write("    <Marker_Type>\n")
        file.write("      <Type>1</Type>\n")
        for i in range(len(df_non_cells.iloc[:, 0])):
            row_counter = row_counter + 1
            if row_counter % 10000 == 0:
                print(str(row_counter), "/", str(df_non_cells_length), " lines are processed")
            file.write("      <Marker>\n")
            file.write(f"        <MarkerX>{str(df_non_cells.iloc[i, :].x)}</MarkerX>\n")
            file.write(f"        <MarkerY>{str(df_non_cells.iloc[i, :].y)}</MarkerY>\n")
            file.write(f"        <MarkerZ>{str(df_non_cells.iloc[i, :].z)}</MarkerZ>\n")
            file.write("      </Marker>\n")
        file.write("    </Marker_Type>\n")
        file.write("    <Marker_Type>\n")
        file.write("      <Type>2</Type>\n")
        for i in range(len(df_cells.iloc[:, 0])):
            row_counter2 = row_counter2 + 1
            if row_counter2 % 10000 == 0:
                print(str(row_counter2), "/", str(df_cells_length), " lines are processed")
            file.write("      <Marker>\n")
            file.write(f"        <MarkerX>{str(df_cells.iloc[i, :].x)}</MarkerX>\n")
            file.write(f"        <MarkerY>{str(df_cells.iloc[i, :].y)}</MarkerY>\n")
            file.write(f"        <MarkerZ>{str(df_cells.iloc[i, :].z)}</MarkerZ>\n")
            file.write("      </Marker>\n")
        file.write("    </Marker_Type>\n")
        file.write("  </Marker_Data>\n")
        file.write("</CellCounter_Marker_File>\n")



def write_transformed_xml(df_non_cells: utils.pd.DataFrame,df_cells: utils.pd.DataFrame, pathname:str, filename:str):
    """
    Writes transformed cell and non-cell data to an XML file in the format expected by CellCounter.

    This function generates an XML file that contains the coordinates of both cells and non-cells in 3D space.
    It processes two DataFrames containing the transformed coordinates of non-cell and cell points, and writes them
    into the appropriate XML structure. The XML file is saved with the specified `filename` at the given `pathname`.

    Parameters:
    df_non_cells (pandas.DataFrame): A DataFrame containing the transformed coordinates of non-cell points.
                                      The DataFrame should have at least the columns 'xt', 'yt', and 'zt' for x, y, and z coordinates.
    df_cells (pandas.DataFrame): A DataFrame containing the transformed coordinates of cell points.
                                  The DataFrame should have at least the columns 'xt', 'yt', and 'zt' for x, y, and z coordinates.
    pathname (str): The directory path where the XML file will be saved.
    filename (str): The name of the output XML file. The file extension will be automatically set to ".xml".

    Returns:
    None: The function writes the output XML file directly to the specified location.

    Example:
    >>> df_non_cells = pd.DataFrame({'xt': [1.0, 2.0], 'yt': [3.0, 4.0], 'zt': [5.0, 6.0]})
    >>> df_cells = pd.DataFrame({'xt': [7.0, 8.0], 'yt': [9.0, 10.0], 'zt': [11.0, 12.0]})
    >>> write_transformed_xml(df_non_cells, df_cells, '/path/to/save/', 'output.xml')

    File Format:
    The function creates an XML file with the following structure:
    - The root element `<CellCounter_Marker_File>` contains metadata and marker data.
    - `<Image_Properties>` holds information about the image (e.g., the filename).
    - `<Marker_Data>` contains two `<Marker_Type>` sections:
      - The first `<Marker_Type>` represents non-cell data (Type 1).
      - The second `<Marker_Type>` represents cell data (Type 2).
    - Each marker is represented by `<Marker>` elements with `MarkerX`, `MarkerY`, and `MarkerZ` for the coordinates.
    """
    df_non_cells = utils.pd.DataFrame(df_non_cells)
    df_cells = utils.pd.DataFrame(df_cells)
    filename = f"{filename[0:-3]}xml"
    row_counter = 1
    row_counter2 = 1
    df_non_cells_length = len(df_non_cells)
    df_cells_length = len(df_cells)
    with open(f"{pathname}{filename}", "w") as file:
        file.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        file.write("<CellCounter_Marker_File>\n")
        file.write("  <Image_Properties>\n")
        file.write("    <Image_Filename>placeholder.tif</Image_Filename>\n")
        file.write("  </Image_Properties>\n")
        file.write("  <Marker_Data>\n")
        file.write("    <Current_Type>1</Current_Type>\n")
        file.write("    <Marker_Type>\n")
        file.write("      <Type>1</Type>\n")
        for i in range(len(df_non_cells.iloc[:, 0])):
            row_counter = row_counter + 1
            if row_counter % 10000 == 0:
                print(str(row_counter), "/", str(df_non_cells_length), " lines are processed")
            file.write("      <Marker>\n")
            file.write(f"        <MarkerX>{str(df_non_cells.iloc[i, :].xt)}</MarkerX>\n")
            file.write(f"        <MarkerY>{str(df_non_cells.iloc[i, :].yt)}</MarkerY>\n")
            file.write(f"        <MarkerZ>{str(df_non_cells.iloc[i, :].zt)}</MarkerZ>\n")
            file.write("      </Marker>\n")
        file.write("    </Marker_Type>\n")
        file.write("    <Marker_Type>\n")
        file.write("      <Type>2</Type>\n")
        for i in range(len(df_cells.iloc[:, 0])):
            row_counter2 = row_counter2 + 1
            if row_counter2 % 10000 == 0:
                print(str(row_counter2), "/", str(df_cells_length), " lines are processed")
            file.write("      <Marker>\n")
            file.write(f"        <MarkerX>{str(df_cells.iloc[i, :].xt)}</MarkerX>\n")
            file.write(f"        <MarkerY>{str(df_cells.iloc[i, :].yt)}</MarkerY>\n")
            file.write(f"        <MarkerZ>{str(df_cells.iloc[i, :].zt)}</MarkerZ>\n")
            file.write("      </Marker>\n")
        file.write("    </Marker_Type>\n")
        file.write("  </Marker_Data>\n")
        file.write("</CellCounter_Marker_File>\n")

def process_cells_csv(my_working_directory: str, chosen_channel: str) -> None:
    """
    Processes cell data from CSV files, filters specific markers, and saves transformed data to XML and CSV files.

    This function reads cell data from a CSV file, filters for specific region markers (like "universe" and "No label"),
    and prepares separate files for these markers. It also performs multiprocessing to convert the data into XML format 
    for specific types of cell classifications, as well as generating a summary count of cells in each brain region.

    Parameters:
    -----------
    my_working_directory : str
        Directory path where the CSV and XML files will be saved and accessed.

    chosen_channel : str
        Channel name (used as a filename prefix) for the cell data to specify processing output files.

    Returns:
    --------
    None
        Outputs various CSV and XML files directly to `my_working_directory`.

    Process:
    --------
    1. Creates an XML output directory if it doesn’t already exist.
    2. Reads cell data from a specified CSV file (`cells_<chosen_channel>.csv`).
    3. Filters the data into separate DataFrames for:
       - Cells marked as "No label" (`cells_<chosen_channel>_no_label.csv`).
       - Cells marked as "universe" (`cells_<chosen_channel>_universe.csv`).
       - Both "No label" and "universe" (`non_cells_<chosen_channel>.csv`).
    4. Generates a final filtered DataFrame excluding "universe" and "No label" markers, and saves it as `cell_classification_<chosen_channel>.csv`.
    5. Uses multiprocessing to convert these CSV files into XML format by invoking:
       - `write_xml` for standard cell classification.
       - `write_transformed_xml` for transformed cell classification.
    6. Counts the abundance of cells in each brain region and saves the summarized count to `cells_<chosen_channel>_summarized_counts.csv`.

    Example:
    --------
    Calling `process_cells_csv('/path/to/dir', 'ch1')` will:
    - Process CSV files in `/path/to/dir` for the specified channel (`ch1`).
    - Generate filtered and transformed data files in both CSV and XML formats.
    """
    pathname2xmlfolder = f"{my_working_directory}/{chosen_channel}xmlFiles"
    if not utils.os.path.exists(pathname2xmlfolder):
        utils.os.makedirs(f"{my_working_directory}/{chosen_channel}xmlFiles")

    df_filename = f"/cells_{chosen_channel}.csv"
    df_name = f"{my_working_directory}{df_filename}"
    df = utils.pd.read_csv(df_name, header=0, sep=";")

    df_no_label_filename = f"/cells_{chosen_channel}_no_label.csv"
    df_no_label = df[df["name"] == "No label"]


    df_universe_filename = f"/cells_{chosen_channel}_universe.csv"
    df_universe = df[df["name"] == "universe"]


    df_universe_plus_no_label_filename = f"/non_cells_{chosen_channel}.csv"
    df_universe_plus_no_label_name = f"{my_working_directory}{df_universe_plus_no_label_filename}"
    df_universe_plus_no_label = utils.pd.concat([df_no_label,df_universe], axis=0)
    df_universe_plus_no_label.to_csv(df_universe_plus_no_label_name)

    
    df_final = df[df["name"] != "universe"]
    df_final = df_final[df_final["name"] != "No label"]


    df_final_filename = f"/cell_classification_{chosen_channel}.csv"
    df_final_transformed_filename = f"/cell_classification_{chosen_channel}_transformed.csv"


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
    df_final.to_csv(f"{my_working_directory}/cells_{chosen_channel}_summarized_counts.csv", sep=";")


#check from where workinDir and chosen channel is coming from
def embed_ontology(my_working_directory, chosen_channel):
    """
    Embeds hierarchical ontology information into cell data, saving the result as an enriched CSV file.

    This function reads brain region ontology information and cell data, mapping cell counts to 
    hierarchical brain structures. It outputs an enriched DataFrame, which includes cumulative cell 
    counts for each brain region across different hierarchy levels. This result is saved as a new CSV file.

    Parameters:
    -----------
    my_working_directory : str
        Directory path where input cell data is stored and output CSV files will be saved.

    chosen_channel : str
        Channel name for the cell data (used as a suffix for file naming).

    Returns:
    --------
    None
        The function saves an embedded ontology CSV file in the specified working directory.

    Process:
    --------
    1. Reads `ontology_mouse.csv`, a reference ontology file containing brain region hierarchies.
    2. Calls `create_tracking_list` to generate a tracked level list with hierarchical abundances and mappings.
    3. Reads the cell data file (`cells_<chosen_channel>_summarized_counts.csv`), which contains summarized cell counts for each region.
    4. Calls `analyse_csv` to:
       - Embed ontology levels into the cell data.
       - Summarize cell counts for each brain region, incorporating hierarchical information.
    5. Saves the enriched DataFrame as `<samplename>_<chosen_channel>_embedded_ontology.csv` in `my_working_directory`.

    Example:
    --------
    Running `embed_ontology('/path/to/dir', 'ch1')`:
    - Embeds ontology information from `ontology_mouse.csv` into the cell data for channel `ch1`.
    - Saves the enriched ontology data as a CSV file in `/path/to/dir`.
    """
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
    df = utils.pd.read_csv(f"{my_working_directory}/cells_{chosen_channel}_summarized_counts.csv", header=0, sep=";")

    samplename = utils.os.path.basename(my_working_directory)
    new_df = analyse_csv(df,reference_df, tracked_levels, my_working_directory)
    new_df_name = f"{my_working_directory}/{samplename}_{chosen_channel}_embedded_ontology.csv"
    new_df.to_csv(new_df_name, sep=";", index=0)
    return


class CellDetection:
   
    def cell_detection(self, 
                   flatfield_illumination = None,           
                   scaling_illumination: str = "max",                    
                   shape_background_x: int = 7,                           
                   shape_background_y: int = 7,                           
                   form_background: str = "Disk",                     
                   execute_equalization: bool = False,                   
                   percentile_equalization_low: float = 0.5,            
                   percentile_equalization_high: float = 0.95,          
                   max_value_equalization: float = 1.5,                  
                   selem_equalization_x: int = 200,                       
                   selem_equalization_y: int = 200,                       
                   selem_equalization_z: int = 5,                         
                   spacing_equalization_x: int = 50,                      
                   spacing_equalization_y: int = 50,                      
                   spacing_equalization_z: int = 5,                       
                   interpolate_equalization: int = 1,                     
                   execute_dog_filter: bool = False,                    
                   shape_dog_filter_x: int = 6,                           
                   shape_dog_filter_y: int = 6,                           
                   shape_dog_filter_z: int = 6,                           
                   sigma_dog_filter:float = None,              
                   sigma2_dog_filter:float = None,            
                   hmax_maxima_det = None,                 
                   shape_maxima_det_x: int = 6,                           
                   shape_maxima_det_y: int = 6,                           
                   shape_maxima_det_z: int = 11,                          
                   measure_intensity_det: str = "Source",                 
                   method_intensity_det: str = "mean",                  
                   threshold_shape_det: int = 200,                        
                   save_shape_det: bool = True,                         
                   amount_processes: int = 10,                            
                   size_maximum: int = 20,                                
                   size_minimum: int = 11,                                
                   area_of_overlap: int = 10                              
                   ):
        """
        Detects cells in imaging data based on specified preprocessing, filtering, and detection parameters.

        This function configures and executes cell detection in 3D imaging data. It allows for image equalization, 
        background correction, difference of Gaussian (DoG) filtering, and maxima detection, providing flexibility 
        for identifying cellular structures based on shape, intensity, and size thresholds.

        Parameters:
        -----------
        flatfield_illumination : Optional[int]
            Determines flatfield illumination for correction; default is None (no correction).
        
        scaling_illumination : str
            Method of scaling after flatfield correction ("max" or "mean").
        
        shape_background_x, shape_background_y : int
            Dimensions for background correction (cell shape parameters).
        
        form_background : str
            Shape of background correction element; "Disk" or "Sphere".

        execute_equalization : bool
            If True, performs histogram equalization on the data.

        percentile_equalization_low, percentile_equalization_high : float
            Percentiles used to clip intensity values during equalization.

        max_value_equalization : float
            Maximum intensity value for equalization scaling.
        
        selem_equalization_x, selem_equalization_y, selem_equalization_z : int
            Shape elements for 3D equalization structuring.
        
        spacing_equalization_x, spacing_equalization_y, spacing_equalization_z : int
            Spacing for equalization in x, y, and z dimensions.
        
        interpolate_equalization : int
            Interpolation method for equalization (e.g., nearest, linear).
        
        execute_dog_filter : bool
            If True, applies a difference of Gaussian filter.
        
        shape_dog_filter_x, shape_dog_filter_y, shape_dog_filter_z : int
            Shape of DoG filter elements.
        
        sigma_dog_filter, sigma2_dog_filter : Optional[float]
            Gaussian standard deviations for the DoG filter; `None` uses default values.

        hmax_maxima_det : Optional[int]
            Height threshold for maxima detection; None uses simple local maxima detection.

        shape_maxima_det_x, shape_maxima_det_y, shape_maxima_det_z : int
            Dimensions for maxima detection structuring.

        measure_intensity_det : str
            Source for intensity measurement ("source", "illumination", "background", etc.).

        method_intensity_det : str
            Method to measure intensity for each detected cell ("mean" or "max").

        threshold_shape_det : int
            Threshold for shape-based cell detection.
        
        save_shape_det : bool
            If True, saves detected shapes.

        amount_processes : int
            Number of parallel processes to use in detection.

        size_maximum, size_minimum : int
            Maximum and minimum cell size thresholds.

        area_of_overlap : int
            Overlap area threshold for cell detection.

        Returns:
        --------
        None
            The function performs cell detection and saves results but does not return values.

        Notes:
        ------
        1. Adjusting the parameters optimizes detection for different types of cellular imaging data.
        2. Results are saved in workspace filenames according to the specified channel.
        """
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


        utils.cells.detect_cells(self.ws.filename(f"stitched_{self.chosen_channel}"),
                           self.ws.filename('cells', postfix=f"raw_{self.chosen_channel}"),
                           cell_detection_parameter=cell_detection_parameter,
                           processing_parameter=processing_parameter)


    def filter_cells(self, filt_size:int = 20) -> None:
        """
        Filters the detected cells based on size and intensity thresholds.

        This function applies a size-based filter to remove small or large cells from the detection results.
        The size threshold is defined by the `filt_size` parameter, which specifies the minimum cell size in pixels.
        It then passes the filtered data to the `filter_cells` function of the `utils.cells` module.

        Parameters:
        filt_size (int): The minimum size of the cells to retain, specified in pixels. Cells smaller than this size will be removed.
                        Default is 20.

        Returns:
        None: The function does not return any value. It directly saves the filtered results to the workspace.

        Notes:
        - This function expects the workspace (`self.ws`) to contain the raw cell detection data.
        - The output is saved as a filtered cell dataset in the workspace with a postfix of '_filtered_' and the current channel.
        """
        thresholds = {'source': None, 'size': (filt_size, None)}
        utils.cells.filter_cells(self.ws.filename('cells', postfix=f"raw_{self.chosen_channel}"),
                           self.ws.filename('cells', postfix=f"filtered_{self.chosen_channel}"),
                           thresholds=thresholds)


    def atlas_assignment(self, orientation_x:int = 3, orientation_y:int = 2, orientation_z:int = 1):
        """
        Performs cell annotation by transforming the cell coordinates and aligning them with a reference brain atlas.

        This function processes the cell data, applies transformations to the cell coordinates, and then annotates the 
        transformed coordinates by comparing them to a specified brain atlas. The resulting annotated data is saved in various formats,
        including as a numpy array, CSV file, and ClearMap1 format.

        The process involves several key steps:
        1. The function filters the cell data based on previously defined criteria.
        2. The cell coordinates are transformed through resampling and elastix-based transformations.
        3. The transformed coordinates are annotated by matching them to a brain atlas.
        4. The final annotated data is saved to the workspace and exported in different formats.

        Parameters:
        orientation_x (int): The x-axis orientation for the atlas (default is 3).
        orientation_y (int): The y-axis orientation for the atlas (default is 2).
        orientation_z (int): The z-axis orientation for the atlas (default is 1).

        Returns:
        None: The function does not return any value. It saves the annotated cell data to the workspace and exports it in CSV and ClearMap1 formats.

        Raises:
        - If no workspace is selected (`self.ws` is None), an alert message is shown to inform the user.

        Notes:
        - The transformation of coordinates involves resampling and elastix-based affine transformations.
        - The annotation file is selected based on the specified orientation and is used to map transformed coordinates to the brain atlas.
        - The function supports multiple export formats, including CSV for cell data and ClearMap1 format for 3D visualization tools.
        - The transformed cell data is stored in the workspace with the chosen channel as a postfix.
        """
        if self.ws == None:
            alert = utils.QMessageBox()
            alert.setText("You did not choose a workspace yet!")
            alert.exec()
            return
        # sink_maxima = self.ws.filename('cells_', postfix = 'raw_'+self.channel_chosen)
        source = self.ws.source('cells', postfix = f"raw_{self.chosen_channel}")
        #sink_raw = self.ws.source('cells', postfix='raw_' + self.chosen_channel)

        self.filter_cells()

        # Assignment of the cells with filtered maxima
        # Filtered cell maxima are used to execute the alignment to the atlas
        source = self.ws.source('cells', postfix=f"filtered_{self.chosen_channel}")

        # Didn't understand the functions so far. Seems like coordinates become transformed by each function and reassigned.
        #print("Transformation\n")


        def transformation(coordinates:utils.np.array):
            """
            Transforms the input coordinates through a series of resampling and elastix-based affine transformations.

            This function applies a series of transformations to the provided 3D coordinates. The coordinates are first resampled 
            to match the shape of a target image. Then, two successive elastix transformations are applied to map the coordinates 
            from the resampled space to an intermediate space and finally to a reference space. Additionally, it searches for 
            an appropriate brain atlas annotation file based on the specified orientation parameters.

            Parameters:
            coordinates (array-like): The 3D coordinates to be transformed, typically representing cell positions.
            permutation (tuple, optional): A tuple of three integers that defines the orientation of the atlas. 
                                            If not provided, defaults to `None`.

            Returns:
            tuple: A tuple containing:
                - Transformed coordinates (array-like): The coordinates after applying resampling and elastix transformations.
                - annotation_file (str): The file path to the corresponding brain atlas annotation file.

            Raises:
            - If no annotation file matching the pattern is found, `None` is returned for the annotation file.
            
            Notes:
            - The `coordinates` array is resampled to match the dimensions of the reference image and then transformed using elastix.
            - The annotation file search is based on a regex pattern that incorporates the specified `orientation_x`, `orientation_y`, 
            and `orientation_z` parameters.
            - The function assumes a directory structure where elastix transformation files and brain atlas files are stored.

            Example:
            >>> coordinates_transformed, annotation_file = transformation(coordinates, permutation=(3, 2, 1))
            """
            #print(coordinates)
            coordinates = utils.res.resample_points(coordinates,
                                              sink=None,
                                              orientation=None,
                                              resample_source=None,
                                              source_shape=utils.io.shape(self.ws.filename(f"stitched_{self.chosen_channel}")),
                                              sink_shape=utils.io.shape(self.ws.filename(f"resampled_{self.chosen_channel}")))
            #print(coordinates)
            coordinates = utils.elx.transform_points(coordinates,
                                               sink=None,
                                               transform_directory=f"{self.my_working_directory}/elastix_resampled_to_auto_{self.chosen_channel}",
                                               binary=True,
                                               indices=False)
            #print(coordinates)
            coordinates = utils.elx.transform_points(coordinates,
                                               sink=None,
                                               transform_directory=f"{self.my_working_directory}/elastix_auto_to_reference_{self.chosen_channel}",
                                               binary=True,
                                               indices=False)
            #print(coordinates)
            path_to_annotation_file = "./ClearMap2/ClearMap/Resources/Atlas/"
            annotation_file_regex = f"ABA_25um_annotation__{str(orientation_x)}_{str(orientation_y)}_{str(orientation_z)}__*.tif" 
            def find_annotation_file(directory:str, pattern:str):
                # Combines directory with the glob pattern
                matched_files = utils.glob.glob(utils.os.path.join(directory, pattern), recursive=False)
                return matched_files[0] if matched_files else None
            annotation_file = find_annotation_file(path_to_annotation_file,annotation_file_regex)
            #annotation_file = "/home/margaryta/ClearFinder/ClearMap/ClearMap2/ClearMap/Resources/Atlas/ABA_25um_annotation__-1_3_2__slice_None_None_None__slice_None_None_None__slice_None_None_None__.tif"
            return coordinates, annotation_file
            
        # These are the initial coordinates originating in the file cells_filtered.npy containing the coordinates of the filtered maxima.
        # Each coordinate of 3 dimensional space x,y,z  is written into a new numpy array. [[x1,y1,z1],[x2,y2,3],...,[x_last,y_last,z_last]]
        coordinates = utils.np.array([source[c] for c in 'xyz']).T
        
        margins = [0,0,0]
        array_of_files = utils.os.listdir(f"{self.my_working_directory}/Signal/{self.chosen_channel}")
        #print(array_of_files)
        margins[2] = len(array_of_files)
        first_signal_image = utils.imread(f"{self.my_working_directory}/Signal/{self.chosen_channel}/{array_of_files[0]}")
        margins[0] = first_signal_image.shape[1]
        margins[1] = first_signal_image.shape[2]
        #print(margins)
    
        # Coordinates become transformed by the above defined transformation function
        coordinates_transformed, annotation_file_transformed = transformation(coordinates)

        # Cell annotation
        # Transformed coordinates are used as input to annotate cells by comparing with brain atlas
        # Due to a future warning occured coordinates_transformed was converterted from array[seq] to arr[tuple(seq)] as coordinates_transformed_tuple
        coordinates_transformed_tuple = utils.np.array(tuple(coordinates_transformed))

        print("Label Point\n")
        label = utils.ano.label_points(points = coordinates_transformed,annotation_file = annotation_file_transformed, key='order')
        print("Convert labeled points\n")
        names = utils.ano.convert_label(label, key='order', value='name')

        # Save results
        coordinates_transformed.dtype = [(t, float) for t in ('xt', 'yt', 'zt')]
        nparray_label = utils.np.array(label, dtype=[('order', int)])
        nparray_names = utils.np.array(names, dtype=[('name', 'a256')])

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
        """
        Performs voxelization of the cell coordinates to generate a density map.

        This function processes the cell coordinates and intensity values, then voxelizes them to create a 3D density map
        based on the given cell data. The voxelization method uses a spherical kernel to assign values to a 3D grid, which 
        represents the spatial distribution and density of cells.

        The voxelization process involves the following steps:
        1. Preparation of annotation and reference files for spatial information.
        2. Extraction of cell coordinates and intensity values.
        3. Application of the voxelization algorithm, with specific parameters such as radius and method.
        4. Saving the resulting density map to the workspace.

        Parameters:
        None: This method does not take any arguments other than the instance itself.

        Returns:
        None: The function does not return any value. It directly saves the voxelized density map to the workspace.

        Notes:
        - The function requires the workspace (`self.ws`) to contain the cell coordinates and intensities data.
        - The voxelization process uses a spherical kernel with a default radius of (7, 7, 7) for the 3D grid.
        - The output is stored as a density map in the workspace with the postfix '_counts_' and the chosen channel name.
        - If no workspace is selected, the function will show an alert message.
        """
        if self.ws == None:
            alert = utils.QMessageBox()
            alert.setText("You did not choose a workspace yet!")
            alert.exec()
            return

        annotation_file, reference_file, distance_file = utils.ano.prepare_annotation_files(slicing=(slice(None),
                                                                                               slice(None),
                                                                                               slice(0, 256)),
                                                                                      orientation=(3, 2, 1),
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
                     sink=self.ws.filename('density', postfix=f"counts_{self.chosen_channel}"),
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

        # Orientation of the sample
        orientation_x = utils.QLineEdit("1")
        orientation_y = utils.QLineEdit("2")
        orientation_z = utils.QLineEdit("3")


        def save_config(save_path:str):
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


        def load_config(load_path:str):
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
        inner_layout8.addWidget(utils.QLabel("Orientation:"), 2, 0)
        inner_layout8.addWidget(utils.QLabel("X"), 2, 1)
        inner_layout8.addWidget(orientation_x, 2, 2)
        inner_layout8.addWidget(utils.QLabel("Y"), 2, 3)
        inner_layout8.addWidget(orientation_y, 2, 4)
        inner_layout8.addWidget(utils.QLabel("Z"), 2, 5)
        inner_layout8.addWidget(orientation_z, 2, 6)

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
            lambda: load_config(load_path = f"{utils.os.getcwd()}/cell_detection_{config_path.text()}.csv"))
        save_config_button.clicked.connect(
            lambda: save_config(save_path = f"{utils.os.getcwd()}/cell_detection_{config_path.text()}.csv"))
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

        atlas_assignment_button.clicked.connect(lambda: self.atlas_assignment(int(orientation_x.text()),int(orientation_y.text()),int(orientation_z.text())))
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
