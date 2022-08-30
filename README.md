# Brainmap_dev
## Installation

Open your terminal (Ctrl + Alt + T) or manually on the desktop.

### 1. Download github repository

```
cd ~
git clone git@github.com:your_username/Brainmap_dev.git
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
curl -fsSL https://get.nextflow.io | bash
```
Please follow the instructions of the nextflow installation guide

### 4. install different environments

It is mandatory to call the environments with the following names

Cellfinder_env
```
mamba create -n Cellfinder_env --file ./Brainmap_dev/Cellfinder/requirements.txt
```

Clearmap_env
```
mamba create -n Clearmap_env --file ./Brainmap_dev/ClearMap/requirements.txt
```

Napari_env
```
mamba create -n Napari_env --file ./Brainmap_dev/Napari/requirements.txt
```
