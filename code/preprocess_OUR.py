import xarray as xr
import glob
from params import *

data_path = "../data/OUR/"

for year in range(1986, 2016):
    print(year)
    for experiment in EXPERIMENTS:
        #open both wind components in one dataset
        ds_list = []
        for variable in ["ua", "va"]:
            filename = glob.glob(
                data_path + experiment + "/" + variable + "/*" + str(year) + "1231.nc"
            )[0]
            ds_list.append(xr.open_dataset(filename))
        ds = xr.merge(ds_list)

        # Compute wind speeds
        ds["S"] = (ds["ua"] ** 2 + ds["va"] ** 2) ** (1.0 / 2)

        # Drop non-needed variables and save to file
        ds = ds.drop(["ua", "va"])
        ds.to_netcdf(data_path + experiment + "/S/" + str(year) + ".nc")
