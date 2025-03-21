import utils

# Contains all features of the grouping and normalization tab

class Preprocessing:
    """
    A class for handling preprocessing operations related to resizing images and adjusting voxel sizes for analysis.

    Attributes:
        my_working_directory (str): Directory containing the files to process.
        channel_chosen (str): Specific channel chosen for processing, if applicable.
    """
    def resize_pictures(self, _voxel_size_signal_x:int = 5, _voxel_size_signal_y:int = 2, _voxel_size_signal_z:int = 2, 
                              _voxel_size_auto_x:int = 5, _voxel_size_auto_y:int = 2, _voxel_size_auto_z:int = 2) -> None:
        """
        Resizes images within the specified directory, adjusting voxel sizes based on input parameters.

        Args:
            _voxel_size_signal_x (int, optional): Voxel size in the X direction for signal images.
            _voxel_size_signal_y (int, optional): Voxel size in the Y direction for signal images.
            _voxel_size_signal_z (int, optional): Voxel size in the Z direction for signal images.
            _voxel_size_auto_x (int, optional): Voxel size in the X direction for auto images.
            _voxel_size_auto_y (int, optional): Voxel size in the Y direction for auto images.
            _voxel_size_auto_z (int, optional): Voxel size in the Z direction for auto images.
        """
        if self.my_working_directory != "":
            filepath = self.my_working_directory
            print(filepath)
            print(utils.os.path.exists(filepath))
            filepath_auto = str(f"{filepath}/Auto/")
            print(filepath_auto)
            filepath_signal = str(f"{filepath}/Signal/")
            if self.channel_chosen != "":
                filepath_signal = f"{filepath_signal}{self.channel_chosen}/"
            print(filepath_signal)

            filenames_auto = []
            filenames_signal = []

            for base,dirs,files in utils.os.walk(filepath_auto):
                filenames_auto = files

            for base,dirs,files in utils.os.walk(filepath_signal):
                filenames_signal = files

            print(len(filenames_auto),len(filenames_signal))

            filenames_auto = utils.natsorted(filenames_auto, reverse=False)
            filenames_signal = utils.natsorted(filenames_signal, reverse=False)

            #print("Filenames Auto ",filenames_auto,"\nFilenames Signal:",filenames_signal)

            if len(filenames_auto) != len(filenames_signal):
                difference = abs(len(filenames_auto) - len(filenames_signal))
                if len(filenames_auto) > len(filenames_signal):
                    longer_array = filenames_auto
                    # shorter_array = filenames_signal
                    longer_str = "/Auto"
                else:
                    longer_array = filenames_signal
                    # shorter_array = filenames_auto
                    longer_str = "/Signal"

                print(longer_array)

                if (difference % 2) == 0:
                    front = difference // 2
                    back = difference // 2
                else:
                    front = difference // 2 + 1
                    back = difference // 2

                moved_filepath = f"{filepath}{longer_str}_moved"
                if not utils.os.path.exists(moved_filepath):
                    utils.os.mkdir(moved_filepath)
                else:
                    print("File existed")

                for i in range(front):
                    print(longer_array[0])
                    utils.os.remove(f"{filepath}{longer_str}/{longer_array[0]}")
                    longer_array.pop(0)

                for j in range(0,back):
                    print(longer_array[-1])
                    utils.os.remove(f"{filepath}{longer_str}/{longer_array[-1]}")
                    longer_array.pop()

                    print("Same lenght now ?:", len(filenames_auto) == len(filenames_signal))

            else:
                print("Lengths are equal\n")

            flag = True
            for i,j in zip(filenames_auto,filenames_signal):

                #im1 = img_as_uint(filepath_auto + i)
                #im2 = img_as_uint(filepath_auto + j)

                im1 = utils.Image.open(f"{filepath_auto}{i}")
                im2 = utils.Image.open(f"{filepath_signal}{j}")

                if im1.size != im2.size:
                    print("I'm in if")

                    pixel_growth_x_signal = im2.size[0] / 2050#im1.size[0]
                    pixel_growth_y_signal = im2.size[1] / 3500#im1.size[1]

                    pixel_growth_x_auto = im1.size[0] / 2050
                    pixel_growth_y_auto = im1.size[1] / 3500

                    print("Image 1 size", im1.size)
                    print("Image2 size", im2.size)
                    #new_signal_size_x =  (im1.size[0] / im2.size[0]) * im2.size[0]
                    #new_signal_size_y = (im1.size[1] / im2.size[1]) * im2.size[1]

                    new_size = (3500,2050)

                    im1 = utils.np.asarray(im1)
                    im2 = utils.np.asarray(im2)

                    print("Image1 old shape: ", im1.shape)
                    print("Image2 old shape: ", im2.shape)

                    im1 = utils.resize(im1,new_size)
                    im2 = utils.resize(im2,new_size)

                    print("Image 1 new shape: ", im1.shape)
                    print("Image 2 new shape: ", im2.shape)

                    im1 = utils.img_as_uint(im1)
                    im2 = utils.img_as_uint(im2)

                    im1 = utils.Image.fromarray(im1)
                    im2 = utils.Image.fromarray(im2)

                    print("Image 1 new size", im1.size)
                    print("Image 2 new size", im2.size)

                    im1.save(f"{filepath_auto}{i}")
                    im2.save(f"{filepath_signal}{j}")
                
                else:
                    pixel_growth_x_signal = 1
                    pixel_growth_y_signal = 1

                    pixel_growth_x_auto = 1
                    pixel_growth_y_auto = 1

                voxel_filepath = f"{self.my_working_directory}/{self.channel_chosen}_voxel_size_signal"
                if not utils.os.path.exists(voxel_filepath):
                    utils.os.mkdir(voxel_filepath)

                new_voxel_size_x = _voxel_size_signal_x * pixel_growth_x_signal
                new_voxel_size_y = _voxel_size_signal_y * pixel_growth_y_signal 
                new_voxel_size_z = _voxel_size_signal_z

                with open(f"{voxel_filepath}/voxel_sizes.txt", "w") as file:
                    file.write(str(new_voxel_size_x))
                    file.write(",")
                    file.write(str(new_voxel_size_y))
                    file.write(",")
                    file.write(str(new_voxel_size_z))

                voxel_filepath = f"{self.my_working_directory}/voxel_size_auto"
                if not utils.os.path.exists(voxel_filepath):
                    utils.os.mkdir(voxel_filepath)

                new_voxel_size_x = _voxel_size_auto_x * pixel_growth_x_auto
                new_voxel_size_y = _voxel_size_auto_y * pixel_growth_y_auto
                new_voxel_size_z = _voxel_size_auto_z

                with open(f"{voxel_filepath}/voxel_sizes.txt", "w") as file:
                    file.write(str(new_voxel_size_x))
                    file.write(",")
                    file.write(str(new_voxel_size_y))
                    file.write(",")
                    file.write(str(new_voxel_size_z))

                print("Finished work!")

        else:
            self.warning_ws()


