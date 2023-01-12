# Preprocessing of GERICS data, in particular handling the shifted grids in
# rlat (V uses rlat_2), rlon (U uses rlon_2), and vertical  (FI uses lev_2)
# dimension as discussion in github issue #9 and prototype in
#       notebooks/3_GERICS_grid_offsets.ipynb
# Execution of this script requires prior execution of preprocess_GERICS.sh

import xarray as xr
from params import *

data_path = "../data/GERICS/"

######################
# Combine ground geopotential (FIB) with upper levels (FI) and interpolate from lev_2 to lev
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

######################
# Compute wind speeds from half-shifted wind components
######################
for year in range(1986, 2016):
    for experiment in EXPERIMENTS:
        # Open files
        ds_u = xr.open_dataset(data_path + experiment + "/U/U_" + str(year) + ".nc")
        ds_v = xr.open_dataset(data_path + experiment + "/V/V_" + str(year) + ".nc")

        # u wind component at grid center is mean of u at its western and eastern margin
        ds_u = ds_u.rolling({"rlon_2": 2}).mean()
        ds_u = ds_u.rename({"rlon_2": "rlon"}).assign_coords({"rlon": ds_v.rlon})
        # same for v with northern & southern margin
        ds_v = ds_v.rolling({"rlat_2": 2}).mean()
        ds_v = ds_v.rename({"rlat_2": "rlat"}).assign_coords({"rlat": ds_u.rlat})

        # Compute wind speeds from components
        ds = xr.merge([ds_u, ds_v])
        ds["S"] = (ds.U**2 + ds.V**2)**(1./2)
        ds.S.attrs = {"long_name": "Wind speed", "units": "m/s", "grid_mapping": "rotated_pole"}

        # drop non-needed vars and save
        ds.drop(["U", "V"]).to_netcdf(data_path + experiment + "/S/S_" + str(year) + ".nc")