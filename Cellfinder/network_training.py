from pathlib import Path
from cellfinder_core.train.train_yml import run as run_training

#list of trainint yml files 
yaml_files = [Path(input("Please insert path: "))]
output_directory = Path(input("Please insert output path:"))
home = Path.home()
install_path = home / ".cellfinder"

run_training(output_directory,yaml_files,install_path=install_path,learning_rate=0.0001,continue_training=input("Please insert trained model:"),test_fraction=0.1,batch_size=32,save_progress=True,epochs=2)