class PreprocessingLayout:
    """
    A class to construct and manage the GUI layout for preprocessing tasks, including voxel size selection.

    Methods:
        preprocess_layout(): Creates and returns the layout for the preprocessing tab.
    """
    def preprocess_layout(self) -> utils.QWidget:
        """
        Sets up the preprocessing layout including widgets for voxel size input and a start button.

        Returns:
            QWidget: The tab widget containing the layout for preprocessing.
        """
        tab = utils.QWidget()
        outer_layout = utils.QVBoxLayout()
        inner_layout = utils.QGridLayout()
        ### Widgets for determining voxel size
        voxel_size_signal_x = utils.QLineEdit("5.00")
        voxel_size_signal_y = utils.QLineEdit("2.00")
        voxel_size_signal_z = utils.QLineEdit("2.00")
        voxel_size_auto_x = utils.QLineEdit("5.00")
        voxel_size_auto_y = utils.QLineEdit("2.00")
        voxel_size_auto_z = utils.QLineEdit("2.00")

        ### Widgets for starting Prepprocessing
        start_preprocess_button = utils.QPushButton("Start Preprocessing")

        ### Visualization of Widgets for preprocessing tab on GUI
        inner_layout.addWidget(utils.QLabel("<b>Insert voxel sizes: <\b>"), 0, 0)

        inner_layout.addWidget(utils.QLabel("Voxel size Signal X:"), 1, 0)
        inner_layout.addWidget(voxel_size_signal_x, 1, 1)

        inner_layout.addWidget(utils.QLabel("Voxel size Signal Y:"), 2, 0)
        inner_layout.addWidget(voxel_size_signal_y, 2, 1)

        inner_layout.addWidget(utils.QLabel("Voxel Size Signal Z:"), 3, 0)
        inner_layout.addWidget(voxel_size_signal_z, 3, 1)

        inner_layout.addWidget(utils.QLabel("Voxel size Auto X:"), 4, 0)
        inner_layout.addWidget(voxel_size_auto_x, 4, 1)

        inner_layout.addWidget(utils.QLabel("Voxel size Auto Y:"), 5, 0)
        inner_layout.addWidget(voxel_size_auto_y, 5, 1)

        inner_layout.addWidget(utils.QLabel("Voxel Size Auto Z:"), 6, 0)
        inner_layout.addWidget(voxel_size_auto_z, 6, 1)


        inner_layout.addWidget(start_preprocess_button, 7, 0)

        ### Connection of button and preprocessing function
        start_preprocess_button.pressed.connect(lambda: self.resize_pictures(_voxel_size_signal_x = float(voxel_size_signal_x.text()),
                                                                             _voxel_size_signal_y = float(voxel_size_signal_y.text()),
                                                                             _voxel_size_signal_z = float(voxel_size_signal_z.text()),
                                                                             _voxel_size_auto_x = float(voxel_size_auto_x.text()),
                                                                             _voxel_size_auto_y = float(voxel_size_auto_y.text()),
                                                                             _voxel_size_auto_z = float(voxel_size_auto_z.text())))

        outer_layout.addLayout(inner_layout)
        outer_layout.addStretch()
        tab.setLayout(outer_layout)
        return tab
