import xarray as xr

data_dir = "../data/"
target_dir = "../data/summernights_IDL/"


def select_summer_nights(ds):
    ds = ds.sel(time=(ds["time.hour"] == 0))
    ds = ds.sel(time=ds["time.month"] == 7)
    return ds

# Compute and save July midnight mean wind speeds
for experiment in ["FOREST", "GRASS"]:
    ds = xr.open_mfdataset(
        data_dir + "IDL/" + experiment + "/S/*.nc", preprocess=select_summer_nights
    )
    ds = ds.mean(dim="time")
    ds.load()
    print("loaded")
    ds.to_netcdf(ds.to_netcdf(target_dir + experiment + "/S_IDL_summernights.nc"))

