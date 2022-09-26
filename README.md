# Brainmap_dev
## Installation

Open your terminal (Ctrl + Alt + T) or manually on the desktop.

### 1. Download github repository

```
cd ~
git clone git@github.com:stegiopast/Brainmap_dev.git
sudo chown your_local_username ~/Brainmap_dev -R
cd ~/Brainmap_dev/ClearMap
git clone git@github.com:ChristophKirst/ClearMap2.git
mv ClearMap2/ClearMap ~/Brainmap_dev/ClearMap
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

### 5.Start application
```
cd ~/Brainmap_dev
nextflow run start_guis.nf
```
Once you start napari be aware to download the napari-cellfinder plugin in the tab menu under Plugin -> Install/ Uninstall plugins.
Type napari-cellfinder in the search bar and install the plugin. Restart napari for the plugin to be integrated. 


### 6.Alternative start
Note that with it's first start ClearMap needs to be compiled, which takes around half an hour. Until then the gui window will not appear. If you want to circumvent this problem and see how the compilation performs, run:
```
conda activate Clearmap_env
python3 ~/Brainmap_dev/ClearMap/gui.py
conda deactivate
```

Similarly the other guis can be started sperately in a similar way
For Cellfinder type:
```
conda activate Cellfinder_env
python3 ~/Brainmap_dev/Cellfinder/gui.py
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

Insert the following line in the ~/.bashrc file that should open in the texteditor:

```
alias Brainmap="cd path/to/Brainmap_dev && nextflow run start_guis.nf"
```

Safe the file with Ctrl+S or with the save button of the editor. Then close the editor and get back to the terminal. Type:

```
source ~/.bashrc
```

You can from now and forever start the applications with the following command:

```
Brainmap
```

## Usage

### ClearMap

For the usage of ClearMap a few things have to be considered:

#### Data organization for the software:
-> We follow a strict filename structure:
    All files should end with the following pattern -> *ZX[3-4]_C0Y.tif -> (X can be a number between 0-9 and must consist of at least three numbers (000-9999), Y can be number between 1-2)
    Files hacve to be converted to tif format.\
-> Additionally we follow a strict folder structure: 
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
   Be aware that also the autofluorescent pictures need a _C01 signature in the filename.
 
 -> Always work with copies of the original datasets, since images could be converted or resized in order to enable the processing. Please never use the original data and always prepare backups ! 
 
#### Determine Path | Rename samples
With this tab a ClearMap workspace can be initialized. The following steps should be performed:
1. Choose a Workspace by pressing the "Pick Workspace Directory" button. A dialogue window will open wheren one needs to choose the sample_folder of insterest. 
2. The channel of interest (C01,C02) should be selected by choosing from the Box beside the "Pick Workspace Directory" button. 
3. One should clarify whether the sample is hemispheric or whole brain tissue. This can also be chosen from the Box beside the channel box.
4. The Workspace can be initialized by clicking the "set workspace" button.
5. The "Rename buttons" will allow the renaming of files in the respective channels. Clicking the button will open a Rename window. The renaming is semi-automatized so that a representative file within the folder is shortened to the pattern ZX[3-4]_C0Y.tif. (The shown filename in the rename window should be between Z000_C0Y.tif-Z9999_C0Y.tif). If the filenames are matching the pattern continue the renaming by clicking the "Accept" button in the renaming window . This will perform a renaming of all the files within Auto, Signal->C01 or Signal->C02 respectively. It is necessary to rename the files in order to automatize the cell detection.  
6. After files are renamed one can continue with the resampling step.

#### Resampling
1. Please insert information about the resolution of signal_channel and atlas images for the X,Y,Z dimensions at Resample parameters. 
2. Similarly, insert information about the resolution of auto_channel and atlas images for the X,Y,Z dimensions at Resample parameters.  
3. By inserting a filename the inserted resolutions can be saved and loaded for later experiments. (A unique basename has to be used)
4. Resampling can be started by clicking the "Resample" button

This process usually takes around 10-20 minutes.

