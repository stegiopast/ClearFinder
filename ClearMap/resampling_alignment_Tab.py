import utils


class ResamplingAlignment:
    """
    This class handles the process of resampling and aligning images with specific resolutions.
    It works with predefined parameters for source and sink resolutions, and performs 
    image alignment using the elastix library.
    """
    def init_reference(self, 
                       source_res_x: float = 3.02,
                       source_res_y: float = 3.02,
                       source_res_z: float = 3,
                       sink_res_x: float = 10,
                       sink_res_y: float = 10,
                       sink_res_z: float = 10,
                       auto_source_res_x: float = 3.02,
                       auto_source_res_y: float = 3.02,
                       auto_source_res_z: float = 3,
                       auto_sink_res_x: float = 25,
                       auto_sink_res_y: float = 25,
                       auto_sink_res_z: float = 25,
                       orientation_x: int = 1,
                       orientation_y: int = 2,
                       orientation_z: int = 3) -> None:
        """
        Initializes the reference for resampling and alignment.
        
        Args:
            source_res_x (float): Resolution in the x-direction for the source image.
            source_res_y (float): Resolution in the y-direction for the source image.
            source_res_z (float): Resolution in the z-direction for the source image.
            sink_res_x (float): Resolution in the x-direction for the sink image.
            sink_res_y (float): Resolution in the y-direction for the sink image.
            sink_res_z (float): Resolution in the z-direction for the sink image.
            auto_source_res_x (float): Resolution in the x-direction for the auto source image.
            auto_source_res_y (float): Resolution in the y-direction for the auto source image.
            auto_source_res_z (float): Resolution in the z-direction for the auto source image.
            auto_sink_res_x (float): Resolution in the x-direction for the auto sink image.
            auto_sink_res_y (float): Resolution in the y-direction for the auto sink image.
            auto_sink_res_z (float): Resolution in the z-direction for the auto sink image.
            orientation_x (int): Orientation in the x-direction for alignment.
            orientation_y (int): Orientation in the y-direction for alignment.
            orientation_z (int): Orientation in the z-direction for alignment.

        Returns:
            None
        """
        if not utils.os.path.exists(self.my_working_directory):
            alert = utils.QMessageBox()
            alert.setText("Path to your working directory does not exist! Please check if your workspace was set correctly.")
            alert.exec()
            return
        elif not utils.os.path.exists(f"{self.my_working_directory}/Signal") or not utils.os.path.exists(f"{self.my_working_directory}/Auto"):
            alert = utils.QMessageBox()
            alert.setText("Path to your working directory does not contain a Signal or Auto folder! Please choose another path and check documentation about the folder structure.")
            alert.exec()
            return


        if not utils.os.path.exists(f"{self.my_working_directory}/elastix_resampled_to_auto_{self.chosen_channel}"):
            utils.os.mkdir(f"{self.my_working_directory}/elastix_resampled_to_auto_{self.chosen_channel}")
        else:
            print(f"{self.my_working_directory}/elastix_resampled_to_auto_{self.chosen_channel} already exists\n")

        if not utils.os.path.exists(f"{self.my_working_directory}/elastix_auto_to_reference_{self.chosen_channel}"):
            utils.os.mkdir(f"{self.my_working_directory}/elastix_auto_to_reference_{self.chosen_channel}")
        else:
            print(f"{self.my_working_directory}/elastix_auto_to_reference_{self.chosen_channel} already exists\n")

        resourcesDirectory = utils.settings.resources_path
        annotation_file, reference_file, distance_file = utils.ano.prepare_annotation_files(slicing=self.slicing,
                                                                                      orientation=(orientation_x, orientation_y, orientation_z),
                                                                                      overwrite=False,
                                                                                      verbose=True)

        align_channels_affine_file = utils.io.join(resourcesDirectory, 'Alignment/align_affine.txt')
        align_reference_affine_file = utils.io.join(resourcesDirectory, 'Alignment/align_affine.txt')
        align_reference_bspline_file = utils.io.join(resourcesDirectory, 'Alignment/align_bspline.txt')

        resample_parameter = {"source_resolution": (source_res_x, source_res_y, source_res_z),  # Resolution of your own files!
                              "sink_resolution": (sink_res_x, sink_res_y, sink_res_z),
                              "processes": 4,
                              "verbose": True}

        source = self.ws.source(f"raw_{self.chosen_channel}")
        sink = self.ws.filename(f"stitched_{self.chosen_channel}")
        self.orientation = (orientation_x,orientation_y,orientation_z)
        utils.io.convert(source, sink, verbose=True)

        utils.res.resample(self.ws.filename(f"stitched_{self.chosen_channel}"),
                     sink=self.ws.filename(f"resampled_{self.chosen_channel}"), **resample_parameter)

        resample_parameter_auto = {"source_resolution": (auto_source_res_x, auto_source_res_y, auto_source_res_z),
                                   "sink_resolution": (auto_sink_res_x, auto_sink_res_y, auto_sink_res_z),
                                   "processes": 4,
                                   "verbose": True}

        utils.res.resample(self.ws.filename('autofluorescence'),
                     sink=self.ws.filename(f"resampled_{self.chosen_channel}",postfix='autofluorescence'),
                     **resample_parameter_auto)

        align_channels_parameter = {
            # moving and reference images
            "moving_image": self.ws.filename(f"resampled_{self.chosen_channel}", postfix='autofluorescence'),
            "fixed_image": self.ws.filename(f"resampled_{self.chosen_channel}"),

            # elastix parameter files for alignment
            "affine_parameter_file": align_channels_affine_file,
            "bspline_parameter_file": None,

            # directory of the alig'/home/nicolas.renier/Documents/ClearMap_Ressources/Par0000affine.txt',nment result
            # "result_directory" :  "/raid/CellRegistration_Margaryta/ClearMap1_2/ClearMap2/elastix_resampled_to_auto"
            "result_directory": f"{self.my_working_directory}/elastix_resampled_to_auto_{self.chosen_channel}"
        }

        # first alginment !
        utils.elx.align(**align_channels_parameter)

        align_reference_parameter = {
            # moving and reference images
            "moving_image": reference_file,
            "fixed_image": self.ws.filename(f"resampled_{self.chosen_channel}", postfix='autofluorescence'),

            # elastix parameter files for alignment
            "affine_parameter_file": align_reference_affine_file,
            "bspline_parameter_file": align_reference_bspline_file,
            # directory of the alignment result
            "result_directory": f"{self.my_working_directory}/elastix_auto_to_reference_{self.chosen_channel}"
        }
        utils.elx.align(**align_reference_parameter)
        return


