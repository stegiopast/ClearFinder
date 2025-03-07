import utils


class Preanalysis_And_Normalization:
    """
    A class to handle pre-analysis and normalization steps for genomic or count-based data analysis. 
    It provides a GUI for users to perform the following tasks:
    1. Add and remove result files (such as analysis data in CSV format).
    2. Set the output directory for the processed files.
    3. Preprocess analysis data to create absolute and hierarchical counts.
    4. Apply normalization and log transformations to the data.
    5. Save metadata entered by the user into a CSV file.
    6. Filter and process data based on user selections for normalization methods and log transformations.

    The class contains several methods to manage the layout and interactions within the GUI:
    - `preanalysis_layout`: Initializes the GUI layout and connects widgets to the corresponding actions.
    - Various methods (`add_analysis_file`, `remove_last_element`, `set_output_directory`, etc.) to manage the data flow, perform analysis preprocessing, save metadata, and apply transformations.
    
    Attributes:
        result_file_list (utils.QListWidget): A list widget to display selected analysis files.
        final_output_directory (utils.QLineEdit): Input field to specify the output directory.
        choose_log_transformation_combobox (utils.QComboBox): Dropdown for selecting a log transformation method.
        choose_normalization_combobox (utils.QComboBox): Dropdown for selecting a normalization method.
        metadata_table (utils.QTableWidget): Table to input metadata for the analysis.
        save_metadata (utils.QPushButton): Button to save metadata to a CSV file.
    """
    def preanalysis_layout(self) -> utils.QWidget:
        """
        Creates and configures the main layout for preanalysis and normalization. The layout includes widgets for adding 
        result files, setting an output directory, performing analysis data preprocessing, log transformations, and 
        normalizing the data. It also provides functionality for saving metadata and filtering data.

        Returns:
            utils.QWidget: The QWidget containing the layout for preanalysis and normalization steps.
        """
        tab = utils.QWidget()
        outer_layout = utils.QHBoxLayout()
        inner_layout1 = utils.QVBoxLayout()
        inner_layout2 = utils.QVBoxLayout()
        inner_layout3 = utils.QVBoxLayout()

        #Widgets for inner layout 1
        result_file_list = utils.QListWidget()
        add_resultfile_button = utils.QPushButton("Add analysis file")
        remove_resultfile_button = utils.QPushButton("Remove last file")
        final_output_directory = utils.QLineEdit("")
        create_final_output_directory = utils.QPushButton("Set output dir")
        make_analysis_data = utils.QPushButton("Create analysis data (absolute values)")

        #Widgets for inner Layout2
        choose_log_transformation_combobox = utils.QComboBox()
        choose_log_transformation_combobox.insertItem(0, "None")
        choose_log_transformation_combobox.insertItem(1, "log_10")
        choose_log_transformation_combobox.insertItem(2, "log_2")

        # selecting ComboBox
        choose_normalization_combobox = utils.QComboBox()
        choose_normalization_combobox.insertItem(0,"None")
        choose_normalization_combobox.insertItem(1,"Counts per million")
        choose_normalization_combobox.insertItem(2,"Median of ratio")
        #choose_normalization_combobox.insertItem(3,"Percentile normalization (0.05,0.95)")

        filter_normalization_button = utils.QPushButton("Log Transform | Normalize | Filter ")

        #Widgets for inner Layout 3
        metadata_table = utils.QTableWidget(12,2)

        save_metadata = utils.QPushButton("Save Metadata")
        for i in range(metadata_table.rowCount()):
            for j in range(metadata_table.columnCount()):
                metadata_table.setCellWidget(i,j,utils.QLineEdit(""))

        metadata_table.setHorizontalHeaderLabels(["sample","condition"])

        inner_layout1.addWidget(utils.QLabel("<b>Pre-analysis steps</b>"))
        inner_layout1.addWidget(utils.QLabel("Input for count table:"))
        inner_layout1.addWidget(add_resultfile_button)
        inner_layout1.addWidget(remove_resultfile_button)
        inner_layout1.addWidget(result_file_list)
        inner_layout1.addWidget(utils.QLabel("Output directory for resulting files:"))
        inner_layout1.addWidget(final_output_directory)
        inner_layout1.addWidget(create_final_output_directory)
        inner_layout1.addWidget(make_analysis_data)

        inner_layout2.addWidget(utils.QLabel("<b>Normalization</b>"))
        inner_layout2.addWidget(utils.QLabel("Normalization"))
        inner_layout2.addWidget(choose_normalization_combobox)
        inner_layout2.addWidget(utils.QLabel("Choose log transformation or None"))
        inner_layout2.addWidget(choose_log_transformation_combobox)

        for _ in range(4):
            inner_layout2.addWidget(utils.QLabel("                                          "))
        inner_layout2.addWidget(filter_normalization_button)

        inner_layout3.addWidget(utils.QLabel("<b>Metadata</b>"))
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


        def add_analysis_file() -> None:
            """
            Opens a file dialog to choose an analysis file and adds it to the result file list. 
            If the selected file is not a valid ontology.csv file, it shows an error message.
            """
            path = utils.QFileDialog.getOpenFileName(self,"Choose embedded_ontology.csv of interest")
            if "ontology.csv" in str(path[0]):
                result_file_list.addItem(str(path[0]))
            else:
                alert = utils.QMessageBox()
                alert.setText("Please load an embedded_ontology.csv file !")
                alert.exec()
                return


        def remove_last_element() -> None:
            """
            Removes the last item from the result file list.
            """
            result_file_list.takeItem(result_file_list.count()-1)


        def set_output_directory() -> None:
            """
            Sets the output directory for resulting files. If the directory does not exist, it attempts to create it. 
            If the directory cannot be created, an error message is shown.
            """
            if utils.os.path.exists(final_output_directory.text()):
                pass
            else:
                try:
                    utils.os.makedirs(final_output_directory.text())
                except (ValueError,NameError,FileNotFoundError):
                    alert = utils.QMessageBox()
                    alert.setText("Directory is not creatable!\n Make sure the parent path to the new directory exists.")
                    alert.exec()
                    return


        def save_metadata() -> None:
            """
            Saves the metadata entered in the table to a CSV file in the final output directory. If metadata or output 
            directory is missing, an error message is shown.
            """
            metadata_list = []
            for i in range(metadata_table.rowCount()):
                if metadata_table.cellWidget(i,0).text() != ""  and metadata_table.cellWidget(i,1).text() != "":
                    metadata_list.append([metadata_table.cellWidget(i,j).text() for j in range(metadata_table.columnCount())])
                else:
                    pass
            if metadata_list == []:
                alert = utils.QMessageBox()
                alert.setText("Please insert metadata in table above.")
                alert.exec()
                return
            if final_output_directory.text() == "":
                alert = utils.QMessageBox()
                alert.setText("Please choose a final output directory to write the metadata.csv.")
                alert.exec()
                return

            metadata_df = utils.pd.DataFrame(utils.np.array(metadata_list),columns = ["sample","condition"])
            metadata_df.to_csv(f"{final_output_directory.text()}/metadata.csv", sep = ";")
            print(metadata_list)


        def preprocess_analysis_data() -> None:
            """
            Preprocesses the analysis data by loading the selected files and saving them into output CSV files. 
            If no files are selected, an error message is shown.
            """
            files_to_analyse = [result_file_list.item(i).text() for i in range(result_file_list.count())]
            df_list = []
            print(files_to_analyse)
            for i in files_to_analyse:
                df_list.append(utils.pd.read_csv(i, header=0, sep=";"))
            
            if df_list == []:
                alert = utils.QMessageBox()
                alert.setText("Please add analysis files!")
                alert.exec()
                return

            new_df = utils.pd.DataFrame(df_list[0]["Region"])
            new_df2 = utils.pd.DataFrame(df_list[0]["Region"])
            new_df3 = utils.pd.DataFrame(df_list[0][["Region","TrackedWay","CorrespondingLevel"]])

            for i,val in enumerate(df_list):
                file_base_name = str(utils.os.path.basename(utils.os.path.dirname(files_to_analyse[i])))
                new_df[file_base_name] = val["RegionCellCount"]
                new_df2[file_base_name] = val["RegionCellCountSummedUp"]

            if not utils.os.path.exists(final_output_directory.text()):
                alert = utils.QMessageBox()
                alert.setText("Please set output directory first.")
                alert.exec()
                return
            new_df.to_csv(f"{final_output_directory.text()}/absolute_counts.csv", sep=";",index=False)
            new_df2.to_csv(f"{final_output_directory.text()}/hierarchical_absolute_counts.csv",sep=";",index=False)
            new_df3.to_csv(f"{final_output_directory.text()}/list_information.csv", sep = ";", index=False)


        def logtransform_normalize_filter() -> None:
            """
            Applies normalization and log transformation on absolute count data, and saves the processed data 
            as CSV files in the specified output directory.

            This function performs the following steps:
            1. Loads the absolute counts data (both general and hierarchical) from CSV files located in the specified output directory.
            2. Normalizes the data based on the selected method from the combobox:
                - "Counts per million": Scales the data such that the sum of counts equals 1 million.
                - "Median of ratio": Normalizes the data by the median of row ratios across all samples.
            3. Applies a log transformation if selected:
                - "log_2": Transforms the data using a base-2 logarithm.
                - "log_10": Transforms the data using a base-10 logarithm.
            4. Saves the resulting data to new CSV files with modified filenames, based on the transformations applied.

            Input:
                - final_output_directory.text() (str): The directory path where the processed output files will be saved.
                - choose_normalization_combobox.currentText() (str): The normalization method selected by the user. Options:
                    - "None"
                    - "Counts per million"
                    - "Median of ratio"
                - choose_log_transformation_combobox.currentText() (str): The log transformation selected by the user. Options:
                    - "None"
                    - "log_2"
                    - "log_10"
                - "absolute_counts.csv" and "hierarchical_absolute_counts.csv" (CSV files): Input files containing absolute count data.

            Output:
                - Writes two processed CSV files to the output directory with filenames depending on the normalization and transformation applied. The files are:
                    - Normalized absolute counts file (e.g., "cpm_norm_absolute_counts.csv" or "mor_norm_absolute_counts.csv").
                    - Normalized hierarchical absolute counts file (e.g., "cpm_norm_hierarchical_absolute_counts.csv" or "mor_norm_hierarchical_absolute_counts.csv").
                    - If log transformation is applied, the filenames will be prefixed with "log2_" or "log10_" accordingly.
                    - The final filenames include the applied normalization and transformation methods.

            Raises:
                - QMessageBox: An alert will be shown if the output directory does not exist or the files cannot be read.
            """
            if utils.os.path.exists(final_output_directory.text()):
                df_abs = utils.pd.read_csv(f"{final_output_directory.text()}/absolute_counts.csv", sep = ";", header = 0,index_col=0)
                df_hier_abs = utils.pd.read_csv(f"{final_output_directory.text()}/hierarchical_absolute_counts.csv", sep = ";",header = 0,index_col = 0)

                df_abs_filename = "absolute_counts.csv"
                df_hier_abs_filename = "hierarchical_absolute_counts.csv"

                if choose_normalization_combobox.currentText() == "Counts per million":
                    print("Running counts per million normalization")

                    sum_df_abs = df_abs.sum()
                    df_abs = df_abs / sum_df_abs * 1000000
                    df_hier_abs = df_hier_abs / sum_df_abs * 1000000

                    df_abs_filename = f"cpm_norm_{df_abs_filename}"
                    df_hier_abs_filename = f"cpm_norm_{df_hier_abs_filename}"

                elif choose_normalization_combobox.currentText() == "Median of ratio":
                    print("Running Median of ratio normalization")

                    df_abs_rowmean = df_abs.mean(axis = 1)
                    df_hier_abs_rowmean = df_hier_abs.mean(axis = 1)

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


                    df_abs_filename = f"mor_norm_{df_abs_filename}"
                    df_hier_abs_filename = f"mor_norm_{df_hier_abs_filename}"

                if choose_log_transformation_combobox.currentText() == "log_2":
                    print("Running log2 transformation")

                    df_abs = utils.np.log2(df_abs)
                    df_hier_abs = utils.np.log2(df_hier_abs)

                    df_abs_filename = f"log2_{df_abs_filename}"
                    df_hier_abs_filename = f"log2_{df_hier_abs_filename}"

                elif choose_log_transformation_combobox.currentText() == "log_10":
                    df_abs = utils.np.log10(df_abs)
                    df_hier_abs = utils.np.log10(df_hier_abs)

                    df_abs_filename = f"log10_{df_abs_filename}"
                    df_hier_abs_filename = f"log10_{df_hier_abs_filename}"

                df_abs.to_csv(f"{final_output_directory.text()}/{df_abs_filename}", sep = ";")
                df_hier_abs.to_csv(f"{final_output_directory.text()}/{df_hier_abs_filename}", sep = ";")
            else:
                alert = utils.QMessageBox()
                alert.setText("Directory input does not exist!\n Make sure that the path to the new directory exists.")
                alert.exec()
                return
        return tab