#### Cell-detection and atlas assignment
1. For Cell detection we inserted default values,that were tailored to our experiments. For each experiments the optimal values can vary. Please visit https://christophkirst.github.io/ClearMap2Documentation/html/home.html for more information. The possible processing settings are all based on options provided by ClearMap2. 
2. Please be aware that usually only half of the available threads should be used since the usage of working memory is extraordinary high with more threads. We used 10 parallel processes with 128GB RAM. We recommend 5 threads for 64GB RAM machines. 
3. Once the prefered settings are selected, one can start cell detection by clicking the "Detects cells" button.
4. After cell detection one has to perform Atlass assignment by clicking the "Atlas assignment" button. 

These two processes are executed in 2-3 hours, depending on the machine and the amount of detected cells. 
The process has several files as an output. The embedded_ontology.csv files can be used for further quantification analysis. Fles that have been produced in the C0YXmlFiles folders can be used together with the Signal tif-files for visualisation in napari to validate the cell detection. Cells that are stored in the universe.xml or no_label.xml files were detected as maximas, but could not be aligned to a reference region. 


#### Grouping and Normalization of data 

In this tab data of samples form different conditions can be created. The process will create raw count files and counts that summarize the detected cell counts over different hierarchical structures based on the ontology of Allen Brain atlas. Data can be "median of ratio" or "cellcounts per million" normalized. Additionally, a logarithmic conversion can be performed. A metadata file can be exported for further analytical processing. I is recommended to at least use three samples per condition for further analysis. 

1. Press the "add analysis" button to open a file dialogue and choose an embedded_ontology_C0Y.csv file from the sample_folder of interest. Press "Open" on the dialogue window to confirm you choice. If you made a wrong choice, remove the last selection with "Remove last file"
2. The chosen files should appear in the list below.
3. Once your selection is completed determine an output path by clicking the "Set output dir" button. This opens a folder dialogue window. Create or select an output folder for your count file and press "Open". If you want to normalize your data please chosse a normalization option. If you want raw counts just use the None option. After the selection press "Create analysis data". Twi count files with the raw or normalized counts of hierarchically embedded and non embedded data will be written into your output folder.
4. After the creation of the count file a metadata file is required for condition wise comparison. Please insert the sample names (matching the sample_folder names) and the condition name into the Metadata table on the right side of the tab. Click save metadata to write a metadata.csv  
5. Additionally to the metadata.csv a list_information.csv is exported, which allows the analysis of the dataset over different ontology hierarchies. 

#### Preliminary analysis
All the datsets you need for the following step should be located in the output_folder you defined in the last step
1. Choose an input count file by clicking the "Choose input file button". You can load eather hierarchical or non-hierarchical counts. 
2. Similarly as in step 1 chosse the metadata.csv file.
3. Similarly as in step 1 choose the list_information.csv file.
4. After the selection of the three files please press "Set input and metadata" to confirm your choice.
5. Press the "PCA" button to perform a principal component analysis.
6. For the cell count heatmap you can choose one of Brain regions and its hierarchical subregions that you are interested in or filter for a specific hierarchical level. Press the "Heatmap" button.
7. With the boxplot one can have an insight in the count distribution of a specific region of interest. Please choose a Region of interest and press the "Boxplot" button. 

You can search for the existence of regions in the table on the right side of the tab. 

### Cellfinder

#### Data organization for the software:
-> We follow a strict filename structure:
    All files should end with the following pattern -> *ZX[3-4]_C01.tif -> (X can be a number between 0-9 and must consist of at least three numbers (000-9999))
    
   Be aware, that Cellfinder is only working for a single channel right now.
   If you want to process to channels, please split the datasets up in different folders. 
   
 -> Additionally we follow a strict folder structure: 
   Sample_folder\
      |\
      -> Auto -> *ZXXXX_C01.tif\
      |\
      |\
      -> Signal -> *ZXXXX_C01.tif \

   Be aware that also the autofluorescent pictures need a _C01 signature in the filename.

 -> Always work with copies of the original datasets, since images could be converted or resized in order to enable the processing. Please never use the original data and always prepare backups ! 
 
#### Initialize and choose workspace

#### Resampling

#### Cell-detection and atlas assignment

#### Network training 

#### Preparation of analysis files

#### Preliminary analysis

