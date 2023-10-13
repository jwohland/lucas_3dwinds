from utils import *

# Computes effective roughness values for the GERICS simulation
# as time-mean area-mean onshore z0.
# The values are updated manually in params.py.
# This script only documents how the values are derived.

def filename(experiment, resolution="mon"):
    return (
        "z0_EUR-44_ECMWF-ERAINT_LUCAS_"
        + experiment
        + "_GERICS-REMO2009-iMOVE_v2_"
        + resolution
        + "_19860101-20151231.nc"
    )


data_path = "../data/GERICS/roughness/"
for experiment in ["FOREST", "GRASS"]:
    ds = xr.open_dataset(data_path + filename(experiment))
    ds = ds.isel(
        rlat=slice(0, -1), rlon=slice(0, -1)
    )  # correct area that is slightly too large
    ds = ds.mean(dim="time")
    ds = restrict_to_land(ds, monthly=True, variable_name="z0")  # consider land only
    print(
        experiment + ": " + str(ds["z0"].mean().round(3).values)
    )  # print land-mean roughness

# Output (run 13/10/23):
# FOREST: 1.686
# GRASS: 0.693
