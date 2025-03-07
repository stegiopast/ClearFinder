import utils

# Contains all features of the analysis and plots tab

class PlotWindow(utils.QDialog):
    """
    A dialog window that integrates Matplotlib figure and a navigation toolbar
    for interactive plotting.

    This class creates a simple user interface to display and interact with
    a Matplotlib plot. It includes a canvas to render the plot and a navigation
    toolbar for basic plot interaction such as zooming and panning.

    Attributes:
        figure (matplotlib.figure.Figure): The Matplotlib figure instance that 
            will be used for plotting.
        canvas (FigureCanvas): A widget that displays the Matplotlib figure.
        toolbar (NavigationToolbar): A toolbar for interacting with the plot.
        layout (QVBoxLayout): A vertical layout to organize the toolbar, canvas, 
            and other UI elements.

    Methods:
        __init__(self, parent=None):
            Initializes the PlotWindow with a Matplotlib figure, a canvas, a 
            navigation toolbar, and a layout.
    """
    def __init__(self, parent=None):
        """
        Initializes a PlotWindow instance, setting up the Matplotlib figure, canvas, 
        and toolbar, and arranges them in a vertical layout.

        This method sets up the GUI components necessary for displaying a Matplotlib 
        plot in a dialog window. It creates a Matplotlib figure, attaches it to a 
        canvas widget for rendering, adds a navigation toolbar for plot interaction, 
        and arranges these components in a vertical layout.

        Args:
            parent (QWidget, optional): The parent widget for the dialog window. 
                Defaults to None.

        Attributes:
            figure (matplotlib.figure.Figure): The Matplotlib figure instance used 
                for plotting.
            canvas (FigureCanvas): The widget used to render the Matplotlib figure.
            toolbar (NavigationToolbar): The toolbar for interacting with the plot 
                (e.g., zooming, panning).
            layout (QVBoxLayout): The layout used to organize the widgets within the 
                dialog window, including the toolbar and canvas.
        """
        super(PlotWindow, self).__init__(parent)
        self.figure = utils.plt.figure()
        self.canvas = utils.FigureCanvas(self.figure)
        self.toolbar = utils.NavigationToolbar(self.canvas, self)
        layout = utils.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

