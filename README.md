# ClearFinder
## Installation

Open your terminal (Ctrl + Alt + T) or manually on the desktop.

### 1. Download github repository

```
cd ~
git clone git@github.com:stegiopast/ClearFinder.git
sudo chown your_local_username ~/ClearFinder -R
cd ~/ClearFinder/ClearMap
git clone git@github.com:ChristophKirst/ClearMap2.git
mv ClearMap2/ClearMap ~/ClearFinder/ClearMap
```

### 2. Download conda if not installed
  -> For linux x86_64 based distributions use the following code snippet, otherwise visit anaconda.com and follow the installation instructions for your distribution.

```
cd ~
wget https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
bash ~/Anaconda3-2022.05-Linux-x86_64.sh
source ~/.bashrc
```


Please follow the instructions of the conda installation guide

### 3. install nextflow 

```
conda install -c bioconda nextflow
```
Please follow the instructions of the nextflow installation guide

### 4. install different environments

Cellfinder_env
```
conda env create -n Cellfinder_env python=3.9
conda activate Cellfinder_env
pip install cellfinder
conda deactivate
```

Clearmap_env
```
conda env create --file ~/Brainmap_dev/ClearMap/requirements.yml
```

Napari_env
```
conda env create -y -n Napari_env -c conda-forge python=3.9
conda activate Napari_env
pip install napari[all]
conda deactivate
```

### 5.Start the application

```
cd ~/ClearFinder
nextflow run start_guis.nf
```
Once you start napari be aware to download the napari-cellfinder plugin in the tab menu under Plugin -> Install/ Uninstall plugins.
Type napari-cellfinder in the search bar and install the plugin. Restart napari for the plugin to be integrated. 


### 6.Alternative start

Note that with it's first start ClearMap needs to be compiled, which takes around half an hour. Until then, the GUI window will not appear. If you want to circumvent this problem and see how the compilation performs, run:

```
conda activate Clearmap_env
python3 ~/ClearFinder/ClearMap/gui.py
conda deactivate
```

Similarly the other GUIs can be started sperately in a similar way.

For Cellfinder type:
```
conda activate Cellfinder_env
python3 ~/ClearFinder/Cellfinder/gui.py
conda deactivate
```
For napari type:
```
conda activate Napari_env
napari
conda deactivate
```

### 7.Create an alias in the ~/.bashrc file for quickstart
```
sudo apt-get install gedit
gedit ~/.bashrc
```

Insert the following line in the ~/.bashrc file that should open in the text editor:

```
alias ClearFinder="cd path/to/ClearFinder && nextflow run start_guis.nf"
```

Safe the file with Ctrl+S or with the save button of the editor. Then close the editor and get back to the terminal. Type:

```
source ~/.bashrc
```

From now on, you can start the applications with the following command:

```
ClearFinder
```

## Usage

### ClearMap

For the usage of ClearMap a few things have to be considered:

#### Data organization for the software:
-> We follow a strict filename structure:

    All files should end with the following pattern -> *ZX[3-4]_C0Y.tif -> (X is the number of the optical plane, it can be a number between 0-9 and must consist of at least three numbers (000-9999), Y can be a number between 1-2)
    Files have to be converted to tif format.\

-> Additionally we follow a strict folder structure:\
   Sample_folder\
      |\
      -> Auto -> *ZXXXX_C01.tif\
      |\
      |\
      -> Signal\
            &emsp;|\
            &emsp;-> C01 -> *ZXXXX_C01.tif \
            &emsp;|\
            &emsp;-> C02 -> *ZXXXX_C02.tif \

   Be aware that also the autofluorescence images need a _C01 signature in the filename.
 
 -> Always work with copies of the original datasets, since images could be converted or resized in order to enable the processing. Please never use the original data and always prepare backups ! 
 
#### Determine Path | Rename samples

Always use a copy of your original data for processing ! Make backups !

With this tab a ClearMap workspace can be initialized. The following steps should be performed:

