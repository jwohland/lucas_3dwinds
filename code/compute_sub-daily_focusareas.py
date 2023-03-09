import xarray as xr
from utils import *
import pandas as pd

data_dir = "../data/"
target_dir = "../data/sub-daily/"


def select_common_hours(ds):
    """
    Datasets have different temporal resolution but they all have timesteps at

    0AM, 6AM, 0PM, 6PM
    """
    return ds.sel(
        time=(ds["time.hour"] == 0)
        | (ds["time.hour"] == 6)
        | (ds["time.hour"] == 12)
        | (ds["time.hour"] == 18)
    )


def select_month(ds, month):
    """
    Select specific month and return ds in that month

    month is an integer between 1 and 12
    """
    return ds.sel(time=ds["time.month"] == month)


for experiment in ["FOREST", "GRASS"]:
    for institution in ["BCCR", "GERICS", "ETH", "IDL", "OUR"]:
        print(institution)
        ds = xr.open_mfdataset(data_dir + institution + "/" + experiment + "/S/*.nc")
        if institution == "GERICS":
            # time index needs modification to be understood by xarray
            ds["time"] = pd.date_range(
                start="19860101.", periods=ds.time.size, freq="6h"
            )
        ds = select_common_hours(ds)
        for month in [1, 4, 7, 10]:
            ds_month = select_month(ds, month).load()
            print("monthly data loaded")
            for focus_area in ["Germany", "Sweden", "Spain"]:
                print(focus_area)
                ds_focus = get_focus_area(ds_month, area_name=focus_area)
                ds_focus.to_netcdf(
                    target_dir
                    + experiment
                    + "/S_"
                    + institution
                    + "_subdaily_"
                    + focus_area
                    + "_month_"
                    + str(month)
                    + ".nc"
                )
