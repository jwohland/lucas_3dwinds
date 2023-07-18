# Functionality copied from CESM2energy project (not open at the time of writing)
# These functions are adapted from https://github.com/jwohland/wind_n_solar

import pandas as pd
import glob
import time
import numpy as np
import xarray as xr

out_path = "../output/generation/"

class Power:
    """
    Wind power  conversion class. Based on pre-computed power curves, this
    class provides functionality to translate hub height wind speeds into
    capacity factors.
    """

    def __init__(self, turbine_index):
        self.power_curve = pd.read_pickle(
            sorted(glob.glob("../output/*.p"))[turbine_index]
        )
        self.turbine_name = self.power_curve.keys()[0].replace(
            "/", "_"
        )  # / leads to issues when saving

    def power_conversion(self, s):
        """
        translate wind speed s into capacity factors via the power curves that
        are provided as a lookup table.
        :param s:
        :return:
        """
        if np.isnan(s):
            return np.nan
        elif s <= self.power_curve.index[0] or s >= self.power_curve.index[-1]:
            # below cut_in or above cut_out
            out = 0.0
        else:
            idx = self.power_curve[self.power_curve.index > s].iloc[0]  # close index, power curve index monotonically increases
            out = idx.values[0]
        return float(out)


def update_attrs(ds, var, unitname, varname, long_varname):
    """
    Updates metadata of an xarray dataset, for example after trend calculation
    :param ds: input dataset
    :param var; variable in ds that is to be updated
    :param unitname: new units
    :param varname: new name of the variable
    :param long_varname: new long name of the variable
    :return:
    """
    ds = ds.rename_vars({var: varname})
    ds[varname].attrs["units"] = unitname
    ds[varname].attrs["long_name"] = long_varname
    return ds


def convert_winds(ds, filename):
    """
    Convert wind speeds to wind capacity factors for the three turbines
    :param ds: xr.dataset with hub height wind speeds available as "s_hub"
    :param filename:
    :return:
    """
    wind_power_list = []
    for turbine_index in range(3):
        # Open power curves if they exists, otherwise compute them
        try:
            P = Power(turbine_index)
        except:
            """ You need to download the power curves and store them in ../output"""
        print(P.turbine_name)

        t_0 = time.time()
        wind_power = xr.apply_ufunc(
            P.power_conversion, ds["s_hub"], vectorize=True, dask="allowed"
        ).to_dataset()
        wind_power = update_attrs(
            wind_power, "s_hub", "", "CF_wind", "normalized_wind_power_generation"
        )
        wind_power["turbine"] = P.turbine_name
        print("wind power conversion took " + str(time.time() - t_0))
        t_0 = time.time()
        wind_power.to_netcdf(out_path + P.turbine_name + "/" + filename)
        print("saving took " + str(int(time.time() - t_0)) + " s")
        wind_power_list.append(wind_power)
    wind_power = xr.concat(
        wind_power_list,
        dim=pd.Index(
            [Power(turbine_index).turbine_name for turbine_index in range(3)],
            name="turbine",
        ),
    )
    return wind_power
