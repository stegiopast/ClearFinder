import utils
"""
Initialize Workspace, WorkingDirectory and Channel of Analysis
"""

class RenameBox(utils.QWidget):

    def __init__(self,
                 filename_to_check: str,
                 position: int,
                 _path: str):
        super().__init__()
        self.path = _path
        self.position = position
        self.rename_box = None
        self.setWindowTitle("ClearMap2 GUI")
        self.filename_to_check = filename_to_check
        self.chosen_channel = "C01"
        self.is_first_update = True
        self.shift_bar = utils.QLineEdit("0")
        self.accept = utils.QPushButton("Accept")
        self.reject = utils.QPushButton("Reject and shift")
        self.quit_renaming = utils.QPushButton("Quit Renaming")
        self.layout = utils.QGridLayout()
        self.update_layout()
        self.setLayout(self.layout)


    def update_layout(self) -> utils.QGridLayout:
        self.int_shift = int(self.shift_bar.text())
        self.new_position = self.position + self.int_shift
        if self.new_position < 0:
            self.new_position = 0
        self.update_rename_box(self.new_position)
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


    #Finds the position of Z{3|4}_C0X.tif in every filename provided by the user
    #It is mandatory to include the pattern at the end of each filename to use this application
    #Search is automatized but the user has the opportunity to change the desired position if algorithm is not precise
    def update_rename_box(self, current_position: int) -> str:
        self.position = current_position
        if self.is_first_update:
            if utils.re.search(r'Z[0-9]{5}_C0+', self.filename_to_check):
                find_pattern = utils.re.search(r'Z[0-9]{5}_C0+', self.filename_to_check)
                self.position = find_pattern.span()[0] + 1
            elif utils.re.search(r'Z[0-9]{4}_C0+', self.filename_to_check):
                find_pattern = utils.re.search(r'Z[0-9]{4}_C0+', self.filename_to_check)
                self.position = find_pattern.span()[0] + 1
            elif utils.re.search(r'Z[0-9]{3}_C0+', self.filename_to_check):
                find_pattern = utils.re.search(r'Z[0-9]{3}_C0+', self.filename_to_check)
                self.position = find_pattern.span()[0] + 1
            elif utils.re.search(r'Z[0-9]{2}_C0+', self.filename_to_check):
                find_pattern = utils.re.search(r'Z[0-9]{2}_C0+', self.filename_to_check)
                self.position = find_pattern.span()[0] + 1
            elif utils.re.search(r'Z[0-9]{1}_C0+', self.filename_to_check):
                find_pattern = utils.re.search(r'Z[0-9]{1}_C0+', self.filename_to_check)
                self.position = find_pattern.span()[0] + 1

            self.is_first_update = False

        self.current_filename = self.filename_to_check[self.position:]


    #Function for refreshing the visualization of rename window
    def delete_items_of_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.delete_items_of_layout(item.layout())


    def perform_cut(self):  # Performs the final renaming of the files
        print("path:", self.path)
        for file in utils.pathlib.Path(self.path).iterdir():
            if file.is_file():
                old_name = file.stem + ".tif"
                new_name = old_name[self.position:]
                dir = file.parent
                new_obj1 = utils.re.match(r'^[0-9]{5}_C', new_name)
                new_obj2 = utils.re.match(r'^[0-9]{4}_C', new_name)
                new_obj3 = utils.re.match(r'^[0-9]{3}_C', new_name)
                new_obj4 = utils.re.match(r'^[0-9]{2}_C', new_name)
                new_obj5 = utils.re.match(r'^[0-9]{1}_C', new_name)
                if new_obj1 != None:
                    changed_name = "Z" + new_name
                elif new_obj2 != None:
                    changed_name = "Z0" + new_name
                elif new_obj3 != None:
                    changed_name = "Z00" + new_name
                elif new_obj4 != None:
                    changed_name = "Z000" + new_name
                elif new_obj5 != None:
                    changed_name = "Z0000" + new_name
                else:
                    changed_name = None
                    alert = utils.QMessageBox()
                    alert.setText("Your files are not named in the correct way!")
                    alert.exec()

                print(changed_name)
                if changed_name != None:
                    file.rename(utils.Path(dir, changed_name))


