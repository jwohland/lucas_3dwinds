# 1) Open geopotential height and wind speeds from IDL and GERICS
# 2) Interpolate to hub height using closest 2 model levels and adapted wind profiles (dependent on location and time)
# 3) Apply power curve

import xarray as xr
from utils import *
import numpy as np

data_dir = "../data/"
output_dir = "../output/"


def open_wind_geopotential(ins, year, experiment):
    if ins == "GERICS":
        ds_GERICS_FI = xr.open_dataset(
            "../data/GERICS/" + experiment + "/FI_interpolated/FI_" + year + ".nc"
        ).sel(lev=[26, 27])
        ds_GERICS_FIB = xr.open_dataset(
            "../data/GERICS/" + experiment + "/FIB/FIB_" + year + ".nc"
        )
        ds_GERICS_height = ds_GERICS_FI["FI"] - ds_GERICS_FIB["FIB"]

        ds_wind = (
            xr.open_dataset(data_dir + "GERICS/" + experiment + "/S/S_" + year + ".nc")
            .sel(lev=[26, 27])
            .drop(["rotated_pole", "hyai", "hybi", "hyam", "hybm"])
        )
        ds_wind["height"] = ds_GERICS_height

    return ds_wind


def calculate_hub_height_xr(ds, hub_height=120):
    """
    Calculates wind speeds at hub height using data at evolving heights and
    the power law. Execution is done for one timestep here.

    The power law exponent is fitted per time step and location, thereby accounting
    for the fact that wind profiles do not always look the same

    It is assumed that the Dataset ds only contains two levels that are close to the
    hub height.


    """
    # Identify index of upper and lower level to be used here
    height_max = ds["height"].idxmax(dim="lev")
    height_min = ds["height"].idxmin(dim="lev")
    # Calculate power law exponent alpha
    alpha = np.log(ds["S"].sel(lev=height_max) / ds["S"].sel(lev=height_min)) / np.log(
        ds["height"].sel(lev=height_max) / ds["height"].sel(lev=height_min)
    )
    # Interpolate to hub height
    y_hub = (
        ds["S"].sel(lev=height_min)
        * (hub_height / ds["height"].sel(lev=height_min)) ** alpha
    )
    ds_hub = y_hub.to_dataset(name="S_hub")
    ds_hub["S_hub"].attrs = {"long_name": "Wind speed at hub height [m/s]"}
    ds_hub.drop("lev")
    return ds_hub


def plot_illustration_location(ds=None, ins="GERICS", year="2000", experiment="GRASS"):
    """
    Makes a plot that illustrates the approach, showing
        a) wind speed vs. height scatter plot for 8 locations including the fitting profiles
        b) distribution of power law exponents obtained from the data
    Per default, the plot is made for GERICS in 2000
    """
    if not ds:  # load data if not externally provided
        ds_wind = open_wind_geopotential(ins, year, experiment)
    f, ax = plt.subplots(ncols=2, figsize=(12, 4))
    alphas, y_hub = [], []
    colors = ["b", "g", "r", "c", "m", "y", "k", "w"]
    for i, index in enumerate(range(1, 120)):
        ds_tmp = ds_wind.isel(time=0).isel(rlat=index, rlon=index)
        x = ds_tmp.height.values
        y = ds_tmp.S.values
        alpha = np.log(y[0] / y[1]) / np.log(x[0] / x[1])
        xs = np.arange(5, 200, 1)
        y_hub = y[1] * (120 / x[1]) ** alpha
        if i < 8:
            ax[0].scatter(x, y, color=colors[i])
            ax[0].plot(
                xs,
                [y[1] * (x_value / x[1]) ** alpha for x_value in xs],
                alpha=0.3,
                color=colors[i],
            )
            ax[0].scatter(
                120,
                y_hub,
                label="hub height wind = " + str(np.round(y_hub, 2)),
                marker="*",
                color=colors[i],
            )
        alphas.append(alpha)
    ax[0].set_ylabel("Wind speeds [m/s]")
    ax[0].set_xlabel("Height above ground [m]")
    ax[1].hist(alphas, bins=100)
    ax[1].set_ylabel("Number of occurences")
    ax[1].set_xlabel("Power law exponent")
    plt.tight_layout()
    plt.savefig(
        "../plots/"
        + experiment
        + "_example_wind_interpolation_"
        + ins
        + "_"
        + year
        + ".png",
        dpi=300,
    )


