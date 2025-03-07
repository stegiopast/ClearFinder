import utils

# Contains all features of the grouping and normalization tab

class RenameBox(utils.QWidget):
    """A widget for renaming files according to a specified template in a GUI window."""
    def __init__(self, filename_to_check:str, acceptor:bool, position:int, _path:str):
        """
        Initializes the RenameBox widget.
        
        Args:
            filename_to_check (str): The filename to validate against the template.
            acceptor (bool): Flag for accepting or rejecting the filename.
            position (int): Position of character shift in the filename.
            _path (str): Path to the directory containing the files.
        """
        super().__init__()
        self.path = _path
        self.acceptor = acceptor
        self.position = position
        self.rename_box = None
        self.setWindowTitle("Cellfinder GUI")
        self.filename_to_check = filename_to_check
        self.channel_chosen = "C01"
        self.is_first_update = True
        self.shift_bar = utils.QLineEdit("0")
        self.accept = utils.QPushButton("Accept")
        self.reject = utils.QPushButton("Reject and shift")
        self.quit_renaming = utils.QPushButton("Quit Renaming")
        self.layout = utils.QGridLayout()
        self.update_layout()
        self.setLayout(self.layout)

    def update_layout(self) -> utils.QGridLayout:
        """
        Updates the layout for the RenameBox widget based on the current filename position.
        
        Returns:
            QGridLayout: Updated layout with filename acceptance, rejection, and quit options.
        """
        self.int_shift = int(self.shift_bar.text())
        self.new_position = self.position + self.int_shift
        self.update(self.new_position)
        print("Filename: ", self.filename_to_check[self.position:len(self.filename_to_check)])
        print("Current Filename: ", self.current_filename)
        print(self.position)
        inner_layout = utils.QGridLayout()
        inner_layout.addWidget(utils.QLabel("Current output Filename:"), 0, 0)
        inner_layout.addWidget(utils.QLabel(self.current_filename), 0, 1)
        inner_layout.addWidget(utils.QLabel("      "), 1, 0)
        inner_layout.addWidget(utils.QLabel("Does filename not fit to template 1_C01.tif - 99999_C01.tif ?"), 2, 0)
        inner_layout.addWidget(utils.QLabel("Provide shift (+ and - allowed) and Reject:"), 3, 0)
        inner_layout.addWidget(self.shift_bar, 3, 1)
        inner_layout.addWidget(self.reject, 3, 2)
        inner_layout.addWidget(utils.QLabel("      "), 4, 0)
        inner_layout.addWidget(utils.QLabel("Does filename fit ?"), 5, 0)
        inner_layout.addWidget(utils.QLabel("Press accept:"), 6, 0)
        inner_layout.addWidget(self.accept, 6, 1)
        inner_layout.addWidget(utils.QLabel("      "), 7, 0)
        inner_layout.addWidget(utils.QLabel("Doesn't the filename fit at all?"), 8, 0)
        inner_layout.addWidget(utils.QLabel("Press Quit:"), 9, 0)
        inner_layout.addWidget(self.quit_renaming, 9, 1)

        self.delete_items_of_layout(self.layout)

        self.layout.addLayout(inner_layout, 0, 0)
        return self.layout

    def update(self,current_position:int) -> None:
        """
        Standardizes filenames by updating the current filename position.
        
        Args:
            current_position (int): Position to update in the filename.
        """
        self.position = current_position
        if self.is_first_update:
            if utils.re.search(r'Z[0-9]{5}_C+', self.filename_to_check):
                find_pattern = utils.re.search(r'Z[0-9]{5}_C+', self.filename_to_check)
                self.position = find_pattern.span()[0] + 1
            elif utils.re.search(r'Z[0-9]{4}_C+', self.filename_to_check):
                find_pattern = utils.re.search(r'Z[0-9]{4}_C+', self.filename_to_check)
                self.position = find_pattern.span()[0] + 1
            elif utils.re.search(r'Z[0-9]{3}_C0+', self.filename_to_check):
                find_pattern = utils.re.search(r'Z[0-9]{3}_C+', self.filename_to_check)
                self.position = find_pattern.span()[0] + 1
            elif utils.re.search(r'Z[0-9]{2}_C0+', self.filename_to_check):
                find_pattern = utils.re.search(r'Z[0-9]{2}_C+', self.filename_to_check)
                self.position = find_pattern.span()[0] + 1
            elif utils.re.search(r'Z[0-9]{1}_C0+', self.filename_to_check):
                find_pattern = utils.re.search(r'Z[0-9]{1}_C+', self.filename_to_check)
                self.position = find_pattern.span()[0] + 1
            
            self.is_first_update = False

        self.current_filename = self.filename_to_check[self.position:]

    def delete_items_of_layout(self, layout:utils.QGridLayout) -> None:
        """
        Deletes items within a specified layout.
        
        Args:
            layout (QGridLayout): The layout from which items are deleted.
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.delete_items_of_layout(item.layout())

    def perform_cut(self):
        """
        Renames files in the specified directory by standardizing their filename pattern.
        """
        print("path:",self.path)
        flag = True

        for file in utils.Path(self.path).iterdir():
            if file.is_file():
                print(file.stem)
                old_name = f"{file.stem}.tif"
                new_name = old_name[self.position:len(old_name)]
                dir = file.parent
                new_obj1 = utils.re.match(r'^[0-9]{5}_C', new_name)
                new_obj2 = utils.re.match(r'^[0-9]{4}_C', new_name)
                new_obj3 = utils.re.match(r'^[0-9]{3}_C', new_name)
                new_obj4 = utils.re.match(r'^[0-9]{2}_C', new_name)
                new_obj5 = utils.re.match(r'^[0-9]{1}_C', new_name)
                if new_obj1 != None:
                    changed_name = f"Z{new_name}"
                elif new_obj2 != None:
                    changed_name = f"Z0{new_name}"
                elif new_obj3 != None:
                    changed_name = f"Z00{new_name}"
                elif new_obj4 != None:
                    changed_name = f"Z000{new_name}"
                elif new_obj5 != None:
                    changed_name = f"Z0000{new_name}"
                else:
                    changed_name = None
                    alert = utils.QMessageBox()
                    alert.setText("Your files are not named in the correct way!")
                    alert.exec()
                    flag = False
                print(changed_name)
                if changed_name != None:
                    file.rename(utils.Path(dir, changed_name))

            elif flag:
                alert = utils.QMessageBox()
                alert.setText("You have more than one channel, please select a channel")
                alert.exec()
                flag = False


class InitWorkspace:
    """Class for initializing the workspace directory and selecting a channel for file processing."""
    def init_workspace(self, path = '/home/cellfinder_data', channel = 0):
        """
        Sets up the workspace path and verifies the channel selection.
        
        Args:
            path (str): Directory path for the workspace.
            channel (int): Channel selection, default is 0.
        
        Returns:
            str: Workspace directory path if it exists; otherwise, displays alerts.
        """
        if channel == 1:
            channel_str = "C01"
        elif channel == 2:
            channel_str = "C02"
        else:
            channel_str = ""
        if utils.os.path.exists(f"{path}/Signal/{channel_str}"):
            self.channel_chosen = channel_str
        else:
            self.channel_chosen = ""
            alert = utils.QMessageBox()
            alert.setText("Path does not exist!")
            alert.exec()
            if not utils.os.path.exists(f"{path}/Signal"):
                alert2 = utils.QMessageBox()
                alert2.setText("In this folder there is no Signal folder existent! Please choose different sample!")
                alert2.exec()

        my_working_directory = path

        if utils.os.path.exists(my_working_directory):
            self.my_working_directory = my_working_directory
            print("Working dir:", self.my_working_directory)
            print("Channel chosen:", self.channel_chosen)
            return my_working_directory
        else:
            print("Path does not exist!")

class RenameLayout:
    """Class to create and manage the GUI layout for renaming files in specified directories."""
    def rename_layout(self) -> utils.QWidget:
        """
        Creates the layout for renaming files, with options to choose workspace and set directory.
        
        Returns:
            QWidget: A tab widget containing the layout for file renaming operations.
        """
        def rename_files(_path:str, extend:str) -> None:
            """
            Renames files in a specific directory by removing whitespace and adjusting filenames.
            
            Args:
                _path (str): Path to the directory containing files.
                extend (str): Subdirectory extension ('/Auto' or '/Signal').
            """
            if not utils.os.path.exists(f"{_path}{extend}"):
                alert2 = utils.QMessageBox()
                alert2.setText("In this folder there is no Signal or Auto folder existent! Please choose different sample!")
                alert2.exec()
                return

            if utils.os.path.exists(_path):
                pathlist = [_path + extend]

                ## Remove all the tabs in the filenames
                ## Iteration over each file in Auto and Signal directories
                ## Each filename-string is iterated and a new_name string without tabs is generated by skipping every " " in the old_name.
                ## The filename becomes then substituted by the new name
                for i in pathlist:
                    for file in utils.Path(i).iterdir():
                        if file.is_file():
                            old_name = file.stem
                            print(file.stem)
                            new_name = ""
                            for i in old_name:
                                if i != " ":
                                    new_name += i
                            new_name += ".tif"
                            dir = file.parent
                            file.rename(utils.Path(dir, new_name))

                ##Selecting the right range for each filename:
                for i in pathlist:
                    filename_list = [file for file in utils.Path(i).iterdir()]
                    first_file = filename_list[0]
                    first_filename = f"{first_file.stem}.tif"
                    size_bool = False
                    string_pos = 0

                    self.rename_box = RenameBox(first_filename, size_bool, string_pos,i)
                    self.rename_box.show()

                    #self.rename_box.reject.clicked.connect(lambda: self.rename_box.update(False, self.rename_box.new_position))
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
        channel_button.insertItem(0, "")
        channel_button.insertItem(1, "C01")
        channel_button.insertItem(2, "C02")
        set_ws = utils.QPushButton("Set workspace")
        rename_button1 = utils.QPushButton("Rename files in Auto")
        rename_button2 = utils.QPushButton("Rename files in Signal")

        def choose_sample() -> None:
            """Opens a dialog for selecting the workspace directory path."""
            path = utils.QFileDialog.getExistingDirectory(self, "Choose sample data folder")
            if path != ('', ''):
                ws_path.setText(path)
            else:
                ws_path.setText("")

        inner_layout.addWidget(utils.QLabel("<b>Set Workspace:</b>"), 0, 0)
        inner_layout.addWidget(utils.QLabel("Input path of interest:"), 1, 0)
        inner_layout.addWidget(ws_path, 1, 1)
        #inner_layout.addWidget(channel_button, 1, 2)
        inner_layout.addWidget(set_ws, 1, 3)
        inner_layout.addWidget(rename_button1, 1, 4)
        inner_layout.addWidget(rename_button2, 1, 5)
        inner_layout.addWidget(choose_ws, 2, 1)
        inner_layout.addWidget(utils.QLabel("      "), 3, 0)

        choose_ws.clicked.connect(lambda: choose_sample())
        set_ws.clicked.connect(lambda: self.init_workspace(ws_path.text(), 0))
        rename_button1.clicked.connect(lambda: rename_files(_path = self.my_working_directory, extend='/Auto'))
        rename_button2.clicked.connect(lambda: rename_files(_path = self.my_working_directory, extend=f"/Signal/{self.channel_chosen}"))

        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab

