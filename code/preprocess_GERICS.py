# Preprocessing of GERICS data, in particular handling the shifted grids in
# lat, lon, and vertical dimension as discussion in github issue #9 and prototype in
#       notebooks/3_GERICS_grid_offsets.ipynb
# Execution of this script requires prior execution of preprocess_GERICS.sh

import xarray as xr
from params import *

data_path = "../data/GERICS/"

# Variable overview
# 2D
#   Already fine (i.e., rlat, rlon) : PS, FIB
# 3D
#   Already fine (i.e., rlat, rlon, lev): T
#   rlat, rlon, lev_2: FI
#   rlat, rlon_2, lev: U
#   rlat_2, rlon, lev: V


######################
# Interpolate FI to lev
######################
for year in range(1986, 2016):
    for experiment in EXPERIMENTS:
        # Load geopotential and drop non-needed variables
        ds = xr.open_dataset(data_path + experiment + "/FI/FI_" + str(year) + ".nc")
        ds = ds.drop(["hyai", "hybi", "hyam", "hybm"])
        # Load surface geopotential and assign lev_2 coordinate (counted from top of atmoshere down)
        ds_ground = xr.open_dataset(
            data_path + experiment + "/FIB/FIB_" + str(year) + ".nc"
        )  # Geopotential at surface
        ds_ground = ds_ground.assign_coords({"lev_2": 28.0}).rename(
            {"FIB": "FI"}
        )  # ground is lowermost level
        # Combine surface and further up
        ds_combined = xr.concat([ds, ds_ground], dim="lev_2")
        # Perform rolling mean interpolation (lev is defined between lev_2)
        ds_combined = ds_combined.rolling({"lev_2": 2}).mean().dropna("lev_2")
        # Rename variable from lev_2 to lev and align counting with other datasets
        ds_combined = ds_combined.rename({"lev_2": "lev"}).assign_coords(
            {"lev": [float(x) for x in range(1, 28)]}
        )
        # save
        ds_combined.to_netcdf(
            data_path + experiment + "/FI_interpolated/FI_" + str(year) + ".nc"
        )
