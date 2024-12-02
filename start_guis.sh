#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate base
# Start Cellfinder in environment 1
conda activate Cellfinder_env
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
echo $LD_LIBRARY_PATH
cd Cellfinder
python gui.py &
PID1=$!  # Save process ID
cd ..
conda deactivate

# Start ClearMap in environment 2
conda activate Clearmap_env
cd ClearMap
python gui.py &
PID2=$!
cd ..
conda deactivate

# Start Napari in environment 3
conda activate Napari_env
napari &
PID3=$!
conda deactivate

echo "All GUIs started. PIDs: $PID1, $PID2, $PID3"

# Wait for all processes to finish (optional)
wait $PID1 $PID2 $PID3

echo "All GUIs closed."