1. Choose a Workspace by pressing the "Pick Workspace Directory" button. A dialogue window will open where one needs to choose the sample_folder of interest. 
2. The channel of interest (C01,C02) should be selected by choosing from the box beside the "Pick Workspace Directory" button. 
3. One should clarify whether the sample is a single hemisphere or a whole brain. This can also be chosen from the Box beside the channel box.
4. The Workspace can be initialized by clicking the "set workspace" button.
5. The "Rename buttons" will allow the renaming of files in the respective channels. Clicking the button will open a Rename window. The renaming is semi-automatized so that a representative file within the folder is shortened to the pattern ZX[3-4]_C0Y.tif. (The shown filename in the rename window should be between Z000_C0Y.tif-Z9999_C0Y.tif). If the filenames are matching the pattern continue the renaming by clicking the "Accept" button in the renaming window. This will perform a renaming of all the files within Auto, Signal->C01 or Signal->C02 respectively. It is necessary to rename the files in order to automatize the cell detection.  
6. After files are renamed one can continue with the resampling step.

#### Resampling
1. Please insert information about the resolution of signal_channel and atlas images as micrometer per pixel values for the X,Y,Z dimensions at Resample parameters. 
2. Similarly, insert information about the resolution of auto_channel and the reference atlas images for the X,Y,Z dimensions at Resample parameters.  
3. By inserting a filename the inserted resolutions can be saved and loaded for later experiments. (A unique basename has to be used)
4. Add the orientation of the brain. The default settings match the orientation of the side of the right hemisphere facing the camera. For more information about which orientation to choose, visit -> https://christophkirst.github.io/ClearMap2Documentation/html/CellMap.html 
5. Resampling can be started by clicking the "Resample" button.


This process usually takes around 10-20 minutes.

#### Cell-detection and atlas assignment

1. For Cell detection we inserted default values that were tailored to our experiments. For each experiments the optimal values can vary. Please visit https://christophkirst.github.io/ClearMap2Documentation/html/home.html for more information. The possible processing settings are all based on options provided by ClearMap2. 
2. Please be aware that usually only half of the available threads should be used since the usage of working memory is extraordinary high with more threads. We used 10 parallel processes with 128GB RAM. We recommend 5 threads for 64GB RAM machines. 
3. Once the prefered settings are selected, one can start the cell detection by clicking the "Detects cells" button.
4. After cell detection, one has to perform the alignment to the reference atlas by clicking the "Atlas assignment" button. 

These two processes are executed in 2-3 hours, depending on the machine and the amount of detected cells. 
The process has several files as an output. The embedded_ontology.csv files can be used for further quantification analysis. Files that have been produced in the C0YXmlFiles folders can be used together with the Signal tif-files for visualisation in napari to validate the cell detection. Cells that are stored in the universe.xml or no_label.xml files were detected as maximas, but could not be aligned to a reference region. 



#### Grouping and Normalization of data 


In this tab, data of samples form different conditions can be created. The process will create raw count files and counts that summarize the detected cell counts over different hierarchical structures based on the ontology of Allen Brain atlas. Data can be normalized as "median of ratio" or "cellcounts per million" . Additionally, a logarithmic conversion can be performed. A metadata file can be exported for further analytical processing. It is recommended to at least use three samples per condition for further analysis. 

1. Press the "add analysis" button to open a file dialogue and choose an embedded_ontology_C0Y.csv file from the sample_folder of interest. Press "Open" on the dialogue window to confirm your choice. If you made a wrong choice, remove the last selection with "Remove last file"
2. The chosen files should appear in the list below.
3. Once your selection is completed, determine an output path by clicking the "Set output dir" button. This opens a folder dialogue window. Create or select an output folder for your count file and press "Open". If you want to normalize your data please choose a normalization option. If you want raw counts, just use the "None" option. After the selection press "Create analysis data". Two count files with the raw or normalized counts of hierarchically embedded and non-embedded data will be written into your output folder.
4. After the creation of the count files a metadata file is required for condition wise comparison. Please insert the sample names (matching the sample_folder names) and the condition name into the Metadata table on the right side of the tab. Click "Save metadata" to write a metadata.csv  

5. Additionally to the metadata.csv a list_information.csv is exported, which allows the analysis of the dataset over different ontology hierarchies. 