class Resampling_Alignment_Layout:
    """
    This class handles the user interface layout for resampling and alignment parameters.
    It provides widgets to input and save configuration parameters for resampling and alignment.
    """
    def resample_layout(self) -> utils.QWidget:
        """
        Creates the layout for resampling and alignment configuration, including widgets 
        for entering source/sink resolutions, orientation, and options to load/save configuration.

        Returns:
            utils.QWidget: The widget containing the resampling and alignment layout.
        """
        tab = utils.QWidget()
        outer_layout = utils.QVBoxLayout()
        inner_layout = utils.QGridLayout()

        ### Widgets Orientation variables
        orientation_x = utils.QLineEdit("1")
        orientation_y = utils.QLineEdit("2")
        orientation_z = utils.QLineEdit("3")

        ### Widgets for source resolution variables
        source_res_x: utils.QLineEdit = utils.QLineEdit("3.02")
        source_res_y = utils.QLineEdit("3.02")
        source_res_z = utils.QLineEdit("3")

        ### Widgets for sink resolution variables
        sink_res_x = utils.QLineEdit("25")
        sink_res_y = utils.QLineEdit("25")
        sink_res_z = utils.QLineEdit("25")

        ### Widgets for auto_source resolution variables
        auto_source_res_x = utils.QLineEdit("3.02")
        auto_source_res_y = utils.QLineEdit("3.02")
        auto_source_res_z = utils.QLineEdit("3")

        ### Widgets for auto_source resolution variables
        auto_sink_res_x = utils.QLineEdit("25")
        auto_sink_res_y = utils.QLineEdit("25")
        auto_sink_res_z = utils.QLineEdit("25")

        ### Widgets for parameter saving and loading
        start_resampling_button = utils.QPushButton("Resample")

        config_path = utils.QLineEdit("Insert filename extension")
        load_config_button = utils.QPushButton("Load parameters")
        save_config_button = utils.QPushButton("Save parameters")


        def save_config(save_path:str) -> None:
            """
            Saves the current resampling and alignment configuration to a CSV file.
            
            The function retrieves the values from the input fields (source resolution, sink resolution, 
            auto-source resolution, auto-sink resolution, and orientation) and stores them in a CSV file 
            at the specified `save_path`. If the file already exists at the given path, an alert is shown.

            Args:
                save_path (str): The path where the configuration CSV file should be saved. This should 
                                include the full file name and extension (e.g., 'config.csv').
                                
            Returns:
                None
                
            Raises:
                utils.QMessageBox: Displays an alert if the specified `save_path` already exists.
            """
            if not utils.os.path.exists(save_path):
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

                pd_df = utils.pd.DataFrame([resample_variable_list],
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
                alert = utils.QMessageBox()
                alert.setText("File already exists!")
                alert.exec()


        def load_config(load_path:str) -> None:
            """
            Loads the configuration parameters from a CSV file and updates the corresponding widgets.
            
            The function reads the CSV file specified by `load_path`, extracts the resampling and alignment
            parameters (source resolution, sink resolution, auto-source resolution, auto-sink resolution, 
            and orientation), and updates the respective QLineEdit widgets with the values from the CSV.

            Args:
                load_path (str): The file path to the CSV file containing the configuration parameters.
                
            Returns:
                None
                
            Raises:
                utils.QMessageBox: Displays a message box with an error if the provided path does not exist.
            """
            if utils.os.path.exists(load_path):
                print(load_path)
                pd_df = utils.pd.read_csv(load_path, header=0)
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
                alert = utils.QMessageBox()
                alert.setText("Path does not exist!")
                alert.exec()

        ### visualization of Widgets for resampling
        inner_layout.addWidget(utils.QLabel("<b>Resample Parameter: <\b>"), 0, 0)
        inner_layout.addWidget(utils.QLabel("Source Resolution: "), 1, 0)
        inner_layout.addWidget(utils.QLabel("X:"), 1, 1)
        inner_layout.addWidget(source_res_x, 1, 2)
        inner_layout.addWidget(utils.QLabel("Y:"), 1, 3)
        inner_layout.addWidget(source_res_y, 1, 4)
        inner_layout.addWidget(utils.QLabel("Z:"), 1, 5)
        inner_layout.addWidget(source_res_z, 1, 6)

        inner_layout.addWidget(utils.QLabel("Sink Resolution: "), 2, 0)
        inner_layout.addWidget(utils.QLabel("X:"), 2, 1)
        inner_layout.addWidget(sink_res_x, 2, 2)
        inner_layout.addWidget(utils.QLabel("Y:"), 2, 3)
        inner_layout.addWidget(sink_res_y, 2, 4)
        inner_layout.addWidget(utils.QLabel("Z:"), 2, 5)
        inner_layout.addWidget(sink_res_z, 2, 6)

        inner_layout.addWidget(utils.QLabel("     "), 3, 0)
        inner_layout.addWidget(utils.QLabel("<b>Resample to Auto Parameter:</b>"), 4, 0)
        inner_layout.addWidget(utils.QLabel("Source Resolution: "), 5, 0)
        inner_layout.addWidget(utils.QLabel("X:"), 5, 1)
        inner_layout.addWidget(auto_source_res_x, 5, 2)
        inner_layout.addWidget(utils.QLabel("Y:"), 5, 3)
        inner_layout.addWidget(auto_source_res_y, 5, 4)
        inner_layout.addWidget(utils.QLabel("Z:"), 5, 5)
        inner_layout.addWidget(auto_source_res_z, 5, 6)

        inner_layout.addWidget(utils.QLabel("Sink Resolution: "), 6, 0)
        inner_layout.addWidget(utils.QLabel("X:"), 6, 1)
        inner_layout.addWidget(auto_sink_res_x, 6, 2)
        inner_layout.addWidget(utils.QLabel("Y:"), 6, 3)
        inner_layout.addWidget(auto_sink_res_y, 6, 4)
        inner_layout.addWidget(utils.QLabel("Z:"), 6, 5)
        inner_layout.addWidget(auto_sink_res_z, 6, 6)

        inner_layout.addWidget(utils.QLabel("     "), 7, 0)
        inner_layout.addWidget(utils.QLabel("Orientation: "), 8, 0)
        inner_layout.addWidget(utils.QLabel("X:"), 8, 1)
        inner_layout.addWidget(orientation_x, 8, 2)
        inner_layout.addWidget(utils.QLabel("Y:"), 8, 3)
        inner_layout.addWidget(orientation_y, 8, 4)
        inner_layout.addWidget(utils.QLabel("Z:"), 8, 5)
        inner_layout.addWidget(orientation_z, 8, 6)

        inner_layout.addWidget(utils.QLabel("    "), 9, 0)
        inner_layout.addWidget(config_path, 10, 0, 10, 5, alignment = utils.Qt.AlignTop)
        inner_layout.addWidget(load_config_button, 10, 6)
        inner_layout.addWidget(save_config_button, 10, 7)
        inner_layout.addWidget(start_resampling_button, 10, 8)

        ## These two functions will load or save a variable list
        load_config_button.pressed.connect(lambda: load_config(load_path=f"{utils.os.getcwd()}/resampling_{config_path.text()}.csv"))
        save_config_button.pressed.connect(lambda: save_config(save_path=f"{utils.os.getcwd()}/resampling_{config_path.text()}.csv"))
        
        start_resampling_button.clicked.connect(lambda: self.init_reference(source_res_x=float(source_res_x.text()),
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
