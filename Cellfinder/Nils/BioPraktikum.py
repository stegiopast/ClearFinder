import rpy2
import rpy2.robjects as robjects
import pandas as pd
import numpy as np
from plotnine import ggplot, aes, geom_bar, theme, element_text, coord_flip

# r = robjects.r
# r['source']("C:\\Users\\nilsm\\Desktop\\Bio_Praktikum\\CreateBarplot.R")

df = pd.read_csv("C:\\Users\\nilsm\\Desktop\\Bio_Praktikum\\summary.csv")
#print(df.describe())      # Mathematical summary of dataframe

#print(df.head())

# for col in df.columns:
#     print(col)

# Striatum_data = df[df['structure_name'].str.contains('triatum')]["total_cells"].sum()
# print(Striatum_data)

resultframe = [["Isocortex", df[df['structure_name'].str.contains('socortex')]["total_cells"].sum()],
               ["Cerebral area", df[df['structure_name'].str.contains('erebral')]["total_cells"].sum()],
               ["Hypothalamus", df[df['structure_name'].str.contains('ypothala')]["total_cells"].sum()],
               ["Striatum", df[df['structure_name'].str.contains('tria')]["total_cells"].sum()],
               ["Olfactory area", df[df['structure_name'].str.contains('factory')]["total_cells"].sum()],
               ["Somatosensory area", df[df['structure_name'].str.contains('omatosen')]["total_cells"].sum()],
               ["Motor area", df[df['structure_name'].str.contains('otor')]["total_cells"].sum()],
               ["Thalamus", df[df['structure_name'].str.contains('halamus')]["total_cells"].sum()],
               ["Piriform", df[df['structure_name'].str.contains('iriform')]["total_cells"].sum()],
               ["Dentate Gyrus", df[df['structure_name'].str.contains('entate')]["total_cells"].sum()],
               ["Hypocampus", df[df['structure_name'].str.contains('ypocampus')]["total_cells"].sum()],
               ["Entorhinal area", df[df['structure_name'].str.contains('ntorhin')]["total_cells"].sum()],
               ["Pallidum", df[df['structure_name'].str.contains('allidum')]["total_cells"].sum()],
               ["Cerebellum", df[df['structure_name'].str.contains('erebell')]["total_cells"].sum()],
               ["Epithalamus", df[df['structure_name'].str.contains('pithalam')]["total_cells"].sum()],
               ["Midbrain", df[df['structure_name'].str.contains('idbrain')]["total_cells"].sum()],
               ["Pons", df[df['structure_name'].str.contains('ons')]["total_cells"].sum()],
               ["Medulla", df[df['structure_name'].str.contains('edulla')]["total_cells"].sum()],
               ["Gustatory area", df[df['structure_name'].str.contains('ustato')]["total_cells"].sum()],
               ["Amygdala", df[df['structure_name'].str.contains('mygda')]["total_cells"].sum()],
               ["Zona incerna", df[df['structure_name'].str.contains('ona in')]["total_cells"].sum()],
               ["Limbic", df[df['structure_name'].str.contains('imbic')]["total_cells"].sum()],
               ["Optic area", df[df['structure_name'].str.contains('ptic')]["total_cells"].sum()]]

#print(resultframe)
print()

count = 0
for i in range(len(resultframe)):
    count += resultframe[i][1]

print(count)

resultframe = pd.DataFrame(resultframe, columns =['Region', 'Cellcount'])
print(resultframe)
#print(df)
#df = df.reset_index()

graph = ggplot(resultframe, aes(x='Region', y="Cellcount")) + geom_bar(stat = "identity") + coord_flip() #+ theme(axis_text_x=element_text(rotation=90))
print(graph)
#graph.save(filename='firsttry.pdf', path="C:\\Users\\nilsm\\Desktop\\Bio_Praktikum")
print("Fertig")