#### Preliminary analysis
All the datsets you need for the following step should be located in the output_folder you defined in the last step

1. Choose an input count file by clicking the "Choose input file button". You can load either hierarchical or non-hierarchical counts. 
2. Similarly to step 1, choose the metadata.csv file.
3. Similarly to step 1, choose the list_information.csv file.
4. After the selection of the 3 files please press "Set input and metadata" to confirm your choice.
5. Press the "PCA" button to perform a principal component analysis.
6. For the cell count heatmap, you can choose one of the brain regions and its hierarchical subregions that you are interested in or filter for a specific hierarchical level. Press the "Heatmap" button.
7. With the boxplot one can have an insight in the counts distribution of a specific region of interest. Please choose a region of interest and press the "Boxplot" button. 

You can search for the existence of regions in the table on the right side of the tab. 

### Cellfinder

#### Data organization for the software:
-> We follow a strict filename structure:

   All files should end with the following pattern -> *ZX[3-4]_C01.tif -> (X is the number of the optical plane, it can be a number between 0-9 and must consist of at least three numbers (000-9999))
    
   Be aware that Cellfinder only works with a single signal channel right now.
   If you want to process 2 signal channels, please split the datasets up in different folders. 

   
 -> Additionally we follow a strict folder structure: \
   Sample_folder\
      |\
      -> Auto -> *ZXXXX_C01.tif\
      |\
      |\
      -> Signal -> *ZXXXX_C01.tif \


   Be aware that also the autofluorescence images need a _C01 signature in the filename.


 -> Always work with copies of the original datasets, since images could be converted or resized in order to enable the processing. Please never use the original data and always prepare backups ! 
 
#### Determine Path and rename samples

Always use a copy of your original data for processing ! Make backups !


With this tab a CellFinder workspace can be initialized. The following steps should be performed:
1. Choose a Workspace by pressing the "Choose sample" button. A dialogue window will open where one needs to choose the sample_folder of interest. 
2. The Workspace can be initialized by clicking the "set workspace" button.
3. The "Rename buttons" will allow the renaming of files in the respective channels. Clicking the button will open a Rename window. The renaming is semi-automatized so that a representative file within the folder is shortened to the pattern ZX[3-4]_C0Y.tif. (The shown filename in the rename window should be between Z000_C0Y.tif-Z9999_C0Y.tif). If the filenames are matching the pattern continue the renaming by clicking the "Accept" button in the renaming window. This will perform a renaming of all the files within Auto or Signal respectively. It is necessary to rename the files in order to automatize the cell detection.  
6. After files are renamed one can continue with the resampling step.

Note that Cellfinder is currently only capable of processing whole brain images. Additionally, only a single signal folder per sample can be processed. If you want to process two channels, please copy the sample folder and create a signal folder with the repective image files for the channel of interest. Additionally, be aware not to use your original data, but a copy of it. Images will be resized in further steps if they do not have the same size. 

#### Resampling

1. For resampling please insert the voxel size in micrometer per pixel X,Y,Z for Signal and Auto to determine the resolution.
2. Press "Start preprocessing"

The resampling will resize your images, if they do not have the same size. We recommend once again to only use copies of your original data. In case the images have to be resized, be aware that also the voxel sizes change respectively and will be stored in a voxel_sizes_file within the sample folder. If you plan to resample the same data more than once please use the new voxel_sizes after the first attempt.   


#### Cell-detection and atlas assignment

1. Insert the number of CPUs that your computer is able to process (We used 8)
2. Insert a threshold, being defined as the minimal amount of standard deviations above mean illumination, in order to consider a spot as maximum (Integer)
3. Insert a mean soma diameter of your cells (Integer)
4. Insert the mean cell size in xy plane (Integer)
5. Insert the gaussian filter variable (Float, 0.2 is default)
6. If you want to use your own trained model please pick a model file in .h5 format, otherwise leave the entry free to use the default model
7. Please insert the orientation of your brain during acquisition. You have to explain which directional part of the brain will occur first when passing through the first image of the stack starting from the upper left corner. Choose one orienation out of anterior/posterior ("a"/"p"), superior/inferior ("s"/"i") and left/right ("l"/"r"). Our default is the anterior ("a"), superior ("s"), left ("l") part of the brain. --> asl
8. Click "Start cell detection"
9. After cell detection, one has to click "Embed ontology" to obtain a count file comparable to ClearMap data.

