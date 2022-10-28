import utils

class Plot_Window(utils.QDialog):

    # constructor
    def __init__(self, parent=None):
        super(Plot_Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = utils.plt.figure()

        # this is the Canvas Widget that
        # displays the 'figure'it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = utils.FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = utils.NavigationToolbar(self.canvas, self)

        # Just some button connected to 'plot' method
        # self.button = QPushButton('Plot')

        # adding action to the button
        # self.button.clicked.connect(self.plot)

        # creating a Vertical Box layout
        layout = utils.QVBoxLayout()

        # adding tool bar to the layout
        layout.addWidget(self.toolbar)

        # adding canvas to the layout
        layout.addWidget(self.canvas)

        # adding push button to the layout
        #layout.addWidget(self.button)

        # setting layout to the main window
        self.setLayout(layout)


class _Analysis_and_Plots_Layout:

    def analysis_layout(self):

        tab = utils.QWidget()

        outer_layout = utils.QVBoxLayout()

        inner_layout = utils.QGridLayout()

        intermediate_layout = utils.QHBoxLayout()
        inner_layout2 = utils.QVBoxLayout()
        inner_layout3 = utils.QVBoxLayout()
        inner_layout4 = utils.QVBoxLayout()
        inner_layout5 = utils.QVBoxLayout()
        inner_layout6 = utils.QHBoxLayout()

        input_file = utils.QLineEdit("")
        choose_input_file = utils.QPushButton("Choose input file")

        input_information_file = utils.QLineEdit("")
        choose_information_file = utils.QPushButton("Choose List information file (information.csv)")

        metadata_file = utils.QLineEdit("")
        choose_metadata_file = utils.QPushButton("Choose metadata file")


        plot_window = utils.Plot_Window()


        self.input_csv = utils.pd.DataFrame()
        self.metadata_csv = utils.pd.DataFrame()
        self.information_csv = utils.pd.DataFrame()

        filter_level_ComboBox = utils.QComboBox()
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

        filter_region_LineEdit = utils.QLineEdit("")

        filter_specific_region_LineEdit = utils.QLineEdit("")

        set_input = utils.QPushButton("Set input and metadata")

        create_pca = utils.QPushButton("PCA")
        create_heatmap = utils.QPushButton("Heatmap")
        #create_vol_plot = QPushButton("Volcano Plot")
        create_boxplot = utils.QPushButton("Boxplot")


        inner_layout.addWidget(utils.QLabel("<b>Input file</b>"),0,0)
        inner_layout.addWidget(input_file,0,1)
        inner_layout.addWidget(choose_input_file,0,2)

        inner_layout.addWidget(utils.QLabel("<b>Metadata file</b>"),1,0)
        inner_layout.addWidget(metadata_file,1,1)
        inner_layout.addWidget(choose_metadata_file,1,2)

        inner_layout.addWidget(utils.QLabel("<b>Information file</b>"),2,0)
        inner_layout.addWidget(input_information_file,2,1)
        inner_layout.addWidget(choose_information_file,2,2)

        inner_layout.addWidget(set_input,3,0)

        inner_layout2.addWidget(utils.QLabel("<b>PCA</b>"))
        inner_layout2.addWidget(create_pca)
        inner_layout2.addStretch()

        #inner_layout3.addWidget(QLabel("<b>Volcano Plot</b>"))
        #inner_layout3.addWidget(create_vol_plot)
        #inner_layout3.addStretch()

        inner_layout4.addWidget(utils.QLabel("<b>Heatmap</b>"))
        inner_layout4.addWidget(utils.QLabel("Select a structure level to filter for"))
        inner_layout4.addWidget(filter_level_ComboBox)
        inner_layout4.addWidget(utils.QLabel("Name a region to filter for ist subregions"))
        inner_layout4.addWidget(filter_region_LineEdit)
        inner_layout4.addWidget(create_heatmap)
        inner_layout4.addStretch()

        inner_layout5.addWidget(utils.QLabel("<b>Boxplot</b>"))
        inner_layout5.addWidget(utils.QLabel("Please name specific region"))
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
            path = utils.QFileDialog.getOpenFileName(self,"Choose input file of interest")
            input_file.setText(path[0])

        def select_metadata_file():
            path = utils.QFileDialog.getOpenFileName(self,"Choose metadata file of interest")
            metadata_file.setText(path[0])

        def select_information_file():
            path = utils.QFileDialog.getOpenFileName(self,"Choose metadata file of interest")
            input_information_file.setText(path[0])

        def set_input_and_metadata():
            self.input_csv = utils.pd.read_csv(input_file.text(),sep=";",header = 0,index_col = 0)
            self.metadata_csv = utils.pd.read_csv(metadata_file.text(),sep=";",header = 0,index_col = 0)
            self.information_csv = utils.pd.read_csv(input_information_file.text(),sep=";",header=0, index_col=0)
            print(self.input_csv)
            print(self.metadata_csv)
            print(self.information_csv)

        def pca():

            input_csv = self.input_csv.copy()
            input_csv = input_csv.reset_index(drop = True)
            input_csv = input_csv.loc[:,input_csv.columns != "Region"]
            input_csv = input_csv.dropna()
            input_csv = input_csv[utils.np.isfinite(input_csv).all(1)]
            print(input_csv)


            sample_names = list(input_csv.columns)
            input_csv = utils.np.array(input_csv.transpose())
            print(input_csv)


            metadata_csv = self.metadata_csv.copy()
            print(sample_names)

            output_dir = utils.os.path.dirname(input_file.text())
            output_name = "/PCA_" + utils.os.path.basename(input_file.text())[:-4] + ".png"

            pca = utils.decomposition.PCA(n_components=2)

            pc = pca.fit_transform(input_csv)
            pc_df = utils.pd.DataFrame(data = pc , columns = ['PC1', 'PC2'])
            print(pc_df)
            pc_df["Cluster"] = sample_names

            print(pc_df)

            condition_array = []

            for i in pc_df["Cluster"]:
                for j,val in enumerate(metadata_csv["sample"]):
                    if str(i) == str(val):
                        condition_array.append(list(metadata_csv["condition"])[j])
            pc_df["Condition"] = condition_array

            var_df = utils.pd.DataFrame({'var':pca.explained_variance_ratio_, 'PC':['PC1','PC2']})
            fig = utils.sns.lmplot( x="PC1", y="PC2",data=pc_df,fit_reg=False,hue='Condition',legend=True,scatter_kws={"s": 80})

            for i,txt in enumerate(pc_df["Cluster"]):
                utils.plt.annotate(txt,(list(pc_df["PC1"])[i],list(pc_df["PC2"])[i]), ha = "center", va = "bottom")

            utils.plt.savefig(output_dir + output_name)
            utils.plt.close()

            def hue_regplot(data, x, y, hue, palette=None, **kwargs):
                from matplotlib.cm import get_cmap

                regplots = []

                levels = data[hue].unique()

                if palette is None:
                    default_colors = get_cmap('tab10')
                    palette = {k: default_colors(i) for i, k in enumerate(levels)}

                for key in levels:
                    regplots.append(
                        utils.sns.regplot(
                            x=x,
                            y=y,
                            data=data[data[hue] == key],
                            color=palette[key],
                            **kwargs
                        )
                    )

                for i,txt in enumerate(data["Cluster"]):
                    utils.plt.annotate(txt,(list(data["PC1"])[i],list(data["PC2"])[i]), ha = "center", va = "bottom")

                return regplots

            plot_window.figure.clear()
            ax = plot_window.figure.add_subplot(111)
            hue_regplot(data=pc_df, x='PC1', y='PC2', hue='Condition', ax=ax)
            plot_window.canvas.draw()






        #def volcano():
        #    pass
        def heatmap():
            input_csv = self.input_csv.copy()
            print(input_csv.head())
            information = self.information_csv.copy()
            # while ClearMap runs ()
            # if filter region is
            #if input_csv.empty:
            #    input_csv = self.input_csv()

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
                    alert = utils.QMessageBox()
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

            print("afterwards \n", input_csv.head(), "\n")

            brainregion = brainregion + "_heatmap"


            if input_csv.empty:
                alert = utils.QMessageBox()
                alert.setText("After filtering the region the dataframe it is empty! - Try other filters")
                alert.exec()
                return


            input_csv = input_csv.dropna()
            input_csv = input_csv.loc[:,input_csv.columns != "Region"]
            input_csv = input_csv[utils.np.isfinite(input_csv).all(1)]
            input_csv = input_csv.loc[(input_csv!=0).any(axis=1)]

            regions = input_csv.index.to_numpy()
            input_csv = input_csv.reset_index(drop = True)

            output_dir = utils.os.path.dirname(input_file.text())
            output_name = "/" + brainregion + "_" + utils.os.path.basename(input_file.text())[:-4] + ".png"

            #if (input_csv.loc[(input_csv != 0).any(axis = 1)].size() < 1):
            if utils.np.all(input_csv == 0):
                alert = utils.QMessageBox()
                alert.setText("After filtering the region the dataframe only contains 0! - Try other filters")
                alert.exec()
                return
            else:

                print(input_csv)
                utils.sns.heatmap(input_csv, yticklabels=regions, annot=False)
                utils.plt.title(brainregion)
                utils.plt.savefig(output_dir + output_name, bbox_inches='tight')
                utils.plt.close()

                plot_window.figure.clear()

                ax = plot_window.figure.add_subplot(111)

                utils.sns.heatmap(input_csv, yticklabels=regions, annot=False, ax = ax)
                utils.plt.close()


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
                            mean = utils.np.mean(array_of_cpms)
                            stdd = utils.np.std(array_of_cpms)
                            med = utils.np.median(array_of_cpms)
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

                    data = utils.np.concatenate(spread)
                    array_for_boxplots.append(data)
                print("Array for boxplots\n",array_for_boxplots)

                df_boxplot = utils.pd.DataFrame()

                for val, i in enumerate(conditions):
                    method = "absolute"
                    region_name = region
                    df_tmp = utils.pd.DataFrame({method: array_for_boxplots[val]})
                    df_tmp["condition"] = i
                    df_boxplot = utils.pd.concat([df_boxplot, df_tmp])
                    fig, ax = utils.plt.subplots()
                    ax = utils.sns.boxplot(x="condition", y=method, data=df_boxplot)
                    ax = utils.sns.swarmplot(x="condition", y=method, data=df_boxplot, color=".25")

                    region_name = str(region_name).replace(" ", "")
                    region_name = str(region_name).replace("/", "")
                    utils.plt.title(region)

                output_dir = utils.os.path.dirname(input_file.text())
                output_name = "/" + region + "_boxplot_" + utils.os.path.basename(input_file.text())[:-4] + ".png"
                utils.plt.savefig( output_dir + output_name, bbox_inches='tight')
                utils.plt.close

                plot_window.figure.clear()
                ax2 = plot_window.figure.add_subplot(111)
                utils.sns.boxplot(x="condition", y=method, data=df_boxplot,ax = ax2)
                utils.sns.swarmplot(x="condition", y=method, data=df_boxplot, color=".25", ax = ax2)
                plot_window.canvas.draw()

        return tab

    def createHeatmap(path2file: str):
        dataframe = utils.pd.read_csv(path2file, header=0, sep=";")
        dataframe = dataframe.iloc[:, 1:]
        if not utils.os.path.exists(utils.result_dir.text() + "/AnalysisOutput"):
            utils.os.makedirs(utils.result_dir.text() + "/AnalysisOutput")

        if not utils.result_dir.text():
            alert = utils.QMessageBox()
            alert.setText("Please load a existing directory!")
            alert.exec()
            return

        if utils.brainregion.text():
            print("Filtering Region")
            dataframe = utils.filterDatasetByRegion(dataframe, utils.brainregion.text())

        if dataframe.empty:
            alert = utils.QMessageBox()
            alert.setText("After filtering the region the dataframe it is empty! - Try other filters")
            alert.exec()
            return

        if utils.struc_level.text():
            print("Filtering Level")
            dataframe = utils.filterDatasetByLevel(dataframe, int(utils.struc_level.text()))

        if dataframe.empty:
            alert = utils.QMessageBox()
            alert.setText("After filtering the level the dataframe it is empty! - Try other filters")
            alert.exec()
            return

        regions = dataframe["Region"].to_numpy()

        if utils.CountsOrSummedCounts.currentText() == "Raw_Counts":
            startindex = 3
            endindex = 3 + int((dataframe.shape[1] - 3) / 2)

        elif utils.CountsOrSummedCounts.currentText() == "Summed_Counts":
            startindex = 3 + int((dataframe.shape[1] - 3) / 2)
            endindex = dataframe.shape[1]

        utils.sns.heatmap(dataframe.iloc[:, startindex:endindex], yticklabels=regions, annot=False)
        utils.plt.title(utils.brainregion.text())
        utils.plt.savefig(utils.result_dir.text() + "/AnalysisOutput/"+ utils.brainregion.text()+"_"+ utils.CountsOrSummedCounts.currentText()+"_Lv"+ utils.struc_level.text()+".png", bbox_inches='tight')
        utils.plt.clf()
        print("FERTIG!")

    def createHeatmapZScores(path2file: str):
        df = utils.pd.read_csv(path2file, header=0, sep=";")
        df = df.iloc[:, 1:]
        if not utils.os.path.exists(utils.result_dir.text() + "/AnalysisOutput"):
            utils.os.makedirs(utils.result_dir.text() + "/AnalysisOutput")

        if not utils.result_dir.text():
            alert = utils.QMessageBox()
            alert.setText("Please load a existing directory!")
            alert.exec()
            return

        if not utils.struc_level.text() and not utils.brainregion.text():
            alert = utils.QMessageBox()
            alert.setText("No filter was entered, are you sure to continue without a filter?")  # Make Yes/No Dialog
            alert.exec()

        if utils.brainregion.text():
            print("Filtering Region")
            df = utils.filterDatasetByRegion(df, utils.brainregion.text())

        if df.empty:
            alert = utils.QMessageBox()
            alert.setText("After filtering the region the dataframe it is empty! - Try other filters")
            alert.exec()
            return

        if utils.struc_level.text():
            print("Filtering Level")
            df = utils.filterDatasetByLevel(df, int(utils.struc_level.text()))

        if df.empty:
            alert = utils.QMessageBox()
            alert.setText("After filtering the level the dataframe it is empty! - Try other filters")
            alert.exec()
            return

        regions = df["Region"].to_numpy()

        if utils.CountsOrSummedCounts.currentText() == "Raw_Counts":
            startindex = 3
            endindex = 3 + int((df.shape[1] - 3) / 2)

        elif utils.CountsOrSummedCounts.currentText() == "Summed_Counts":
            startindex = 3 + int((df.shape[1] - 3) / 2)
            endindex = df.shape[1]

        mean = utils.pd.DataFrame(df.iloc[:, startindex:endindex].mean(axis=1))
        stdd = utils.pd.DataFrame(df.iloc[:, startindex:endindex].std(axis=1))
        
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

        utils.sns.heatmap(df.iloc[:, startindex:endindex], yticklabels=regions, annot=False)
        utils.plt.title(utils.brainregion.text())
        utils.plt.savefig(utils.result_dir.text() + "/AnalysisOutput/"+ utils.brainregion.text()+"_ZScore_"+ utils.CountsOrSummedCounts.currentText()+"_Lv"+ utils.struc_level.text()+".png", bbox_inches='tight')
        utils.plt.clf()

        return

    def createBoxplot(path2file: str):
        dataframe = utils.pd.read_csv(path2file, header=0, sep=";")
        dataframe = dataframe.iloc[:, 1:]

        if utils.CountsOrSummedCounts.currentText() == "Raw_Counts":
            startindex = 3
            endindex = 3 + int((dataframe.shape[1] - 3) / 2)

        elif utils.CountsOrSummedCounts.currentText() == "Summed_Counts":
            startindex = 3 + int((dataframe.shape[1] - 3) / 2)
            endindex = dataframe.shape[1]

        sample_names = list(dataframe.iloc[:, startindex:endindex].columns)
        metadata_list = utils.pd.read_csv(utils.result_dir.text()+"/metadata.csv", header=0, sep=";") # :Metadata
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
                mean = utils.np.mean(array_of_cpms)
                stdd = utils.np.std(array_of_cpms)
                med = utils.np.median(array_of_cpms)
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

        desired_region = utils.brainregion.text()
        chosen_data = dataframe[dataframe["Region"] == desired_region]

        array_for_boxplots = []

        for i in conditions:
            spread = list(chosen_data[str(i) + "_single_values"])

            data = utils.np.concatenate(spread)
            array_for_boxplots.append(data)

        df_boxplot = utils.pd.DataFrame()
        for val, i in enumerate(conditions):
            method = "absolute"
            region_name = utils.brainregion.text()
            df_tmp = utils.pd.DataFrame({method: array_for_boxplots[val]})
            df_tmp["condition"] = i
            df_boxplot = utils.pd.concat([df_boxplot, df_tmp])
            fig, ax = utils.plt.subplots()
            ax = utils.sns.boxplot(x="condition", y=method, data=df_boxplot)
            ax = utils.sns.swarmplot(x="condition", y=method, data=df_boxplot, color=".25")
            region_name = str(region_name).replace(" ", "")
            region_name = str(region_name).replace("/", "")
            utils.plt.title(utils.brainregion.text())
        utils.plt.savefig(utils.result_dir.text() + "/AnalysisOutput/"+ utils.brainregion.text()+"_BoxPlot_"+ utils.CountsOrSummedCounts.currentText()+"_Lv"+ utils.struc_level.text()+".png", bbox_inches='tight')


    def createVolcanoPlot(path2file: str):
        dataframe = utils.pd.read_csv(path2file, header=0, sep=";")
        dataframe = dataframe.iloc[:, 1:]
        index = 3 + ((dataframe.shape[1] - 3) / 2)
        sample_names = list(dataframe.iloc[:, 3:int(index)].columns)
        print(sample_names)
        metadata_list = utils.pd.read_csv(utils.result_dir.text()+"/metadata.csv", header=0, sep=";")

        analysis_folders = utils.getFilenames(utils.result_dir.text())
        doi = utils.pd.read_csv(analysis_folders[0], header=0, sep=";")

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
        z_score = utils.np.array(dataframe["Change_z_score"])
        p_values = utils.scipy.stats.norm.sf(abs(z_score))
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

        fig, ax = utils.plt.subplots()
        ax.scatter(utils.np.log2(dataframe["Change"]), -utils.np.log10(dataframe["Change_pvalue"]),
                    c=dataframe["Change_pvalue_significant"],
                    cmap="jet")

        x = list(utils.np.log2(dataframe["Change"]))
        y = list(-utils.np.log10(dataframe["Change_pvalue"])) # there was a "-" Symbol at the front of np.

        regions = []
        for val, j in enumerate(list(dataframe["Region"])):
            if list(dataframe["to_label"])[val]:
                regions.append(j)
                # print(j)
            else:
                regions.append("")

        for i, txt in enumerate(regions):
            ax.annotate(txt, (x[i], y[i]), ha="center", va="bottom", size="6")

        utils.plt.xlim((-3, 3))
        utils.plt.title() 
        utils.plt.show()

        return