# initalize working directory
class InitWorkspace():

    def init_workspace(self, path='/home/cellfinder_data', channel=0, choice="Hemisphere"):
        if channel == 0:
            channel_str = "C01"
        elif channel == 1:
            channel_str = "C02"
        self.chosen_channel = channel_str
        my_working_directory = path
        if choice == "Hemisphere":
            self.slicing = (slice(None),slice(None),slice(0,256))
        else:
            self.slicing = (slice(None),slice(None),slice(None))
        print(self.slicing, "Self Slicing as ", choice, "\n")
        if utils.os.path.exists(my_working_directory):
            #my_working_directory is the base directory <- alles relativ dazu
            expression_raw = 'Signal/' + channel_str + '/Z<Z,5>_' + channel_str + '.tif'  # applies for example : "Z0001_C01.tif, Z0023..."
            expression_auto = 'Auto/Z<Z,5>_' + 'C01' + '.tif'
            ws = utils.wsp.Workspace('CellMap', directory=my_working_directory)

            #This update is necessary to evoke usage of more than one channel
            ws.update(raw_C01='Signal/C01/Z<Z,5>_C01.tif',
                      raw_C02='Signal/C02/Z<Z,5>_C02.tif',
                      stitched_C01='stitched_C01.npy',
                      stitched_C02='stitched_C02.npy',
                      resampled_C01='resampled_C01.tif',
                      resampled_C02='resampled_C02.tif')
            if self.chosen_channel == "C01":
                ws.update(raw_C01=expression_raw, autofluorescence=expression_auto)
            if self.chosen_channel == "C02":
                ws.update(raw_C02=expression_raw, autofluorescence=expression_auto)

            if utils.os.path.exists(my_working_directory + '/stitched_' + self.chosen_channel + '.tif'):
                expression_stitched = 'stitched_' + self.chosen_channel + '.npy'
                if self.chosen_channel == "C01":
                    ws.update(stitched_C01=expression_stitched)
                if self.chosen_channel == "C02":
                    ws.upate(stitched_C02=expression_stitched)

            if utils.os.path.exists(my_working_directory + '/resampled_' + self.chosen_channel + '.tif'):
                expression_resampled = 'resampled_' + self.chosen_channel + '.tif'
                if self.chosen_channel == "C01":
                    ws.update(resampled_C01=expression_resampled)
                if self.chosen_channel == "C02":
                    ws.update(resampled_C02=expression_resampled)
            ws.info()
            print(ws.filename('cells', postfix='raw_C01'))
            self.ws = ws
            self.my_working_directory = my_working_directory

            print("Worksapce: ", self.ws)
            print("Working dir:", self.my_working_directory)
            print("Channel chosen:", self.chosen_channel)
            return [ws, my_working_directory]
        else:
            alert = utils.QMessageBox()
            alert.setText("Path does not exist!")
            alert.exec()


class RenameLayout:
    def rename_layout(self):


        def choose_sample():
            path = utils.QFileDialog.getExistingDirectory(self, "Choose sample data folder")
            if path != ('', ''):
                ws_path.setText(path)
            else:
                ws_path.setText("")


        def rename_files(_path, extend):
            if utils.os.path.exists(_path + extend):
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

                    string_pos = 0

                    self.rename_box = RenameBox(first_filename, string_pos, i)
                    self.rename_box.show()


                    self.rename_box.reject.clicked.connect(self.rename_box.update_layout)
                    self.rename_box.reject.clicked.connect(self.rename_box.repaint)


                    self.rename_box.accept.clicked.connect(self.rename_box.perform_cut)
                    self.rename_box.accept.clicked.connect(self.rename_box.close)

                    # Next line is implemented to quit the application in case a renaming is not possible.
                    # self.rename_box.quit_renaming.clicked.connect(lambda: self.rename_box.update(False,4000000))
                    self.rename_box.quit_renaming.clicked.connect(self.rename_box.close)

            else:
                alert = utils.QMessageBox()
                alert.setText("Path does not exist! Please check github documentation to select the workspace correctly.")
                alert.exec()


        tab = utils.QWidget()
        outer_layout = utils.QVBoxLayout()
        inner_layout = utils.QGridLayout()

        ## Widget for input path
        ws_path = utils.QLineEdit("")
        choose_workspacedir_button = utils.QPushButton("Pick Workspace Directory")

        channel_button = utils.QComboBox()
        channel_button.insertItem(0, "C01")
        channel_button.insertItem(1, "C02")
        set_ws = utils.QPushButton("Set workspace")
        rename_button1 = utils.QPushButton("Rename files in Auto")
        rename_button2 = utils.QPushButton("Rename files in Signal C01")
        rename_button3 = utils.QPushButton("Rename files in Signal C02")
        testdata = utils.QComboBox()
        testdata.insertItem(0, "Border region")
        testdata.insertItem(1, "Background region")
        make_testdata = utils.QPushButton("Make Testdata")
        debug_button = utils.QPushButton("Test Mode")
        debug_button.setCheckable(True)
        hemisphere_whole_brain = utils.QComboBox()
        hemisphere_whole_brain.insertItem(0,"Hemisphere")
        hemisphere_whole_brain.insertItem(1,"Whole brain")

        ##
        inner_layout.addWidget(utils.QLabel("<b>Set Workspace:</b>"), 0, 0)
        inner_layout.addWidget(utils.QLabel("Input path of interest:"), 1, 0)
        inner_layout.addWidget(ws_path, 1, 1)
        inner_layout.addWidget(choose_workspacedir_button, 1, 2)
        inner_layout.addWidget(channel_button, 1, 3)
        inner_layout.addWidget(hemisphere_whole_brain, 1,4)
        inner_layout.addWidget(set_ws, 1, 5)
        inner_layout.addWidget(rename_button1, 1, 6)
        inner_layout.addWidget(rename_button2, 1, 7)
        inner_layout.addWidget(rename_button3, 1, 8)
        inner_layout.addWidget(utils.QLabel("      "), 2, 0)
        inner_layout.addWidget(utils.QLabel("<b>Testdata option:</b>"), 3, 0)
        inner_layout.addWidget(make_testdata, 4, 0)
        inner_layout.addWidget(testdata, 4, 1)
        inner_layout.addWidget(debug_button, 5, 0, 5, 4)

        choose_workspacedir_button.clicked.connect(lambda: choose_sample())
        set_ws.clicked.connect(lambda: self.init_workspace(ws_path.text(), channel_button.currentIndex(),hemisphere_whole_brain.currentText()))
        rename_button1.clicked.connect(lambda: rename_files(_path=self.my_working_directory, extend='/Auto'))
        rename_button2.clicked.connect(lambda: rename_files(_path=self.my_working_directory, extend='/Signal/C01'))
        rename_button3.clicked.connect(lambda: rename_files(_path=self.my_working_directory, extend='/Signal/C02'))
        make_testdata.clicked.connect(lambda: self.createTestdata(index=testdata.currentIndex()))


        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab
