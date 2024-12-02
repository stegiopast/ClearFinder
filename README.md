![GitHub Release](https://img.shields.io/github/v/release/stegiopast/ClearFinder?include_prereleases) 
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/stegiopast/ClearFinder/total)

# General information

ClearFinder GUI is designed to assist working with ClearMap and Cell Finder, two tools for cell counting and atlas annotation of intact volumes of mouse brains. The data required for the applications is generated on a light-sheet microscope. The samples are whole mouse brains or hemispheres subjected to iDISCO+ tissue immunostaining and clearing protocol. Every sample requires an autofluorescence (Auto) and a signal datasets. The Auto is imaged in 488nm channel, therefore it's recommended to avoid the secondary antibodies coupled to fluorophores in this range for immunostaining. To result in good signal to noise ratio, it is recommended to use secondaries in red and far-red part of the spectrum. The quality of your analysis highly depends on the quality of the data: sample preparation, data acquisition and data preprocessing are steps that need to be optimized before starting with CellFinder.

```diff
- Always work with copies of the original datasets, since images could be converted or resized in order to enable the processing. Please never use the original data and always prepare backups
```

# ClearFinder
## Installation

Open your terminal (Ctrl + Alt + T) or manually on the desktop.

### 1. Download github repository

```bash
cd ~
git clone git@github.com:stegiopast/ClearFinder.git
cd ClearFinder
git submodule update --recursive --init
```

### 2. Download conda if not installed

  -> For linux x86_64 based distributions use the following code snippet, otherwise visit anaconda.com and follow the installation instructions for your distribution.

```bash
cd ~
wget https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
bash ~/Anaconda3-2022.05-Linux-x86_64.sh
source ~/.bashrc
conda update conda
```

Please follow the instructions of the conda installation guide

### 3. install different environments

#### Cellfinder_env

Please install all drivers of your graphics device on the computer to make sure your GPU is working.
You can find help with your GPU Setup on:
<https://docs.brainglobe.info/cellfinder/installation/using-gpu>
<https://www.nvidia.com/download/index.aspx>

```bash
conda env create -f ~/ClearFinder/Cellfinder/requirements_04_11.yml
```

Please check if the GPU is available for tensorflow:
```bash
conda activate Cellfinder_env
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
python
```
```python
import tensorflow as tf
tf.test.is_gpu_available()
quit()
```
```bash
conda deactivate
```
The GPU is available if the tensorflow function output shows True in the final row.



#### Clearmap_env

```bash
conda env create -f ~/ClearFinder/ClearMap/requirements_04_11.yml
```

Clearmap needs to be compiled in the first run (runtime ~30mins)
```bash
conda activate Clearmap_env
cp ~/ClearFinder/ClearMap/compile.py ~/ClearFinder/ClearMap/ClearMap2/compile.py
cd ~/ClearFinder/ClearMap/
python ClearMap2/compile.py
conda deactivate
cd ~
```

#### Napari_env
```bash
conda env create -f Napari/requirements_04_11.yml
conda activate Napari_env
napari
conda deactivate
```
Once you start napari be aware to download the "cellfinder-napari" and "brainglobe-napari-io" plugins in the tab menu under Plugin -> Install/ Uninstall plugins.
Type napari-cellfinder in the search bar and install the plugin. Restart napari for the plugin to be integrated.


### 4.Start the application

```bash
cd ~/ClearFinder
bash ./start_guis.sh
```

### 5.Alternative start

Note that with it's first start ClearMap needs to be compiled, which takes around half an hour if not performed during the installation as mentioned above. Until then, the GUI window will not appear. If you want to circumvent this problem and see how the compilation performs, run:

```bash
conda activate Clearmap_env
python3 ~/ClearFinder/ClearMap/gui.py
conda deactivate
```

Similarly the other GUIs can be started separately in a similar way.

For Cellfinder type:

```bash
conda activate Cellfinder_env
python3 ~/ClearFinder/Cellfinder/gui.py
conda deactivate
```