#### Network training 
Training data can be generated with the Cellfinder plugin of napari. Please check the documentation on https://docs.brainglobe.info/cellfinder-napari/user-guide/training-data-generation. 


1. After generating the training data, click on "Choose Yaml" which opens a dialogue window. Navigate to the yaml file created with the cellfinder-napari plugin.
2. Choose a pretrained model, if you want to continue training a custom model. A dialogue window will open where you have to choose a file that contains a model you want to continue training on. The file is in .h5 format. Click open in the dialogue window to proceed. 
3. Click on "Continue training" to use the custom model as template model for continuation of the training.
4. Choose a test fraction the programm will use as subset for the model training during an epoch.
5. Determine the learning rate used for backpropagation during the weight changes of the neural network.
6. Determine a batch size in which the data will be processed. The bigger the batch size, the more demanding it will be for your GPU computation. (Default: 32, Options: 8,16,32,64). 
7. Determine the number of epochs you want to perform during network training. 
8. Choose a directory or create a new one to store your data. Click on "Choose your base directory" to open a dialogue window. By clicking on the "folder+" icon on the dialogue you can create a new window. Rename the newly created folder and proceed by clicking "Choose".  
9. Start the network training by clicking the "Train network" button.

#### Grouping and Normalization of data 

In this tab data of samples from different conditions can be created. The process will create raw count files and counts that summarize the detected cell counts over different hierarchical structures, based on the ontology of the Allen Brain Atlas. Data can be normalized as "median of ratio" or "cellcounts per million". Additionally, a logarithmic conversion can be performed. A metadata file can be exported for further analytical processing. It is recommended to at least use three samples per condition for further analysis. 

1. Press the "add analysis" button to open a file dialogue and choose an embedded_ontology_C0Y.csv file from the sample_folder of interest. Press "Open" on the dialogue window to confirm you choice. If you made a wrong choice, remove the last selection with "Remove last file"
2. The chosen files should appear in the list below.
3. Once your selection is completed determine an output path by clicking the "Set output dir" button. This opens a folder dialogue window. Create or select an output folder for your count file and press "Open". If you want to normalize your data please chosse a normalization option. If you want raw counts just use the "None" option. After the selection press "Create analysis data". Two count files with the raw or normalized counts of hierarchically embedded and non embedded data will be written into your output folder.
4. After the creation of the count files, a metadata file is required for condition wise comparison. Please insert the sample names (matching the sample_folder names) and the condition name into the Metadata table on the right side of the tab. Click save metadata to write a metadata.csv  
5. Additionally to the metadata.csv a list_information.csv is exported, which allows the analysis of the dataset over different ontology hierarchies. 

#### Preliminary analysis
All the datsets you need for the following step should be located in the output_folder you defined in the last step
1. Choose an input count file by clicking the "Choose input file button". You can load eather hierarchical or non-hierarchical counts. 
2. Similarly to step 1, choose the metadata.csv file.
3. Similarly to step 1, choose the list_information.csv file.
4. After the selection of the 3 files please press "Set input and metadata" to confirm your choice.
5. Press the "PCA" button to perform a principal component analysis.
6. For the cell count heatmap you can choose one of the brain regions and their hierarchical subregions that you are interested in or filter for a specific hierarchical level. Press the "Heatmap" button.
7. With the boxplot one can have an insight in the counts distribution of a specific region of interest. Please choose a region of interest and press the "Boxplot" button. 

You can search for the existence of regions in the table on the right side of the tab. 

#### Processing of ClearMap and Cellfinder after Atlas alignment
The application is designed to produce similar output data from Cellfinder and ClearMap to enable the comparison of both software packages. The grouping and normalization step can therefore be performed together with samples of one or the other processing tool. Be aware that we do not guarantee the scientific relevance of your findings. Be aware the statistical meaningfulness of the experiment still lies on the users responsibility. Be carefull which data you use or combine and how you normalize it.
