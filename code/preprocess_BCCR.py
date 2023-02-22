import xarray as xr

# Open wind components at pressure level,
# combine them in one file per year,
# compute wind speeds and
# store everything separately

data_path = "../data/BCCR/"
years = range(1986, 2016)


def replace_pole(ds_list):
    """
    replace  faulty rotated  pole information (integer instead of string)
    """
    ds_correct_rotpole = xr.open_dataset("../data/BCCR/EVAL/U/U_1986.nc")
    for ds_tmp in ds_list:
        ds_tmp["rotated_pole"] = ds_correct_rotpole.rotated_pole
    return ds_list


for experiment in ["EVAL", "FOREST", "GRASS"]:
    data_path_tmp = data_path + experiment + "/"

    for year in years:
        #####################
        # at pressure levels
        #####################
        print(year)
        # ua
        var_names = ["ua" + str(plev) for plev in [1000, 925, 850, 700]]
        # open all pressure levels at once and rename variables (e.g., ua925)
        # to ua in all cases (plev is a coordinate, doesn't have to be variable name)
        ds_list = [
            xr.open_mfdataset(
                data_path_tmp + "raw_data/" + var + "_*" + str(year) + "010100-*.nc"
            ).rename({var: "U"})
            for var in var_names
        ]
        if experiment == "GRASS":
            ds_list = replace_pole(ds_list)
        ds_ua = xr.merge(ds_list).where(ds_ua["U"] < 1e+10)  # merge and mask really high values signifying nans as nans
        ds_ua.to_netcdf(data_path_tmp + "U/U_" + str(year) + ".nc")

        # va
        var_names = ["va" + str(plev) for plev in [1000, 925, 850, 700]]
        # open all pressure levels at once and rename variables (e.g., ua925)
        # to ua in all cases (plev is a coordinate, doesn't have to be variable name)
        ds_list = [
            xr.open_mfdataset(
                data_path_tmp + "raw_data/" + var + "_*" + str(year) + "010100-*.nc"
            ).rename({var: "V"})
            for var in var_names
        ]
        # Fix bug in 1986 EVAL meta data. See issue #27 for explanation
        if ((experiment == "EVAL") & (year == 1986)):
            ds_problem = ds_list[0]
            ds_problem = ds_problem.rename({"x": "rlon", "y": "rlat"})
            ds_correct = xr.open_dataset(
                data_path
                + "/EVAL/raw_data/va1000_EUR44_ECMWF-ERAINT_EVAL_r1i1p1_BCCR-WRF381_1hr_1987010100-1987123123.nc"
            )  # file with correct meta data
            for coordinate in ["rlat", "rlon", "plev"]:
                ds_problem[coordinate] = ds_correct.coords[coordinate].values
            for variable in ["rotated_pole", "lat", "lon"]:
                ds_problem[variable] = ds_correct[variable]
            ds_list[0] = ds_problem

        if experiment == "GRASS":
            ds_list = replace_pole(ds_list)

        ds_va = xr.merge(ds_list).where(ds_va["V"] < 1e+10)  # merge and mask really high values signifying nans as nans
        ds_va.to_netcdf(data_path_tmp + "V/V_" + str(year) + ".nc")

        # s
        ds_s = (ds_ua["U"] ** 2 + ds_va["V"] ** 2) ** (1.0 / 2)
        ds_s = ds_s.to_dataset(name="S")
        ds_s["S"].attrs = {
            "standard_name": "wind_speed",
            "long_name": "Wind speed",
            "units": "m s-1",
            "grid_mapping": "rotated_pole",
            "cell_methods": "time: point",
        }
        ds_s.to_netcdf(data_path_tmp + "S/S_" + str(year) + ".nc")

        # zg
        var_names = ["zg" + str(plev) for plev in [1000, 925, 850, 700]]
        # open all pressure levels at once and rename variables (e.g., ua925)
        # to ua in all cases (plev is a coordinate, doesn't have to be variable name)
        ds_list = [
            xr.open_mfdataset(
                data_path_tmp + "raw_data/" + var + "_*" + str(year) + "010100-*.nc"
            ).rename({var: "zg"})
            for var in var_names
        ]

        if experiment == "GRASS":
            ds_list = replace_pole(ds_list)
        ds_zg = xr.merge(ds_list)
        ds_zg.to_netcdf(data_path_tmp + "ZG/ZG_" + str(year) + ".nc")

        #####################
        # at 10M and 100M
        #####################

        folder_dictionary = {"100m": "100", "s": "10"}
        var_name_endings = [
            "s"
        ]  # ["100m", "s"]  # 100m winds essentially not usable because FOREST 100m v component does not exist. See issue #25

        for var_name_ending in var_name_endings:
            ds_ua = xr.open_mfdataset(
                data_path_tmp
                + "raw_data/ua"
                + var_name_ending
                + "_*"
                + str(year)
                + "010100-*.nc"
            )
            ds_ua.to_netcdf(
                data_path_tmp
                + "U_"
                + folder_dictionary[var_name_ending]
                + "/U_"
                + folder_dictionary[var_name_ending]
                + "_"
                + str(year)
                + ".nc"
            )
            ds_va = xr.open_mfdataset(
                data_path_tmp
                + "raw_data/va"
                + var_name_ending
                + "_*"
                + str(year)
                + "010100-*.nc"
            )
            ds_va.to_netcdf(
                data_path_tmp
                + "V_"
                + folder_dictionary[var_name_ending]
                + "/V_"
                + folder_dictionary[var_name_ending]
                + "_"
                + str(year)
                + ".nc"
            )

            # s
            ds_s = (
                ds_ua["ua" + var_name_ending] ** 2 + ds_va["va" + var_name_ending] ** 2
            ) ** (1.0 / 2)

            ds_s = ds_s.to_dataset(name="S_" + folder_dictionary[var_name_ending])
            ds_s["S_" + folder_dictionary[var_name_ending]].attrs = {
                "standard_name": folder_dictionary[var_name_ending] + "m wind_speed",
                "long_name": "Wind speed at "
                + folder_dictionary[var_name_ending]
                + "m",
                "units": "m s-1",
                "grid_mapping": "rotated_pole",
                "cell_methods": "time: point",
            }
            ds_s.to_netcdf(
                data_path_tmp
                + "S_"
                + folder_dictionary[var_name_ending]
                + "/S_"
                + folder_dictionary[var_name_ending]
                + "_"
                + str(year)
                + ".nc"
            )
