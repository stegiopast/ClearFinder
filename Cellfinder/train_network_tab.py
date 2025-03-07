import utils

class TrainNetwork:
    def train_network(self, _yaml_files:str = "",
                        _trained_model:str = "",
                        _continue_training:bool = True, 
                        _test_fraction:float = 0.1, 
                        _learning_rate:float = 0.0001, 
                        _batch_size:int = 32,
                        _epochs:int = 1,
                        _output_directory:str = "") -> None:
        """
        Trains a machine learning model using the specified configuration.

        Args:
            _yaml_files (str): Path to the YAML files for training data.
            _trained_model (str): Path to a pre-trained model for continuing training.
            _continue_training (bool): Whether to continue training from a pre-trained model.
            _test_fraction (float): Fraction of the data to be used for testing.
            _learning_rate (float): The learning rate to use for training.
            _batch_size (int): The batch size for training.
            _epochs (int): The number of epochs to train the model.
            _output_directory (str): Directory where the output of training will be saved.

        Raises:
            QMessageBox: If the output directory is not specified or does not exist.
        """
        output_directory = _output_directory

        print(output_directory)
        if output_directory == "":
            alert = utils.QMessageBox()
            alert.setText("Please choose output directory!")
            alert.exec()
            return
        
        print("Output directory will be", output_directory)

        home = utils.Path.home()
        install_path = home / ".cellfinder"
               
        training_string = "cellfinder_train "
        training_yml_string = f"-y {str(_yaml_files)} "
        if _continue_training and _trained_model != "":
            continue_str = "--continue-training "
            trained_model_str = f"--trained-model {str(_trained_model)} "
        else:
            continue_str = ""
            trained_model_str = ""

        learning_rate_string = f"--learning-rate {str(_learning_rate)} "
        
        batch_size_str = f"--batch-size {str(_batch_size)} "
        epochs_str = f"--epochs {str(_epochs)} "
        output_dir_str = f"-o {str(output_directory)}"

        final_string = training_string + training_yml_string + continue_str + trained_model_str + learning_rate_string + batch_size_str + epochs_str + output_dir_str
                         
        if utils.os.path.exists(output_directory):
            utils.os.system(final_string)
        else:
            alert = utils.QMessageBox()
            alert.setText("Output directory doesn't exists!")
            alert.exec()
            return

