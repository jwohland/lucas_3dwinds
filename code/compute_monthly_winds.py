import xarray as xr
import pandas as pd
from params import *

data_dir = "../data/"
target_dir = "../data/monthly/"

for experiment in ["FOREST", "GRASS"]:
    for institution in ["GERICS", "ETH", "IDL", "OUR"]:
        print(institution)
        ds = xr.open_mfdataset(data_dir + institution + "/" + experiment + "/S/*.nc")
        if institution == "GERICS":
            # time index needs modification to be understood by xarray
            ds["time"] = pd.date_range(start="19860101.", periods=ds.time.size, freq="6h")
        # Resample to monthly values
        ds = ds.resample(time="1MS").mean(dim="time").compute()
        # use same lat-lon coordinates
        ds = ds.sel({"rlat": horizontal_ranges["rlats"], "rlon": horizontal_ranges["rlons"]})
        ds.to_netcdf(target_dir + experiment + "/S_" + institution + ".nc")