class Analysis_And_Plots_Layout:
    """
    Class for organizing and managing the layout of the Analysis and Plots functionality.

    This class manages the creation of the layout for user inputs, file selections,
    and plot generation. It provides widgets for input file selection, filter 
    settings, and buttons for generating various plots (e.g., PCA, heatmap, boxplot).

    Methods:
        analysis_layout(self):
            Creates and arranges the layout for the Analysis and Plots functionality,
            including input fields, buttons for plot generation, and the ontology table.
    """
    def analysis_layout(self):
        """
        Creates and arranges the layout for the analysis and plot features, including:
        - File selection for input, metadata, and information files.
        - Dropdowns and line edits for filtering data.
        - Buttons for generating plots (e.g., PCA, heatmap, boxplot).
        - Embeds a PlotWindow instance to display generated plots.

        The layout also includes an ontology table that provides an overview of 
        selected brain regions and structure levels.

        Returns:
            QWidget: The QWidget containing the entire analysis and plot layout.
        """
        tab = utils.QWidget()

        outer_layout_hor = utils.QHBoxLayout()
        outer_layout = utils.QVBoxLayout()
        outer_layout2 = utils.QVBoxLayout()
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


        def ontology_mouse_overview():
            """
            Creates an overview of the ontology data for the user to select a specific
            region and structure level.

            Reads the ontology data from a CSV file, sorts it by structure level and 
            region name, and returns the relevant subset for display.

            Returns:
                pd.DataFrame: A sorted DataFrame containing the 'st_level' and 'name' 
                columns from the ontology data.
            """
            df_selected_table = utils.pd.read_csv("./ontology_mouse.csv", sep=";",header=0)
            selected_columns = ["st_level", "name"]
            df_selected_table = df_selected_table[selected_columns]
            print(df_selected_table[selected_columns])

            # first sorting the st_levels and afterwards the region names alphabeticaly
            selected_and_sorted_table = df_selected_table.sort_values(["st_level", "name"],ascending=[True, True])
            print(selected_and_sorted_table)
            return selected_and_sorted_table
            


        ontology_table = ontology_mouse_overview()
        ontology_headers = list(ontology_table)
        ontology_mouse_table = utils.QTableWidget()
        ontology_mouse_table.setRowCount(ontology_table.shape[0])
        ontology_mouse_table.setColumnCount(ontology_table.shape[1])
        ontology_mouse_table.setHorizontalHeaderLabels(ontology_headers)

        ontology_table_array = ontology_table.values
        for row in range(ontology_table.shape[0]):
            for col in range(ontology_table.shape[1]):
                ontology_mouse_table.setItem(row, col, utils.QTableWidgetItem(str(ontology_table_array[row,col]))) 

        plot_window = PlotWindow()

        self.input_csv = utils.pd.DataFrame()
        self.metadata_csv = utils.pd.DataFrame()
        self.information_csv = utils.pd.DataFrame()

        filter_level_combobox = utils.QComboBox()
        filter_level_combobox.insertItem(0, "None")
        for i in range(1, 13):
            filter_level_combobox.insertItem(i, str(i))

        filter_region_lineedit = utils.QLineEdit("")

        filter_specific_region_lineedit = utils.QLineEdit("")

        set_input = utils.QPushButton("Set input and metadata")

        #create_vol_plot = QPushButton("Volcano Plot")
        create_pca = utils.QPushButton("PCA")
        create_heatmap = utils.QPushButton("Heatmap")
        create_boxplot = utils.QPushButton("Boxplot")

        inner_layout.addWidget(utils.QLabel("<b>Input file</b>"), 0, 0)
        inner_layout.addWidget(input_file, 0, 1)
        inner_layout.addWidget(choose_input_file, 0, 2)
        inner_layout.addWidget(utils.QLabel("<b>Metadata file</b>"), 1, 0)
        inner_layout.addWidget(metadata_file,1,1)
        inner_layout.addWidget(choose_metadata_file, 1, 2)
        inner_layout.addWidget(utils.QLabel("<b>Information file</b>"), 2, 0)
        inner_layout.addWidget(input_information_file, 2, 1)
        inner_layout.addWidget(choose_information_file, 2, 2)
        inner_layout.addWidget(set_input, 3, 0)



        inner_layout2.addWidget(utils.QLabel("<b>PCA</b>"))
        inner_layout2.addWidget(create_pca)
        inner_layout2.addStretch()
        #inner_layout3.addWidget(QLabel("<b>Volcano Plot</b>"))
        #inner_layout3.addWidget(create_vol_plot)
        #inner_layout3.addStretch()

        inner_layout4.addWidget(utils.QLabel("<b>Heatmap</b>"))
        inner_layout4.addWidget(utils.QLabel("Select a structure level to filter for"))
        inner_layout4.addWidget(filter_level_combobox)
        inner_layout4.addWidget(utils.QLabel("Name a region to filter for its subregions"))
        inner_layout4.addWidget(filter_region_lineedit)
        inner_layout4.addWidget(create_heatmap)
        inner_layout4.addStretch()

       

        inner_layout5.addWidget(utils.QLabel("<b>Boxplot</b>"))
        inner_layout5.addWidget(utils.QLabel("Please name specific region"))
        inner_layout5.addWidget(filter_specific_region_lineedit)
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

        
        outer_layout2.addWidget(utils.QLabel("<b>Ontology Mouse Overview"))
        outer_layout2.addWidget(ontology_mouse_table)
        
        outer_layout_hor.addLayout(outer_layout)
        outer_layout_hor.addLayout(outer_layout2)
        
        tab.setLayout(outer_layout_hor)

        choose_input_file.pressed.connect(lambda: select_input_file())
        choose_metadata_file.pressed.connect(lambda: select_metadata_file())
        choose_information_file.pressed.connect(lambda: select_information_file())
        create_pca.pressed.connect(lambda: pca())
        create_heatmap.pressed.connect(lambda:heatmap())
        create_boxplot.pressed.connect(lambda:boxplot())
        set_input.pressed.connect(lambda: set_input_and_metadata())

        def select_input_file():
            """
            Opens a file dialog to allow the user to select an input file.

            Sets the selected file path to the input file line edit widget.
            """
            path = utils.QFileDialog.getOpenFileName(self, "Choose input file of interest")
            input_file.setText(path[0])

        def select_metadata_file():
            """
            Opens a file dialog to allow the user to select a metadata file.

            Sets the selected file path to the metadata file line edit widget.
            """
            path = utils.QFileDialog.getOpenFileName(self, "Choose metadata file of interest")
            metadata_file.setText(path[0])

        def select_information_file():
            """
            Opens a file dialog to allow the user to select an information file.

            Sets the selected file path to the information file line edit widget.
            """
            path = utils.QFileDialog.getOpenFileName(self, "Choose metadata file of interest")
            input_information_file.setText(path[0])

        def set_input_and_metadata():
            """
            Sets the input, metadata, and information files by reading the paths 
            from the line edit widgets. If any of the files do not exist, an alert 
            message is shown.

            Reads the content of the files into Pandas DataFrames and stores them 
            in instance variables for further analysis.
            """
            if utils.os.path.exists(input_file.text()) and utils.os.path.exists(metadata_file.text()) and utils.os.path.exists(input_information_file.text()):
                self.input_csv = utils.pd.read_csv(input_file.text(), sep=";", header = 0, index_col = 0)
                self.metadata_csv = utils.pd.read_csv(metadata_file.text(), sep=";", header = 0, index_col = 0)
                self.information_csv = utils.pd.read_csv(input_information_file.text(), sep=";", header=0, index_col=0)
                print(self.input_csv)
                print(self.metadata_csv)
                print(self.information_csv)
            else:
                alert = utils.QMessageBox()
                alert.setText("Some of the input files do not exist!")
                alert.exec()
                return

        def pca():
            """
            Generates a PCA plot based on the provided input data, metadata, and information.

            This function performs PCA on the input data, visualizes the results in
            a scatter plot with points colored by condition, and updates the PlotWindow 
            with the generated plot.
            """
            if self.input_csv.empty or self.metadata_csv.empty or self.information_csv.empty:
                alert = utils.QMessageBox()
                alert.setText("Some of the input files do not exist!")
                alert.exec()
                return
            input_csv = self.input_csv.copy()
            input_csv = input_csv.reset_index(drop = True)
            input_csv = input_csv.loc[:,input_csv.columns != "Region"]
            input_csv = input_csv.dropna()
            input_csv = input_csv[utils.np.isfinite(input_csv).all(1)]

            sample_names = list(input_csv.columns)
            input_csv = utils.np.array(input_csv.transpose())

            metadata_csv = self.metadata_csv.copy()

            output_dir = utils.os.path.dirname(input_file.text())
            output_name = f"/PCA_{utils.os.path.basename(input_file.text())[:-4]}.png"

            pca = utils.decomposition.PCA(n_components=2)
            pc = pca.fit_transform(input_csv)
            pc_df = utils.pd.DataFrame(data = pc , columns = ['PC1', 'PC2'])
            pc_df["Cluster"] = sample_names

            condition_array = []

            for i in pc_df["Cluster"]:
                for j,val in enumerate(metadata_csv["sample"]):
                    if str(i) == str(val):
                        condition_array.append(list(metadata_csv["condition"])[j])
            pc_df["Condition"] = condition_array

            var_df = utils.pd.DataFrame({'var':pca.explained_variance_ratio_, 'PC':['PC1', 'PC2']})
            #fig = utils.sns.lmplot( x="PC1", y="PC2",data=pc_df,fit_reg=False, hue='Condition', legend=True,scatter_kws={"s": 80})
            fig = utils.sns.scatterplot(data=pc_df,x="PC1", y="PC2",fit_reg=False, hue='Condition', legend=True,s=80)

            for i,txt in enumerate(pc_df["Cluster"]):
                utils.plt.annotate(txt, (list(pc_df["PC1"])[i], list(pc_df["PC2"])[i]), ha = "center", va = "bottom")

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
                    utils.plt.annotate(txt, (list(data["PC1"])[i], list(data["PC2"])[i]), ha = "center", va = "bottom")

                return regplots

            plot_window.figure.clear()
            variable_ax = plot_window.figure.add_subplot(111)
            hue_regplot(data=pc_df, x='PC1', y='PC2', hue='Condition', ax=variable_ax)
            plot_window.figure.tight_layout()
            plot_window.canvas.draw()
        

        def heatmap():
            """
            Generates a heatmap based on the provided input data, metadata, and information.

            The heatmap can be filtered by region and structure level. If no matching 
            data is found, an alert is shown. The generated heatmap is displayed in the 
            PlotWindow.
            """
            if self.input_csv.empty or self.metadata_csv.empty or self.information_csv.empty:
                alert = utils.QMessageBox()
                alert.setText("Some of the input files do not exist!")
                alert.exec()
                return
            """Plot Heatmap"""
            input_csv = self.input_csv.copy()
            print(input_csv)
            information = self.information_csv.copy()

            brainregion = ""
            if filter_region_lineedit.text() != "":
                region = filter_region_lineedit.text()
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
                brainregion = f"region_{region}"

            if filter_level_combobox.currentText() != "None":
                level = int(filter_level_combobox.currentText())
                index_list = []
                for i,val in enumerate(information["CorrespondingLevel"]):
                    array = eval(val)
                    if level == array[0]:
                        index_list.append(i)
                input_csv = input_csv.iloc[index_list, :]
                information = information.iloc[index_list, :]
                brainregion = f"{brainregion}level_{str(level)}"

            brainregion = f"{brainregion}_heatmap"

            if input_csv.empty:
                alert = utils.QMessageBox()
                alert.setText("After filtering the region the dataframe it is empty! - Try other filters")
                alert.exec()
                return
            

            input_csv = input_csv.dropna()
            input_csv = input_csv.loc[:, input_csv.columns != "Region"]
            input_csv = input_csv[utils.np.isfinite(input_csv).all(1)]
            input_csv = input_csv.loc[(input_csv!=0).any(axis=1)]

            print("Input csv shape:  ",input_csv.shape )
            if input_csv.shape[0] > 50:
                alert = utils.QMessageBox()
                alert.setText("After filtering the region the dataframe has too many entries for a heatmap, please filter more specifically - Try other filters")
                alert.exec()
                return

            regions = input_csv.index.to_numpy()
            input_csv = input_csv.reset_index(drop = True)

            if input_csv.empty:
                alert = utils.QMessageBox()
                alert.setText("After filtering the region the dataframe it is empty! - Try other filters")
                alert.exec()
                return
            

            output_dir = utils.os.path.dirname(input_file.text())
            output_name = f"/{brainregion}_{utils.os.path.basename(input_file.text())[:-4]}.png"
            
            
            #utils.sns.heatmap(input_csv, yticklabels=regions, annot=False)
            #utils.plt.title(brainregion)
            #utils.plt.savefig(output_dir + output_name, bbox_inches='tight')
            #utils.plt.close()

            plot_window.figure.clear()

            variable_ax = plot_window.figure.add_subplot(111)


            utils.sns.heatmap(input_csv, yticklabels=regions, annot=False, ax = variable_ax)
            utils.plt.close()
            plot_window.figure.tight_layout()
            plot_window.canvas.draw()
            


        def boxplot():
            """
            Generates a boxplot based on the provided input data, metadata, and information.

            The plot is filtered by the specified region and condition, and shows the
            distribution of the values across conditions. The generated boxplot is 
            displayed in the PlotWindow.
            """
            if self.input_csv.empty or self.metadata_csv.empty or self.information_csv.empty:
                alert = utils.QMessageBox()
                alert.setText("Some of the input files do not exist!")
                alert.exec()
                return
            input_csv = self.input_csv.copy()
            print(input_csv)
            information = self.information_csv.copy()
            brainregion = ""
            if filter_specific_region_lineedit.text() != "":
                region = filter_specific_region_lineedit.text()
                print(information["TrackedWay"])
                if region not in information["TrackedWay"]:
                    alert = utils.QMessageBox()
                    alert.setText("Region does not exist in ontology file! Please check if Region is written in the correct way!")
                    alert.exec()
                    return

                region = filter_specific_region_lineedit.text()
                if region in input_csv.index:
                    input_csv = input_csv[input_csv.index == region]

                conditions = self.metadata_csv["condition"].unique()

                sample_names = list(input_csv.columns)
                for i in sample_names:
                    cpm_name = f"{i}_processed"
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
                            processed_list = list([f"{str(l)}_processed" for l in list(metadata_list_tmp["sample"])])
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
                    input_csv[f"{str(i)}_mean"] = array_of_means
                    input_csv[f"{str(i)}_stdd"] = array_of_stdd
                    input_csv[f"{str(i)}_med"] = array_of_medians
                    input_csv[f"{str(i)}_single_values"] = array_of_single_values

                print(input_csv)
                array_for_boxplots = []

                for i in conditions:
                    spread = list(input_csv[f"{str(i)}_single_values"])

                    data = utils.np.concatenate(spread)
                    array_for_boxplots.append(data)
                print("Array for boxplots\n", array_for_boxplots)

                df_boxplot = utils.pd.DataFrame()

                for val, i in enumerate(conditions):
                    method = "absolute"
                    region_name = region
                    df_tmp = utils.pd.DataFrame({method: array_for_boxplots[val]})
                    df_tmp["condition"] = i
                    df_boxplot = utils.pd.concat([df_boxplot, df_tmp])
                    fig, variable_ax = utils.plt.subplots()
                    variable_ax = utils.sns.boxplot(x="condition", y=method, data=df_boxplot)
                    variable_ax = utils.sns.swarmplot(x="condition", y=method, data=df_boxplot, color=".25")

                    region_name = str(region_name).replace(" ", "")
                    region_name = str(region_name).replace("/", "")
                    utils.plt.title(region)

                output_dir = utils.os.path.dirname(input_file.text())
                output_name = f"/{region}_boxplot_{utils.os.path.basename(input_file.text())[:-4]}.png"
                utils.plt.close

                plot_window.figure.clear()
                ax2 = plot_window.figure.add_subplot(111)
                utils.sns.boxplot(x="condition", y=method, data=df_boxplot, ax = ax2)
                utils.sns.swarmplot(x="condition", y=method, data=df_boxplot, color=".25", ax = ax2)
                plot_window.figure.tight_layout()
                plot_window.canvas.draw()
                
        return tab
