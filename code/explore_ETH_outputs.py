"""
Explore ETH data and screen for relevant variables
"""
import xarray as xr
from os import listdir

# path to one unzipped year (hoping that output is identical across years and experiments)
path_to_data = "../data/ETH/EVAL/2000/output/"

for folder in ["1hr/", "3hr/", "6hr/", "daily/", "3D/", "h0/", "h1/", "h2/", "h3/"]:
    print(folder)
    f = open(path_to_data + folder[:-1] + "_variablelist.txt", "w")
    # choose first file in folder
    filename = listdir(path_to_data + folder)[0]
    ds = xr.open_dataset(path_to_data + folder + filename)
    for var_name in list(ds.keys()):
        try:
            f.write(var_name + ": " + ds[var_name].long_name + "\n")
        except:
            f.write(var_name + " no long_name" + "\n")
    f.close()