For napari type:

```bash
conda activate Napari_env
napari
conda deactivate
```

### 6.Create an alias in the ~/.bashrc file for quickstart

Create a command alias in the ~/.bashrc file:

If you want to use the nextflow version:
```bash
# Replace path/to/ClearFinder by your real path
echo "alias ClearFinder=\"cd path/to/ClearFinder && bash start_guis.sh\"" >> ~/.bashrc
source ~/.bashrc
```
If you want to evoke it directly from the shell:

From now on, you can start the applications with the following command:

```bash
ClearFinder
```

## ClearMap usage

For the usage of ClearMap a few things have to be considered:

### Data organization for the software:
-> We follow a strict filename structure:

    All files should end with the following pattern -> *ZX[3-4]_C0Y.tif -> (X is the number of the optical plane, it can be a number between 0-9 and must consist of at least three numbers (000-9999), Y can be a number between 1-2)
    Files have to be converted to tif format.\

-> Additionally we follow a strict folder structure:

```
Sample_folder
│
│
│
└───Auto
│   |   *ZXXXX_C01.tif
│
│
└───Signal
    │
    |
    |
    └───C01
    |   |    *ZXXXX_C01.tif
    |
    |
    └───C02
        |    *ZXXXX_C02.tif
```


   Be aware that also the autofluorescence images need a _C01 signature in the filename.

```diff
-> Always work with copies of the original datasets, since images could be converted or resized in order to enable the processing. Please never use the original data and always prepare backups
```

### Determine Path | Rename samples

```diff
- Always use a copy of your original data for processing ! Make backups !
```
With this tab a ClearMap workspace can be initialized. The following steps should be performed:

1. Choose a Workspace by pressing the "Pick Workspace Directory" button. A dialogue window will open where one needs to choose the sample_folder of interest.
2. The channel of interest (C01,C02) should be selected by choosing from the box beside the "Pick Workspace Directory" button.
3. One should clarify whether the sample is a single hemisphere or a whole brain. This can also be chosen from the Box beside the channel box.
4. The Workspace can be initialized by clicking the "set workspace" button.
5. The "Rename buttons" will allow the renaming of files in the respective channels. Clicking the button will open a Rename window. The renaming is semi-automatized so that a representative file within the folder is shortened to the pattern ZX[3-4]_C0Y.tif. (The shown filename in the rename window should be between Z000_C0Y.tif-Z9999_C0Y.tif). If the filenames are matching the pattern continue the renaming by clicking the "Accept" button in the renaming window. This will perform a renaming of all the files within Auto, Signal->C01 or Signal->C02 respectively. It is necessary to rename the files in order to automatize the cell detection.
6. After files are renamed one can continue with the resampling step.

### Resampling

