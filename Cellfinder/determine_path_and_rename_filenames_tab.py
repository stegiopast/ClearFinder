import utils

## Contains all features of the grouping and normalization tab

class RenameBox(utils.QWidget):
    def __init__(self, filename_to_check, acceptor, position, _path):
        super().__init__()
        self.path = _path
        self.acceptor = acceptor
        self.position = position
        self.rename_box = None
        self.setWindowTitle("Cellfinder GUI")
        self.filename_to_check = filename_to_check
        self.channel_chosen = "C01"
        self.shift_bar = utils.QLineEdit("0")
        self.accept = utils.QPushButton("Accept")
        self.reject = utils.QPushButton("Reject and shift")
        self.quit_renaming = utils.QPushButton("Quit Renaming")
        self.layout = utils.QGridLayout()
        self.update_layout()
        self.setLayout(self.layout)

    def update_layout(self):
        """Update the layout inside the QWindow for the DeterminePath Tab"""
        self.int_shift = int(self.shift_bar.text())
        self.new_position = self.position + self.int_shift
        self.update(self.new_position)
        print("Filename: ",self.filename_to_check[self.position:len(self.filename_to_check)])
        print("Current Filename: ",self.current_filename)
        print(self.position)
        inner_layout = utils.QGridLayout()
        inner_layout.addWidget(utils.QLabel("Current output Filename:"),0,0)
        inner_layout.addWidget(utils.QLabel(self.current_filename),0,1)
        inner_layout.addWidget(utils.QLabel("      "),1,0)
        inner_layout.addWidget(utils.QLabel("Does filename not fit to template 001_C01.tif - 9999_C01.tif ?"),2,0)
        inner_layout.addWidget(utils.QLabel("Provide shift (+ and - allowed) and Reject:"), 3,0)
        inner_layout.addWidget(self.shift_bar, 3,1)
        inner_layout.addWidget(self.reject,3,2)
        inner_layout.addWidget(utils.QLabel("      "),4,0)
        inner_layout.addWidget(utils.QLabel("Does filename fit ?"),5,0)
        inner_layout.addWidget(utils.QLabel("Press accept:"), 6,0)
        inner_layout.addWidget(self.accept,6,1)
        inner_layout.addWidget(utils.QLabel("      "),7,0)
        inner_layout.addWidget(utils.QLabel("Doesn't the filename fit at all?"),8,0)
        inner_layout.addWidget(utils.QLabel("Press Quit:"),9,0)
        inner_layout.addWidget(self.quit_renaming,9,1)

        self.delete_items_of_layout(self.layout)

        self.layout.addLayout(inner_layout,0,0)
        return self.layout

    def update(self,current_position):
        """Start of standartize the filenames"""
        self.position = current_position
        self.current_filename = self.filename_to_check[self.position:len(self.filename_to_check)]

    def delete_items_of_layout(self,layout):
        """Deletion in filename"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.delete_items_of_layout(item.layout())

    def perform_cut(self):
        """actually performs the cut in the filename"""
        print("path:",self.path)
        flag = True

        for file in utils.pathlib.Path(self.path).iterdir():
            if file.is_file():
                print(file.stem)
                old_name = file.stem + ".tif"
                new_name = old_name[self.position:len(old_name)]
                dir = file.parent
                new_obj = utils.re.match(r'^[0-9]{3}_',new_name)
                if new_obj:
                    new_name = "Z0" + new_name
                else:
                    new_obj = utils.re.match(r'[0-9]',new_name)
                    if new_obj:
                        new_name = "Z" + new_name
                print(new_name)
                file.rename(utils.pathlib.Path(dir, new_name))

            elif flag:
                alert = utils.QMessageBox()
                alert.setText("You have more than one channel, please select a channel")
                alert.exec()
                flag = False


class InitWorkspace:
    def init_workspace(self,path = '/home/cellfinder_data',channel = 0):
        """Constructor"""
        if channel == 1:
            channel_str = "C01"
        elif channel == 2:
            channel_str = "C02"
        else:
            channel_str = ""
        if utils.os.path.exists(path + '/Signal/' + channel_str):
            self.channel_chosen = channel_str
        else:
            self.channel_chosen = ""
            alert = utils.QMessageBox()
            alert.setText("Path does not exist!")
            alert.exec()
            if not utils.os.path.exists(path + '/Signal'):
                alert2 = utils.QMessageBox()
                alert2.setText("In this folder there is no Signal folder existent! Please choose different sample!")
                alert2.exec()

        my_working_directory = path

        if utils.os.path.exists(my_working_directory):
            self.my_working_directory = my_working_directory
            print("Working dir:",self.my_working_directory)
            print("Channel chosen:", self.channel_chosen)
            return my_working_directory
        else:
            print("Path does not exist!")

class RenameLayout:
    def rename_layout(self):
        def rename_files(_path, extend):
            if utils.os.path.exists(_path):
                pathlist = [_path + extend]

                ## Remove all the tabs in the filenames
                ## Iteration over each file in Auto and Signal directories
                ## Each filename-string is iterated and a new_name string without tabs is generated by skipping every " " in the old_name.
                ## The filename becomes then substituted by the new name
                for i in pathlist:
                    for file in utils.pathlib.Path(i).iterdir():
                        if file.is_file():
                            old_name = file.stem
                            print(file.stem)
                            new_name = ""
                            for i in old_name:
                                if i != " ":
                                    new_name += i
                            new_name += ".tif"
                            dir = file.parent
                            file.rename(utils.pathlib.Path(dir, new_name))

                ##Selecting the right range for each filename:
                for i in pathlist:
                    filename_list = [file for file in utils.pathlib.Path(i).iterdir()]
                    first_file = filename_list[0]
                    first_filename = first_file.stem + ".tif"
                    size_bool = False
                    string_pos = 0

                    self.rename_box = RenameBox(first_filename,size_bool,string_pos,i)
                    self.rename_box.show()

                    #self.rename_box.reject.clicked.connect(lambda: self.rename_box.update(False,self.rename_box.new_position))
                    self.rename_box.reject.clicked.connect(self.rename_box.update_layout)
                    self.rename_box.reject.clicked.connect(self.rename_box.repaint)

                    #reject.clicked.connect(self.close())
                    self.rename_box.accept.clicked.connect(self.rename_box.perform_cut)
                    self.rename_box.accept.clicked.connect(self.rename_box.close)

                    #Next line is implemented to quit the application in case a renaming is not possible.
                    #self.rename_box.quit_renaming.clicked.connect(lambda: self.rename_box.update(False,4000000))
                    self.rename_box.quit_renaming.clicked.connect(self.rename_box.close)
            else:
                alert = utils.QMessageBox()
                alert.setText("Path does not exist!")
                alert.exec()
        tab = utils.QWidget()
        outer_layout = utils.QVBoxLayout()
        inner_layout = utils.QGridLayout()

        ## Widget for input path
        ws_path = utils.QLabel("/home/cellfinder_data")
        choose_ws = utils.QPushButton("Choose sample")
        channel_button = utils.QComboBox()
        channel_button.insertItem(0,"")
        channel_button.insertItem(1,"C01")
        channel_button.insertItem(2,"C02")
        set_ws = utils.QPushButton("Set workspace")
        rename_button1 = utils.QPushButton("Rename files in Auto")
        rename_button2 = utils.QPushButton("Rename files in Signal")

        def choose_sample():
            """Function for selection of working directory"""
            path = utils.QFileDialog.getExistingDirectory(self, "Choose sample data folder")
            if path != ('', ''):
                ws_path.setText(path)
            else:
                ws_path.setText("")

        inner_layout.addWidget(utils.QLabel("<b>Set Workspace:</b>"),0,0)
        inner_layout.addWidget(utils.QLabel("Input path of interest:"),1,0)
        inner_layout.addWidget(ws_path,1,1)
        #inner_layout.addWidget(channel_button,1,2)
        inner_layout.addWidget(set_ws,1,3)
        inner_layout.addWidget(rename_button1,1,4)
        inner_layout.addWidget(rename_button2,1,5)
        inner_layout.addWidget(choose_ws,2,1)
        inner_layout.addWidget(utils.QLabel("      "),3,0)

        choose_ws.clicked.connect(lambda: choose_sample())
        set_ws.clicked.connect(lambda: self.init_workspace(ws_path.text(),0))
        rename_button1.clicked.connect(lambda: rename_files(_path = self.my_working_directory, extend='/Auto'))
        rename_button2.clicked.connect(lambda: rename_files(_path = self.my_working_directory, extend='/Signal/' + self.channel_chosen))

        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab

