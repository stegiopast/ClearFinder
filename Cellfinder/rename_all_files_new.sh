#remove spaces in the files
rename "s/ //g" *

#Determine cut range for the files

#right_cut=0
#while [ $right_cut==0 ]
#do
#    ls *.tif
    

#cut away the unnecessary microscopy information in the files
#for i in $(ls *.tif); do mv $i ${i:93:150}; done 

for i in $(ls *.tif); do mv $i ${i:93:150}; done 
# Add a 0 to all files which include only 3 digits
# Checkup to select all 999 files
ls *.tif | grep -E '^[0-9]{3}_' | wc -l
for i in $(ls *.tif) | grep -E '^[0-9]{3}_';do mv $i Z0${i};done

#Add a Z to all files above 999 

ls *.tif | grep -E '[0-9]' | wc -l
for i in $(ls *.tif) | grep -E '^[0-9]';do mv $i Z${i};done





