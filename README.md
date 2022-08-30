# Brainmap_dev
## Installation

Open your terminal (Ctrl + Alt + T) or manually on the desktop.

### 1. Download github repository

```
cd ~
git clone git@github.com:your_username/Brainmap_dev.git
sudo chown your_username ~/Brainmap_dev -R
cd ~/Brainmap_dev/ClearMap
git clone git@github.com:ChristophKirst/ClearMap2.git
mv ClearMap2/ClearMap ~/Brainmap_dev/ClearMap
```

### 2. Download conda if not installed
  -> For linux 64 based distributions use the following code snippet, otherwise visit anaconda.com and follow the installation instructions

```
cd ~
wget https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
bash ~/Anaconda3-2022.05-Linux-x86_64.sh
```
  -> Install mamba for fast environment setup

```
conda install -c conda-forge mamba
```

Please follow the instructions of the conda installation guide

### 3. install nextflow 

```
cd ~
curl -fsSL https://get.nextflow.io | bash
cp nextflow /usr/bin/
sudo chown your_username /usr/bin/nextflow
sudo chown your_username ~/.nextflow -R
```
Please follow the instructions of the nextflow installation guide

### 4. install different environments

Cellfinder_env
```
conda env create --file ~/Brainmap_dev/Cellfinder/requirements.yml
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
conda env create --file ~/Brainmap_dev/Napari/requirements.yml
```