class TrainingNetworkLayout:
    def training_layout(self) -> utils.QWidget:
        """
        Creates the GUI layout for the training network tab.

        Returns:
            QWidget: The layout containing the widgets for setting up and starting the training process.
        """  
        tab = utils.QWidget()
        outer_layout = utils.QVBoxLayout()
        inner_layout = utils.QGridLayout()

        ### Widgets for data access to trained models and training data
        yaml_files = utils.QLabel("")
        choose_yaml_button = utils.QPushButton("Choose Yaml")
        trained_model = utils.QLabel("")
        choose_trained_model_button = utils.QPushButton("Choose trained model")
        continue_training = utils.QCheckBox()
        
        ### Widgets for training parameters 
        test_fraction = utils.QLineEdit("0.1")
        learning_rate = utils.QLineEdit("0.0001")
        batch_size = utils.QLineEdit("32")
        epochs  = utils.QLineEdit("1")
        training_output_directory = utils.QLabel("")
        choose_training_output_button = utils.QPushButton("Choose your base directory")

        ### Widgets for starting training,loading and saving parametes
        config_path = utils.QLineEdit("Insert filename extension")
        load_config_button = utils.QPushButton("Load parameters")
        save_config_button = utils.QPushButton("Save parameters")
        train_network_button = utils.QPushButton("Train network")
        
        ### Visualization of Widgets 
        inner_layout.addWidget(utils.QLabel("Training data"), 0, 0)
        inner_layout.addWidget(yaml_files, 0, 1)
        inner_layout.addWidget(choose_yaml_button, 0, 2)
        
        inner_layout.addWidget(utils.QLabel("Pretrained Model"), 1, 0)
        inner_layout.addWidget(trained_model, 1, 1)
        inner_layout.addWidget(choose_trained_model_button, 1, 2)

        inner_layout.addWidget(utils.QLabel("Continue training ?"), 2, 0)
        inner_layout.addWidget(continue_training, 2, 1)

        inner_layout.addWidget(utils.QLabel("Test fraction"), 3, 0)
        inner_layout.addWidget(test_fraction, 3, 1)
        
        inner_layout.addWidget(utils.QLabel("Learning Rate"), 4, 0)
        inner_layout.addWidget(learning_rate, 4, 1)
        
        inner_layout.addWidget(utils.QLabel("Batch size"), 5, 0)
        inner_layout.addWidget(batch_size, 5, 1)
        
        inner_layout.addWidget(utils.QLabel("Epochs"), 6, 0)
        inner_layout.addWidget(epochs, 6, 1)

        inner_layout.addWidget(utils.QLabel("Choose base directory and create new one"), 7, 0)
        inner_layout.addWidget(training_output_directory, 7, 1)
        inner_layout.addWidget(choose_training_output_button, 7, 2)
        
        inner_layout.addWidget(config_path, 8, 0)
        inner_layout.addWidget(load_config_button, 8, 1)
        inner_layout.addWidget(save_config_button, 8, 2)
        inner_layout.addWidget(train_network_button, 8, 3)

        ### Save and load paramters function
        def save_config(save_path:str) -> None:
            """
            Saves the current configuration to a CSV file.

            Args:
                save_path (str): The path where the configuration file will be saved.

            Displays a message if the file already exists.
            """
            if not utils.os.path.exists(save_path):    
                print(save_path)
                resample_variable_list = [continue_training.isChecked(),
                                          test_fraction.text(),
                                          learning_rate.text(),
                                          batch_size.text(),
                                          epochs.text()]

                pd_df = utils.pd.DataFrame([resample_variable_list],
                                     index = [1],
                                     columns = ["Continue training", "Test fraction",
                                                "Learning rate","Batch size","Epochs"])
                pd_df.to_csv(save_path)
            else:
                alert = utils.QMessageBox()
                alert.setText("File already exists!")
                alert.exec()
               
        def load_config(load_path:str) -> None:
            """
            Loads configuration parameters from a CSV file.

            Args:
                load_path (str): The path to the configuration file to load.

            Displays a message if the file does not exist.
            """
            if utils.os.path.exists(load_path):    
                print(load_path)
                pd_df = utils.pd.read_csv(load_path, header=0)
                continue_training.setCheckState(bool(pd_df["Continue training"][0]))
                test_fraction.setText(str(pd_df["Test fraction"][0]))
                learning_rate.setText(str(pd_df["Learning rate"][0]))
                batch_size.setText(str(pd_df["Batch size"][0]))
                epochs.setText(str(pd_df["Epochs"][0]))
          
            else:
                alert = utils.QMessageBox()
                alert.setText("Path does not exist!")
                alert.exec()   


        def choose_yaml() -> None:
            """
            Opens a file dialog to choose a YAML file for training data.

            Updates the label with the selected file path.
            """
            path = utils.QFileDialog.getOpenFileName(self, "Choose a Model file (.h5)")
            if path != ('', ''):
                yaml_files.setText(str(path[0]))
                print("Yaml files text", yaml_files.text())
            else:
                yaml_files.setText('')
                print("Yaml files text", yaml_files.text())

        def choose_model() -> None:
            """
            Opens a file dialog to choose a trained model file.

            Updates the label with the selected file path.
            """
            path = utils.QFileDialog.getOpenFileName(self, "Choose a Model file (.h5)")
            if path != ('', ''):
                trained_model.setText(str(path[0]))
                print("Trained model text",trained_model.text())
            else:
                trained_model.setText('')
                print("Trained model text",trained_model.text())

        def choose_output_directory() -> None:
            """
            Opens a file dialog to choose an output directory for training.

            Updates the label with the selected directory path.
            """
            path = utils.QFileDialog.getExistingDirectory(self, "Save Output training data")
            print(path)
            if path != '':
                training_output_directory.setText(f"{str(path)}/")
                print("Output training", training_output_directory.text())
            else:
                training_output_directory.setText('')
                print("Output training", training_output_directory.text())

        ### Connection of widgets with fundtion, start training, save and load, choose yaml or trained models
        
        load_config_button.pressed.connect(lambda: load_config(load_path = f"{utils.os.getcwd()}/train_network_{config_path.text()}.csv"))
        save_config_button.pressed.connect(lambda: save_config(save_path = f"{utils.os.getcwd()}/train_network_{config_path.text()}.csv"))
                
        train_network_button.clicked.connect(lambda: self.train_network(_yaml_files=str(yaml_files.text()),
                                                                        _trained_model =str(trained_model.text()),
                                                                        _continue_training=bool(continue_training.isChecked()),
                                                                        _test_fraction=float(test_fraction.text()),
                                                                        _learning_rate=float(learning_rate.text()),
                                                                        _batch_size=int(batch_size.text()),
                                                                        _epochs=int(epochs.text()),
                                                                        _output_directory = str(training_output_directory.text())))

        choose_yaml_button.clicked.connect(lambda: choose_yaml())
        choose_trained_model_button.clicked.connect(lambda: choose_model())
        choose_training_output_button.pressed.connect(lambda: choose_output_directory())

        ### Add inner layout to outer layout, add outer layout to tab and return tab
        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab
