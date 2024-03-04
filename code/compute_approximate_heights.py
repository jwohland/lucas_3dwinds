# Compute dictionary of approximate heights per model level
# and add uncertainty estimates
# and visualize distributions

import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

plot_path = "../plots/vertical_coordinate/"


def plot_mean_std_heights(ds_height, zdim_name, zdim_range, ins, nrows=6):
    f, axs = plt.subplots(ncols=3, nrows=nrows, figsize=(12, 16 / 6 * nrows))
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
ds_GERICS_FI = xr.open_dataset("../data/GERICS/GRASS/FI_interpolated/FI_2000.nc")
ds_GERICS_FIB = xr.open_dataset("../data/GERICS/GRASS/FIB/FIB_2000.nc")
ds_GERICS_height = ds_GERICS_FI["FI"] - ds_GERICS_FIB["FIB"]


plot_mean_std_heights(ds_GERICS_height, "lev", range(22, 28), "GERICS")

# IDL
ds_IDL_zg = xr.open_dataset(
    "../data/IDL/EVAL/zg/zg_EUR-44_ECMWF-ERAINT_LUCAS_EVAL_r1i1p1_IDL_WRFV381D_v1_1hr_2000010100-2000123123.nc"
)
ds_IDL_oro = xr.open_dataset(
    "../data/IDL/orog_EUR-44_ECMWF-ERAINT_LUCAS_EVAL_r1i1p1_IDL_WRFV381D_v1_fx.nc"
)
# coordinates are off by a rounding error. Corrected here
for ds_tmp in [ds_IDL_zg, ds_IDL_oro]:
    for rdim in ["rlat", "rlon"]:
        ds_tmp[rdim] = np.round(ds_tmp[rdim], 2)
ds_IDL_height = ds_IDL_zg["zg"] - ds_IDL_oro["orog"].drop(["lon", "lat"])
plot_mean_std_heights(ds_IDL_height, "mlev", range(6), "IDL")
