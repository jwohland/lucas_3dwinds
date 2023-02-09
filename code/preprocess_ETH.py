# To be executed after preprocess_ETH.sh
import xarray as xr
from params import *

data_path = "../data/ETH/"

for year in range(1986, 2016):
    print(year)
    for experiment in EXPERIMENTS:
        # Step1: Winds at pressure levels
        # open both wind components in one dataset
        ds_list = []
        for variable in ["U", "V"]:
            filename = (
                data_path
                + experiment
                + "/"
                + variable
                + "/"
                + variable
                + "_"
                + str(year)
                + ".nc"
            )
            ds_list.append(xr.open_dataset(filename))
        ds = xr.merge(ds_list)

        # Compute wind speeds
        ds["S"] = (ds["U"] ** 2 + ds["V"] ** 2) ** (1.0 / 2)

        # Drop non-needed variables and save to file
        ds = ds.drop(["U", "V"])
        ds.to_netcdf(data_path + experiment + "/S/" + str(year) + ".nc")

        # Step2: Surface winds
        ds_list = []
        for variable in ["U_10M", "V_10M"]:
            filename = (
                data_path
                + experiment
                + "/"
                + variable
                + "/"
                + variable
                + "_"
                + str(year)
                + ".nc"
            )
            ds_list.append(xr.open_dataset(filename))
        ds = xr.merge(ds_list)

        # Compute wind speeds
        ds["S_10M"] = (ds["U_10M"] ** 2 + ds["V_10M"] ** 2) ** (1.0 / 2)

        # Drop non-needed variables and save to file
        ds = ds.drop(["U_10M", "V_10M"])
        ds.to_netcdf(data_path + experiment + "/S_10M/" + str(year) + ".nc")
