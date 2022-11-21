import utils

# Contains all features of the train network tab

class TrainNetwork:
    """Contains all features of the train network tab"""
    def train_network(self, _yaml_files="",
                        _trained_model = "",
                        _continue_training=True,
                        _test_fraction=0.1,
                        _learning_rate=0.0001,
                        _batch_size=32,
                        _epochs=1,
                        _output_directory=""):

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
        training_yml_string = "-y " + str(_yaml_files) + " "
        if _continue_training and _trained_model != "":
            continue_str = "--continue-training "
            trained_model_str = "--trained-model " + str(_trained_model) + " "
        else:
            continue_str = ""
            trained_model_str = ""

        learning_rate_string = "--learning-rate " + str(_learning_rate) + " "

        batch_size_str = "--batch-size " + str(_batch_size) + " "
        epochs_str = "--epochs " + str(_epochs) + " "
        output_dir_str = "-o " + str(output_directory)

        final_string = training_string + training_yml_string + continue_str + trained_model_str + learning_rate_string + batch_size_str + epochs_str + output_dir_str

        if utils.os.path.exists(output_directory):
            utils.os.system(final_string)
        else:
            alert = utils.QMessageBox()
            alert.setText("Output directory doesn't exists!")
            alert.exec()
            return

class TrainingNetworkLayout:
    """Layouting the Train_Network_Tab"""
    def training_layout(self):  
        tab = utils.QWidget()
        outer_layout = utils.QVBoxLayout()
        inner_layout = utils.QGridLayout()

        # Widgets for data access to trained models and training data
        yaml_files = utils.QLabel("")
        choose_yaml_button = utils.QPushButton("Choose Yaml")
        trained_model = utils.QLabel("")
        choose_trained_model_button = utils.QPushButton("Choose trained model")
        continue_training = utils.QCheckBox()

        # Widgets for training parameters
        test_fraction = utils.QLineEdit("0.1")
        learning_rate = utils.QLineEdit("0.0001")
        batch_size = utils.QLineEdit("32")
        epochs  = utils.QLineEdit("1")
        training_output_directory = utils.QLabel("")
        choose_training_output_button = utils.QPushButton("Choose your base directory")

        # Widgets for starting training,loading and saving parametes
        config_path = utils.QLineEdit("Insert filename extension")
        load_config_button = utils.QPushButton("Load parameters")
        save_config_button = utils.QPushButton("Save parameters")
        train_network_button = utils.QPushButton("Train network")

        # Visualization of Widgets
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

        # Save and load paramters function
        def save_config(save_path):
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


        def load_config(load_path):
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


        def choose_yaml():
            """Functions for choosing .yaml fiels or trained models (.h5) files"""
            path = utils.QFileDialog.getOpenFileName(self, "Choose a Model file (.h5)")
            if path != ('', ''):
                yaml_files.setText(str(path[0]))
                print("Yaml files text", yaml_files.text())
            else:
                yaml_files.setText('')
                print("Yaml files text", yaml_files.text())


        def choose_model():
            path = utils.QFileDialog.getOpenFileName(self, "Choose a Model file (.h5)")
            if path != ('', ''):
                trained_model.setText(str(path[0]))
                print("Trained model text",trained_model.text())
            else:
                trained_model.setText('')
                print("Trained model text",trained_model.text())


        def choose_output_directory():
            """Function for choosing output training directory"""
            path = utils.QFileDialog.getExistingDirectory(self, "Save Output training data")
            print(path)
            if path != '':
                training_output_directory.setText(str(path)+ "/")
                print("Output training", training_output_directory.text())
            else:
                training_output_directory.setText('')
                print("Output training", training_output_directory.text())

        # Connection of widgets with fundtion, start training, save and load, choose yaml or trained models
        load_config_button.pressed.connect(lambda: load_config(load_path = utils.os.getcwd() + "/train_network_" + config_path.text() + ".csv"))
        save_config_button.pressed.connect(lambda: save_config(save_path = utils.os.getcwd() + "/train_network_" + config_path.text() + ".csv"))

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
