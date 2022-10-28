import utils

class _Preanalysis_and_Normalization:

    def preanalysis_layout(self):
        tab = utils.QWidget()
        outer_layout = utils.QHBoxLayout()
        inner_layout1 = utils.QVBoxLayout()
        inner_layout2 = utils.QVBoxLayout()
        inner_layout3 = utils.QVBoxLayout()


        #Widgets for inner layout 1

        # Philipp: Is the add resultfile_button equivalent to the add analysis file ? if so maybe renam
        result_file_list = utils.QListWidget()
        add_resultfile_button = utils.QPushButton("Add analysis file")
        remove_resultfile_button = utils.QPushButton("Remove last file")
        final_output_directory = utils.QLineEdit("")
        create_final_output_directory = utils.QPushButton("Set output dir")
        make_analysis_data = utils.QPushButton("Create analysis data (absolute values)")


        #Widgets for inner Layout2
        choose_log_transformation_ComboBox = utils.QComboBox()
        choose_log_transformation_ComboBox.insertItem(0, "None")
        choose_log_transformation_ComboBox.insertItem(1, "log_10")
        choose_log_transformation_ComboBox.insertItem(2, "log_2")


        choose_normalization_ComboBox = utils.QComboBox()
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
        inner_layout2.addWidget(choose_normalization_ComboBox)

        inner_layout2.addWidget(utils.QLabel("Choose log transformation or None"))
        inner_layout2.addWidget(choose_log_transformation_ComboBox)



        #inner_layout2.addWidget(QLabel("                                          "))
        #inner_layout2.addWidget(QLabel("                                          "))
        #inner_layout2.addWidget(QLabel("Filter for level in hierarchical structure"))
        #inner_layout2.addWidget(filter_level_ComboBox)



        #inner_layout2.addWidget(QLabel("                                          "))
        #inner_layout2.addWidget(QLabel("                                          "))
        #inner_layout2.addWidget(QLabel("Filter for a region and it's subregions"))
        #inner_layout2.addWidget(filter_region_LineEdit)

        inner_layout2.addWidget(utils.QLabel("                                          "))
        inner_layout2.addWidget(utils.QLabel("                                          "))
        inner_layout2.addWidget(utils.QLabel("                                          "))
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

        # Wenn ich die classes layout und functions schreibe dann kann ich auf die functions nicht zugreifen  
        add_resultfile_button.pressed.connect(lambda: add_analysis_file())
        remove_resultfile_button.pressed.connect(lambda: remove_last_element())
        create_final_output_directory.pressed.connect(lambda: set_output_directory())
        make_analysis_data.pressed.connect(lambda: preprocess_analysis_data())
        filter_normalization_button.pressed.connect(lambda: logtransform_normalize_filter())
        save_metadata.pressed.connect(lambda: save_metadata())


        #Functions for preprocessing
        # want to add a class for the functions but there is a problem with inheritance from the layout class
        def add_analysis_file():
            path = utils.QFileDialog.getOpenFileName(self,"Choose embedded_ontology.csv of interest")
            if "ontology.csv" in str(path[0]):
                result_file_list.addItem(str(path[0]))
            else:
                alert = utils.QMessageBox()
                alert.setText("Please load an embedded_ontology.csv file !")
                alert.exec()
                return


        def remove_last_element():
            result_file_list.takeItem(result_file_list.count()-1)

        def set_output_directory():
            if utils.os.path.exists(final_output_directory.text()):
                pass
            else:
                try:
                    utils.os.makedirs(final_output_directory.text())
                except (ValueError,NameError):
                    alert = utils.QMessageBox()
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
            metadata_df = utils.pd.DataFrame(utils.np.array(metadata_list),columns = ["sample","condition"])
            metadata_df.to_csv(final_output_directory.text()+"/metadata.csv", sep = ";")
            print(metadata_list)



        def preprocess_analysis_data():
            files_to_analyse = [result_file_list.item(i).text() for i in range(result_file_list.count())]
            df_list = []
            print(files_to_analyse)
            for i in files_to_analyse:
                df_list.append(utils.pd.read_csv(i, header=0, sep=";"))

            new_df = utils.pd.DataFrame(df_list[0]["Region"])
            new_df2 = utils.pd.DataFrame(df_list[0]["Region"])
            new_df3 = utils.pd.DataFrame(df_list[0][["Region","TrackedWay","CorrespondingLevel"]])


            for i,val in enumerate(df_list):
                new_df[str(utils.os.path.basename(utils.os.path.dirname(files_to_analyse[i])))] = val["RegionCellCount"]

            for i,val in enumerate(df_list):
                new_df2[str(utils.os.path.basename(utils.os.path.dirname(files_to_analyse[i])))] = val["RegionCellCountSummedUp"]


            new_df.to_csv(final_output_directory.text() + "/absolute_counts.csv", sep=";",index=False)
            new_df2.to_csv(final_output_directory.text() + "/hierarchical_absolute_counts.csv",sep=";",index=False)
            new_df3.to_csv(final_output_directory.text() + "/list_information.csv", sep = ";", index=False)


        def logtransform_normalize_filter():
            if utils.os.path.exists(final_output_directory.text()):
                df_abs = utils.pd.read_csv(final_output_directory.text() + "/absolute_counts.csv", sep = ";", header = 0,index_col=0)
                df_hier_abs = utils.pd.read_csv(final_output_directory.text() + "/hierarchical_absolute_counts.csv", sep = ";",header = 0,index_col = 0)

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

                    df_abs = utils.np.log2(df_abs)
                    df_hier_abs = utils.np.log2(df_hier_abs)

                    df_abs_filename = "log2_" + df_abs_filename
                    df_hier_abs_filename = "log2_" + df_hier_abs_filename

                elif choose_log_transformation_ComboBox.currentText() == "log_10":
                    df_abs = utils.np.log10(df_abs)
                    df_hier_abs = utils.np.log10(df_hier_abs)

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
                alert = utils.QMessageBox()
                alert.setText("Directory input does not exist!\n Maike sure that the path to the new directory exists.")
                alert.exec()
                return
        return tab