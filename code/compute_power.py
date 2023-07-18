# Translate hub height wind speeds to capacity factor timeseries

from utils_from_CESM2energy import *


if __name__ == "__main__":
    out_path = "../output/generation/"
    # Instantiate turbine SWT120-3600 (i.e., the median turbine at 7m/s)
    P = Power(1)
    ins = "GERICS"  # todo generalize
    for experiment in ["GRASS", "FOREST"]:
        for year in [str(x) for x in np.arange(1986, 2016)]:
            # Open hub height wind
            ds_wind = xr.open_dataset(
                (
                    "../output/hub_height_wind/S_hub_"
                    + ins
                    + "_"
                    + year
                    + "_"
                    + experiment
                    + ".nc"
                )
            )
            # Convert to capacity factor
            wind_power = xr.apply_ufunc(
                P.power_conversion,
                ds_wind["S_hub"],
                vectorize=True,
                dask="allowed",
            ).to_dataset()
            # Save
            wind_power.to_netcdf(
                "../output/generation/"
                + ins
                + "_"
                + P.turbine_name
                + "_"
                + year
                + "_"
                + experiment
                + ".nc"
            )
