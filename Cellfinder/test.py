import os
if os.path.exists("/home/cellfinder_data/KF03/voxel_size_signal"):
   with open("/home/cellfinder_data/KF03/voxel_size_signal/voxel_sizes.txt", "r") as file:
       x = file.read().split(sep=",")
       voxel_x = x[0]
       voxel_y = x[1]
       voxel_z = x[2]
print(voxel_x,voxel_y,voxel_z)