1. Please insert information about the resolution of signal_channel and atlas images as micrometer per pixel values for the X,Y,Z dimensions at Resample parameters.
2. Similarly, insert information about the resolution of auto_channel and the reference atlas images for the X,Y,Z dimensions at Resample parameters.
3. By inserting a filename the inserted resolutions can be saved and loaded for later experiments. (A unique basename has to be used)
4. Add the orientation of the brain. The default settings match the orientation of the side of the right hemisphere facing the camera. For more information about which orientation to choose, visit [here](https://clearanatomics.github.io/ClearMapDocumentation/scripts/cell_map_tutorial.html)
5. Resampling can be started by clicking the "Resample" button.


This process usually takes around 10-20 minutes.

### Cell-detection and atlas assignment

1. For Cell detection we inserted default values that were tailored to our experiments. For each experiments the optimal values can vary. Please visit [here](https://clearanatomics.github.io/ClearMapDocumentation/scripts/cell_map_tutorial.html) for more information. The possible processing settings are all based on options provided by ClearMap2.
2. Please be aware that usually only half of the available threads should be used since the usage of working memory is extraordinary high with more threads. We used 10 parallel processes with 128GB RAM. We recommend 5 threads for 64GB RAM machines.
3. Once the preferred settings are selected, one can start the cell detection by clicking the "Detects cells" button.
4. After cell detection, one has to perform the alignment to the reference atlas by clicking the "Atlas assignment" button.

These two processes are executed in 2-3 hours, depending on the machine and the amount of detected cells.
The process has several files as an output. The embedded_ontology.csv files can be used for further quantification analysis. Files that have been produced in the C0YXmlFiles folders can be used together with the Signal tif-files for visualization in napari to validate the cell detection. Cells that are stored in the universe.xml or no_label.xml files were detected as maximas, but could not be aligned to a reference region.

### Grouping and Normalization of data

In this tab, data of samples form different conditions can be created. The process will create raw count files and counts that summarize the detected cell counts over different hierarchical structures based on the ontology of Allen Brain atlas. Data can be normalized as "median of ratio" or "cellcounts per million" . Additionally, a logarithmic conversion can be performed. A metadata file can be exported for further analytical processing. It is recommended to at least use three samples per condition for further analysis.

1. Press the "add analysis" button to open a file dialogue and choose an embedded_ontology_C0Y.csv file from the sample_folder of interest. Press "Open" on the dialogue window to confirm your choice. If you made a wrong choice, remove the last selection with "Remove last file"
2. The chosen files should appear in the list below.
3. Once your selection is completed, determine an output path by clicking the "Set output dir" button. This opens a folder dialogue window. Create or select an output folder for your count file and press "Open". If you want to normalize your data please choose a normalization option. If you want raw counts, just use the "None" option. After the selection press "Create analysis data". Two count files with the raw or normalized counts of hierarchically embedded and non-embedded data will be written into your output folder.
4. After the creation of the count files a metadata file is required for condition wise comparison. Please insert the sample names (matching the sample_folder names) and the condition name into the Metadata table on the right side of the tab. Click "Save metadata" to write a metadata.csv

5. Additionally to the metadata.csv a list_information.csv is exported, which allows the analysis of the dataset over different ontology hierarchies.

### Preliminary analysis

All the datsets you need for the following step should be located in the output_folder you defined in the last step

1. Choose an input count file by clicking the "Choose input file button". You can load either hierarchical or non-hierarchical counts.
2. Similarly to step 1, choose the metadata.csv file.
3. Similarly to step 1, choose the list_information.csv file.
4. After the selection of the 3 files please press "Set input and metadata" to confirm your choice.
5. Press the "PCA" button to perform a principal component analysis.
6. For the cell count heatmap, you can choose one of the brain regions and its hierarchical subregions that you are interested in or filter for a specific hierarchical level. Press the "Heatmap" button.
7. With the boxplot one can have an insight in the counts distribution of a specific region of interest. Please choose a region of interest and press the "Boxplot" button.

You can search for the existence of regions in the table on the right side of the tab.

## Cellfinder usage

### Data organization for the software:

-> We follow a strict filename structure:

   All files should end with the following pattern -> *ZX[3-4]_C01.tif -> (X is the number of the optical plane, it can be a number between 0-9 and must consist of at least three numbers (000-9999))

   Be aware that Cellfinder only works with a single signal channel right now.
   If you want to process 2 signal channels, please split the datasets up in different folders.


 -> Additionally we follow a strict folder structure:

```
Sample_folder
│
│
│
└───Auto
│   |   *ZXXXX_C01.tif
│
│
└───Signal
    |   *ZXXXX_C01.tif
```

   Be aware that also the autofluorescence images need a _C01 signature in the filename.

```diff
- Always work with copies of the original datasets, since images could be converted or resized in order to enable the processing. Please never use the original data and always prepare backups
```

### Determine Path and rename samples

```diff
- Always use a copy of your original data for processing ! Make backups !
```

With this tab a CellFinder workspace can be initialized. The following steps should be performed:

1. Choose a Workspace by pressing the "Choose sample" button. A dialogue window will open where one needs to choose the sample_folder of interest.
2. The Workspace can be initialized by clicking the "set workspace" button.
3. The "Rename buttons" will allow the renaming of files in the respective channels. Clicking the button will open a Rename window. The renaming is semi-automatized so that a representative file within the folder is shortened to the pattern ZX[3-4]_C0Y.tif. (The shown filename in the rename window should be between Z000_C0Y.tif-Z9999_C0Y.tif). If the filenames are matching the pattern continue the renaming by clicking the "Accept" button in the renaming window. This will perform a renaming of all the files within Auto or Signal respectively. It is necessary to rename the files in order to automatize the cell detection.
4. After files are renamed one can continue with the resampling step.

Note that Cellfinder is currently only capable of processing whole brain images. Additionally, only a single signal folder per sample can be processed. If you want to process two channels, please copy the sample folder and create a signal folder with the repective image files for the channel of interest. Additionally, be aware not to use your original data, but a copy of it. Images will be resized in further steps if they do not have the same size.

### Resampling

1. For resampling please insert the voxel size in micrometer per pixel X,Y,Z for Signal and Auto to determine the resolution.
2. Press "Start preprocessing"

The resampling will resize your images, if they do not have the same size. We recommend once again to only use copies of your original data. In case the images have to be resized, be aware that also the voxel sizes change respectively and will be stored in a voxel_sizes_file within the sample folder. If you plan to resample the same data more than once please use the new voxel_sizes after the first attempt.

### Cell-detection and atlas assignment

1. Insert the number of CPUs that your computer is able to process (We used 8)
2. Insert a threshold, being defined as the minimal amount of standard deviations above mean illumination, in order to consider a spot as maximum (Integer)
3. Insert a mean soma diameter of your cells (Integer)
4. Insert the mean cell size in xy plane (Integer)
5. Insert the gaussian filter variable (Float, 0.2 is default)
6. If you want to use your own trained model please pick a model file in .h5 format, otherwise leave the entry free to use the default model
7. Please insert the orientation of your brain during acquisition. You have to explain which directional part of the brain will occur first when passing through the first image of the stack starting from the upper left corner. Choose one orientation out of anterior/posterior ("a"/"p"), superior/inferior ("s"/"i") and left/right ("l"/"r"). Our default is the anterior ("a"), superior ("s"), left ("l") part of the brain. --> asl
8. Click "Start cell detection"
9. After cell detection, one has to click "Embed ontology" to obtain a count file comparable to ClearMap data.

### Network training

Training data can be generated with the Cellfinder plugin of napari. Please check the documentation [here](https://docs.brainglobe.info/cellfinder-napari/user-guide/training-data-generation).

1. After generating the training data, click on "Choose Yaml" which opens a dialogue window. Navigate to the yaml file created with the cellfinder-napari plugin.
2. Choose a pretrained model, if you want to continue training a custom model. A dialogue window will open where you have to choose a file that contains a model you want to continue training on. The file is in .h5 format. Click open in the dialogue window to proceed.
3. Click on "Continue training" to use the custom model as template model for continuation of the training.
4. Choose a test fraction the program will use as subset for the model training during an epoch.
5. Determine the learning rate used for backpropagation during the weight changes of the neural network.
6. Determine a batch size in which the data will be processed. The bigger the batch size, the more demanding it will be for your GPU computation. (Default: 32, Options: 8,16,32,64).
7. Determine the number of epochs you want to perform during network training.
8. Choose a directory or create a new one to store your data. Click on "Choose your base directory" to open a dialogue window. By clicking on the "folder+" icon on the dialogue you can create a new window. Rename the newly created folder and proceed by clicking "Choose".
9. Start the network training by clicking the "Train network" button.

### Grouping and Normalization of data

In this tab data of samples from different conditions can be created. The process will create raw count files and counts that summarize the detected cell counts over different hierarchical structures, based on the ontology of the Allen Brain Atlas. Data can be normalized as "median of ratio" or "cellcounts per million". Additionally, a logarithmic conversion can be performed. A metadata file can be exported for further analytical processing. It is recommended to at least use three samples per condition for further analysis.

1. Press the "add analysis" button to open a file dialogue and choose an embedded_ontology_C0Y.csv file from the sample_folder of interest. Press "Open" on the dialogue window to confirm you choice. If you made a wrong choice, remove the last selection with "Remove last file"
2. The chosen files should appear in the list below.
3. Once your selection is completed determine an output path by clicking the "Set output dir" button. This opens a folder dialogue window. Create or select an output folder for your count file and press "Open". If you want to normalize your data please choose a normalization option. If you want raw counts just use the "None" option. After the selection press "Create analysis data". Two count files with the raw or normalized counts of hierarchically embedded and non embedded data will be written into your output folder.
4. After the creation of the count files, a metadata file is required for condition wise comparison. Please insert the sample names (matching the sample_folder names) and the condition name into the Metadata table on the right side of the tab. Click save metadata to write a metadata.csv
5. Additionally to the metadata.csv a list_information.csv is exported, which allows the analysis of the dataset over different ontology hierarchies.

### Preliminary analysis

All the datasets you need for the following step should be located in the output_folder you defined in the last step

1. Choose an input count file by clicking the "Choose input file button". You can load either hierarchical or non-hierarchical counts.
2. Similarly to step 1, choose the metadata.csv file.
3. Similarly to step 1, choose the list_information.csv file.
4. After the selection of the 3 files please press "Set input and metadata" to confirm your choice.
5. Press the "PCA" button to perform a principal component analysis.
6. For the cell count heatmap you can choose one of the brain regions and their hierarchical subregions that you are interested in or filter for a specific hierarchical level. Press the "Heatmap" button.
7. With the boxplot one can have an insight in the counts distribution of a specific region of interest. Please choose a region of interest and press the "Boxplot" button.

You can search for the existence of regions in the table on the right side of the tab.

### Processing of ClearMap and Cellfinder after Atlas alignment

The application is designed to produce similar output data from Cellfinder and ClearMap to enable the comparison of both software packages. The grouping and normalization step can therefore be performed together with samples of one or the other processing tool. Be aware that we do not guarantee the scientific relevance of your findings. Be aware the statistical meaningfulness of the experiment still lies on the users responsibility. Be careful which data you use or combine and how you normalize it.


### Visualisation with napari

Before starting with the visualization you will need to install two plugins. For that please open napari and click on Plugins -> Install/Uninstall Plugins.
A new window will pop up. Please type cellfinder-napari in the filter section at the top of the new window. Click on the blue install button.
After that please type brainglobe-napari-io in the filter section. Click on the blue install button. Please restart napari to complete the installation of both plugins.


In order to visualize images of signal and autofluorscent channels, one can click on:  File -> Open folder -> Signal_folder (In dialogue window)

The detected maxima can be visualized with the output files of Cellfinder and Clearmap in xml format. These files can be found in the following folders:

Cellfinder
```
Sample_folder
│
│
│
└───points
    |   cell_classification.xml

```


ClearMap

```
Sample_folder
│
│
│
└───C0XxmlFiles
    |  cells_C0X.xml

```

The output xml files can be opened in napari after the plugin installation. Click File -> Open File(s) -> *.xml


## Copyright

### Cellfinder

The following copyright and disclaimers have to be mentioned in order to publish code related to Cellfinder:

Copyright (c) 2020, University College London
All rights reserved.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### Napari

The following copyright and disclaimers have to be mentioned in order to publish code related to Napari:

Copyright (c) 2018, Napari
All rights reserved.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Reference
We are currently working on a preprint


## Contact

Please open an issue if you encounter any issues/troubles. However, please go over the previous issues (including closed issues) before opening a new issue, as your same exact question might have been already answered previously. Thank you!