def plot_illustration_map(ds=None, ins="GERICS", year="2000", experiment="GRASS"):
    if not ds:  # load data if not externally provided
        ds = open_wind_geopotential(ins, year, experiment)
    ds_tmp = ds.isel(time=1)
    ds_hub = calculate_hub_height_xr(ds_tmp)
    height_max, height_min = 26, 27  # Correct levels for GERICS

    f, axs = plt.subplots(ncols=3, nrows=2, figsize=(16, 8))
    plt.subplots_adjust(bottom=0.25)
    cbar_ax = f.add_axes([0.15, 0.12, 0.7, 0.03])
    # Distributions
    ds_tmp["S"].sel(lev=height_min).plot.hist(
        ax=axs[0, 0], bins=100, xticks=np.arange(0, 31, 3)
    )
    axs[0, 0].axvline(x=ds_tmp["S"].sel(lev=height_min).mean(), ls="-", color="red")

    ds_hub["S_hub"].plot.hist(ax=axs[0, 1], bins=100, xticks=np.arange(0, 31, 3))
    axs[0, 1].axvline(x=ds_hub["S_hub"].mean(), ls="-", color="red")

    ds_tmp["S"].sel(lev=height_max).plot.hist(
        ax=axs[0, 2], bins=100, xticks=np.arange(0, 31, 3)
    )
    axs[0, 2].axvline(x=ds_tmp["S"].sel(lev=height_max).mean(), ls="-", color="red")
    # Maps
    ds_tmp["S"].sel(lev=height_min).plot(
        ax=axs[1, 0], vmin=0, vmax=35, add_colorbar=False, levels=15
    )
    ds_hub["S_hub"].plot(ax=axs[1, 1], vmin=0, vmax=35, add_colorbar=False, levels=15)
    ds_tmp["S"].sel(lev=height_max).plot(
        ax=axs[1, 2],
        vmin=0,
        vmax=35,
        levels=15,
        cbar_ax=cbar_ax,
        cbar_kwargs={"orientation": "horizontal"},
    )

    for i, title in enumerate(
        ["low level about 30m", "hub height 120m", "upper level about 147m"]
    ):
        axs[0, i].set_title(title)
        axs[1, i].set_title("")
        axs[1, i].set_ylabel("")
        axs[1, i].set_xlabel("")
    plt.tight_layout()
    plt.savefig(
        "../plots/"
        + experiment
        + "_example_wind_interpolation_"
        + ins
        + "_"
        + year
        + "_maps.png",
        dpi=300,
    )


def make_illustration_plots():
    ins = "GERICS"
    year = "2000"
    experiment = "GRASS"
    ds_wind = open_wind_geopotential(ins, year, experiment)
    plot_illustration_location(
        ds_wind
    )  # Create example plot with profiles for a few locations at one timestep
    plot_illustration_map(ds_wind)


if __name__ == "__main__":
    ins = "GERICS"  # todo generalize
    for experiment in ["GRASS", "FOREST"]:
        for year in [str(x) for x in np.arange(1986, 2016)]:
            print(year)
            ds_wind = open_wind_geopotential(ins, year, experiment)
            ds_hub = calculate_hub_height_xr(ds_wind)
            ds_hub.to_netcdf(
                output_dir
                + "/hub_height_wind/S_hub_"
                + ins
                + "_"
                + year
                + "_"
                + experiment
                + ".nc"
            )
