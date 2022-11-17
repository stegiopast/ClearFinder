import utils

## Contains all features of the analysis and plots tab

class PlotWindow(utils.QDialog):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)

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

class AnalysisAndPlots:
    """Organization of the Analysis and Plots functionality"""
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

        PWindow = PlotWindow()

        self.input_csv = utils.pd.DataFrame()
        self.metadata_csv = utils.pd.DataFrame()
        self.information_csv = utils.pd.DataFrame()

        filter_level_ComboBox = utils.QComboBox()
        filter_level_ComboBox.insertItem(0,"None")
        for i in range(1, 13):
            filter_level_ComboBox.insertItem(i, str(i))

        filter_region_LineEdit = utils.QLineEdit("")

        filter_specific_region_LineEdit = utils.QLineEdit("")

        set_input = utils.QPushButton("Set input and metadata")

        #create_vol_plot = QPushButton("Volcano Plot")
        create_pca = utils.QPushButton("PCA")
        create_heatmap = utils.QPushButton("Heatmap")
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

        inner_layout6.addWidget(PWindow)

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

            PWindow.figure.clear()
            ax = PWindow.figure.add_subplot(111)
            hue_regplot(data=pc_df, x='PC1', y='PC2', hue='Condition', ax=ax)
            PWindow.canvas.draw()

        def heatmap():
            """Plot Heatmap"""
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

            utils.sns.heatmap(input_csv, yticklabels=regions, annot=False)
            utils.plt.title(brainregion)
            utils.plt.savefig(output_dir + output_name, bbox_inches='tight')
            utils.plt.close()

            PWindow.figure.clear()

            ax = PWindow.figure.add_subplot(111)

            utils.sns.heatmap(input_csv, yticklabels=regions, annot=False, ax = ax)
            utils.plt.close()

            PWindow.canvas.draw()


        def boxplot():
            input_csv = self.input_csv.copy()
            print(input_csv)
            # information = self.information_csv.copy()
            if filter_specific_region_LineEdit.text() != "":
                region = filter_specific_region_LineEdit.text()
                if region in input_csv.index:
                    input_csv = input_csv[input_csv.index == region]

                conditions = self.metadata_csv["condition"].unique()

                sample_names = list(input_csv.columns)
                for i in sample_names:
                    cpm_name = i + "_processed"
                    input_csv[cpm_name] = input_csv[i]

                # n³ !! danger danger
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
                            processed_list = list([str(l) + "_processed" for l in list(metadata_list_tmp["sample"])])
                            print(processed_list)
                            if input_csv.columns[k] in processed_list:
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

                PWindow.figure.clear()
                ax2 = PWindow.figure.add_subplot(111)
                utils.sns.boxplot(x="condition", y=method, data=df_boxplot,ax = ax2)
                utils.sns.swarmplot(x="condition", y=method, data=df_boxplot, color=".25", ax = ax2)
                PWindow.canvas.draw()
        return tab