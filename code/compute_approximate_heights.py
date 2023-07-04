# Compute dictionary of approximate heights per model level
# and add uncertainty estimates
# and visualize distributions

import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

plot_path = "../plots/vertical_coordinate/"


def plot_mean_std_heights(ds_height, zdim_name, zdim_range, ins, nrows=6):
    f, axs = plt.subplots(ncols=3, nrows=nrows, figsize=(12, 16/6*nrows))
    for i, lev_2 in enumerate(zdim_range):
        ds_tmp = ds_height.sel({zdim_name: lev_2})
        ds_tmp.mean(dim="time").plot(ax=axs[i, 0])
        ds_tmp.std(dim="time").plot(ax=axs[i, 1])
        sns.histplot(
            ds_tmp.mean(dim="time")
            .drop(zdim_name, errors="ignore")
            .to_dataframe(name="mean height above ground"),
            stat="density",
            cumulative=True,
            ax=axs[i, 2],
            legend=False,
        )
        for q in [0.15, 0.85]:
            axs[i, 2].axhline(y=q, ls="--", color="teal")
        for j in range(2):
            axs[i, j].set(xlabel="", ylabel="")
        axs[i, 0].set_title(
            "Level "
            + str(lev_2)
            + "; mean "
            + str(np.round(ds_tmp.mean().values, 1))
            + "m"
        )
        axs[i, 1].set_title(
            "Spatial mean of temporal std "
            + str(np.round(ds_tmp.std(dim="time").mean().values, 1))
            + "m"
        )
        axs[i, 2].set_title(
            "Spatial std of temporal means "
            + str(np.round(ds_tmp.mean(dim="time").std().values, 1))
            + "m"
        )

    plt.tight_layout()
    plt.savefig(plot_path + "Approximate_height_map_" + ins + ".jpeg", dpi=300)


# GERICS
ds_GERICS_FI = xr.open_dataset(
    "../data/GERICS/GRASS/FI_interpolated/FI_2000.nc"
)  # todo this is only grass
ds_GERICS_FIB = xr.open_dataset("../data/GERICS/GRASS/FIB/FIB_2000.nc")
ds_GERICS_height = ds_GERICS_FI["FI"] - ds_GERICS_FIB["FIB"]


plot_mean_std_heights(ds_GERICS_height, "lev", range(22, 28), "GERICS")
# todo output mean level and standard deviations to a dictionary or so

# IDL
ds_IDL_zg = xr.open_dataset(
    "../data/IDL/EVAL/zg/zg_EUR-44_ECMWF-ERAINT_LUCAS_EVAL_r1i1p1_IDL_WRFV381D_v1_1hr_2000010100-2000123123.nc"
)  # todo this is only EVAL
ds_IDL_oro = xr.open_dataset(
    "../data/IDL/orog_EUR-44_ECMWF-ERAINT_LUCAS_EVAL_r1i1p1_IDL_WRFV381D_v1_fx.nc"
)
# coordinates are off by a rounding error. Corrected here
for ds_tmp in [ds_IDL_zg, ds_IDL_oro]:
    for rdim in ["rlat", "rlon"]:
        ds_tmp[rdim] = np.round(ds_tmp[rdim], 2)
ds_IDL_height = ds_IDL_zg["zg"] - ds_IDL_oro["orog"].drop(["lon", "lat"])
plot_mean_std_heights(ds_IDL_height, "mlev", range(6), "IDL")

# BCCR
ds_zg = xr.open_dataset("../data/BCCR/GRASS/ZG/ZG_2000.nc").drop("rotated_pole")
ds_oro = xr.open_dataset(
    "../data/IDL/orog_EUR-44_ECMWF-ERAINT_LUCAS_EVAL_r1i1p1_IDL_WRFV381D_v1_fx.nc"
).drop("rotated_pole")
# I.e., assuming all use the same orography
for ds_tmp in [ds_zg, ds_oro]:
    for rdim in ["rlat", "rlon"]:
        ds_tmp[rdim] = np.round(ds_tmp[rdim], 2)
ds_height = ds_zg["zg"] - ds_oro["orog"]
plot_mean_std_heights(
    ds_height.drop(["lat", "lon"]),
    "plev",
    np.array([70000.0, 85000.0, 92500.0, 100000.0]),
    "BCCR",
    nrows=4,
)

# ETH todo this does not work well yet. Oro grid appears different. Only few points overlap!!
ds_zg = xr.open_dataset("../data/ETH/GRASS/FI/FI_2000.nc").drop("rotated_pole")
ds_oro = xr.open_dataset(
    "../data/IDL/orog_EUR-44_ECMWF-ERAINT_LUCAS_EVAL_r1i1p1_IDL_WRFV381D_v1_fx.nc"
).drop("rotated_pole")
# I.e., assuming all use the same orography
for ds_tmp in [ds_zg, ds_oro]:
    for rdim in ["rlat", "rlon"]:
        ds_tmp[rdim] = np.round(ds_tmp[rdim], 1)
ds_height = ds_zg["FI"] - ds_oro["orog"]
plot_mean_std_heights(
    ds_height.drop(["lat", "lon"]),
    "pressure",
    np.array([85000., 92500.]),
    "ETH",
    nrows=2,
)