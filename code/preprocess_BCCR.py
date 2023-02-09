import xarray as xr

# Open wind components at pressure level,
# combine them in one file per year,
# compute wind speeds and
# store everything separately


data_path = "../data/BCCR/"
years = range(1986, 2016)


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
            for var in vars
        ]
        ds_ua = xr.merge(ds_list)
        ds_ua.to_netcdf(data_path_tmp + "U/U_" + str(year) + ".nc")

        # va
        var_names = ["va" + str(plev) for plev in [1000, 925, 850, 700]]
        # open all pressure levels at once and rename variables (e.g., ua925)
        # to ua in all cases (plev is a coordinate, doesn't have to be variable name)
        ds_list = [
            xr.open_mfdataset(
                data_path_tmp + "raw_data/" + var + "_*" + str(year) + "010100-*.nc"
            ).rename({var: "V"})
            for var in vars
        ]
        ds_va = xr.merge(ds_list)
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
            for var in vars
        ]
        ds_zg = xr.merge(ds_list)
        ds_zg.to_netcdf(data_path_tmp + "ZG/ZG_" + str(year) + ".nc")

        #####################
        # at 10M and 100M
        #####################

        folder_dictionary = {"100m": "100", "s": "10"}

        for var_name_ending in ["100m", "s"]:
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
            ds_s = (ds_ua["ua"+var_name_ending] ** 2 + ds_va["va"+var_name_ending] ** 2) ** (1.0 / 2)

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
