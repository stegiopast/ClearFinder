from PIL import Image
from pathlib import Path
from natsort import natsorted
import os
from tifffile import imread,imwrite
from skimage.transform import rescale,resize, downscale_local_mean
from skimage.util import img_as_uint
import numpy as np
import shutil

filepath = str(Path(input('Please insert path to sample folder: e.g. /home/cellfinder_data/KF03\n')));
print(filepath)
print(os.path.exists(filepath))
filepath_auto = str(filepath + '/Auto/') 
print(filepath_auto)
filepath_signal = str(filepath + '/Signal/')
print(filepath_signal)

filenames_auto = []
filenames_signal = []
for base,dirs,files in os.walk(filepath_auto):
    filenames_auto = files

for base,dirs,files in os.walk(filepath_signal):
    filenames_signal = files

print(len(filenames_auto),len(filenames_signal))
#print(filenames_auto,filenames_signal)

filenames_auto = natsorted(filenames_auto, reverse = False)
filenames_signal = natsorted(filenames_signal, reverse = False)



#print("Filenames Auto ",filenames_auto,"\nFilenames Signal:",filenames_signal)

if len(filenames_auto) != len(filenames_signal):
    difference = abs(len(filenames_auto) - len(filenames_signal))
    if len(filenames_auto) > len(filenames_signal):
        longer_array = filenames_auto
        shorter_array = filenames_signal
        longer_str = "/Auto"
    else:
        longer_array = filenames_signal
        shorter_array = filenames_auto
        longer_str = "/Signal"
    
    print(longer_array)

    if (difference % 2) == 0:
        front = difference // 2
        back = difference // 2
    else:
        front = difference // 2 + 1
        back = difference // 2
    
    if not os.path.exists(filepath + longer_str +"_moved"):
        os.mkdir(filepath +  longer_str + "_moved")
    else:
        print("File existed")


    for i in range(front):
        print(longer_array[0])
        #os.rename(filepath + longer_str + "/" + longer_array[0], filepath + longer_str + "_moved/" + longer_array[0])
        os.remove(filepath + longer_str + "/" + longer_array[0])
        longer_array.pop(0)
    for j in range(0,back):
        print(longer_array[-1])
        #os.rename(filepath + longer_str + "/" + longer_array[-1], filepath + longer_str + "_moved/" + longer_array[-1])
        os.remove(filepath + longer_str + "/" + longer_array[-1])
        longer_array.pop()

    print("Same lenght now ?:", len(filenames_auto) == len(filenames_signal))

    
else:
    print("Lengths are equal\n")




counter = 0
for i,j in zip(filenames_auto,filenames_signal):
    
    #im1 = img_as_uint(filepath_auto + i)
    #im2 = img_as_uint(filepath_auto + j)


    
    im1 = Image.open(filepath_auto + i)
    im2 = Image.open(filepath_signal + j)


    
    pixel_growth_x_signal = im2.size[0] / 2050#im1.size[0]
    pixel_growth_y_signal = im2.size[1] / 3500#im1.size[1]
    
    pixel_growth_x_auto = im1.size[0] / 2050
    pixel_growth_y_auto = im1.size[1] / 3500

    print("Image 1 size",im1.size)
    print("Image2 size",im2.size)
    #new_signal_size_x =  (im1.size[0] / im2.size[0]) * im2.size[0]
    #new_signal_size_y = (im1.size[1] / im2.size[1]) * im2.size[1]
    
    new_size = (3500,2050)
    
    
    im1 = np.asarray(im1)
    im2 = np.asarray(im2)
     
    
    print("Image1 old shape: ", im1.shape)
    print("Image2 old shape: ", im2.shape)
    
    im1 = resize(im1,new_size)
    im2 = resize(im2,new_size)
   
    
    print("Image 1 new shape: ", im1.shape)
    print("Image 2 new shape: ", im2.shape)



    im1 = img_as_uint(im1)
    im2 = img_as_uint(im2)
    
    
    im1 = Image.fromarray(im1)
    im2 = Image.fromarray(im2)
    
    print("Image 1 new size",im1.size)
    print("Image 2 new size",im2.size)
    
    im1.save(filepath_auto + i)
    im2.save(filepath_signal + j)
    
    
    
    if counter < 1:
        if not os.path.exists(filepath+"/voxel_size_signal"):
            os.mkdir(filepath + "/voxel_size_signal")
    
        voxel_filepath = filepath+"/voxel_size_signal";
        new_voxel_size_x = float(input("Insert old signal pixel size x:")) * pixel_growth_x_signal
        new_voxel_size_y = float(input("Insert old signal pixel size y:")) * pixel_growth_y_signal
        new_voxel_size_z = float(input("Insert old signal pixel size z:"))        
        with open(voxel_filepath+"/voxel_sizes.txt", "w") as file:
            file.write(str(new_voxel_size_x))
            file.write(",")
            file.write(str(new_voxel_size_y))
            file.write(",")
            file.write(str(new_voxel_size_z))


        
        if not os.path.exists(filepath+"/voxel_size_auto"):
            os.mkdir(filepath + "/voxel_size_auto")
    
        voxel_filepath = filepath+"/voxel_size_auto";
        new_voxel_size_x = float(input("Insert old auto pixel size x:")) * pixel_growth_x_auto
        new_voxel_size_y = float(input("Insert old auto pixel size y:")) * pixel_growth_y_auto
        new_voxel_size_z = float(input("Insert old auto pixel size z:"))
        with open(voxel_filepath+"/voxel_sizes.txt", "w") as file:
            file.write(str(new_voxel_size_x))
            file.write(",")
            file.write(str(new_voxel_size_y))
            file.write(",")
            file.write(str(new_voxel_size_z))


            
            

    counter += 1

print("Finished work!")
    
