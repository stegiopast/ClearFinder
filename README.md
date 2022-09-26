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

##Usage

###ClearMap

For the usage of ClearMap a few things have to be considered:

#### Data organization for the software:
-> We follow a strict filename structure:
    All files should end with the following pattern -> *ZX[3-4]_C0Y.tif -> (X can be a number between 0-9 and must consist of at least three numbers (000-9999), Y can be number between 1-2)
    Files hacve to be converted to tif format. 
-> Additionally we follow a strict folder structure: 
   Sample_folder
      \|\
      -> Auto -> *Z(X)XXX_C01.tif
      \|\
      \|\
      -> Signal
            &emsp\|\
            &emsp  -> C01 -> *Z(X)XXX_C01.tif
            &emsp  \|\
            &emsp  -> C02 -> *Z(X)XXX_C02.tif
   Be aware that also the autofluorescent pictures need a _C01 signature in the filename. 
 
  

###Cellfinder


