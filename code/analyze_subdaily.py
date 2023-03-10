import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rc("axes.spines", top=False, right=False)
from utils import *
from params import approximate_heights
import seaborn as sns


def replace_vertical_coordinate(ds, ins):
    initial_name = vertical_dim_dic[ins]
    ds[initial_name] = [approximate_heights[ins][x] for x in ds[initial_name].values]
    ds = ds.rename({initial_name: "approximate height"})
    ds["approximate height"].attrs = {"unit": "m"}
    return ds


data_path = "../data/sub-daily/"
month_dic = {1: "January", 4: "April", 7: "July", 10: "October"}

for ins in [
    "GERICS",
    "IDL",
    "OUR",
]:  # BCCR and ETH excluded because they do not have enough relevant outputs near ground
    for loc in ["Germany", "Sweden", "Spain"]:
        print(ins)
        f, axs = plt.subplots(
            ncols=3, nrows=4, figsize=(14, 16), sharey=True, sharex=True
        )
        for i, month in enumerate([1, 4, 7, 10]):
            ds_forest = replace_vertical_coordinate(
                constrain_vertical_range(
                    xr.open_dataset(
                        data_path
                        + "FOREST/S_"
                        + ins
                        + "_subdaily_"
                        + loc
                        + "_month_"
                        + str(month)
                        + ".nc"
                    ),
                    ins,
                ),
                ins,
            )
            if ins == "ETH":
                # remove known duplicate timestep
                ds_forest = ds_forest.drop_duplicates(dim="time")
            ds_grass = replace_vertical_coordinate(
                constrain_vertical_range(
                    xr.open_dataset(
                        data_path
                        + "GRASS/S_"
                        + ins
                        + "_subdaily_"
                        + loc
                        + "_month_"
                        + str(month)
                        + ".nc"
                    ),
                    ins,
                ),
                ins,
            )
            ds_diff = ds_grass.drop("rotated_pole", errors="ignore") - ds_forest.drop(
                "rotated_pole", errors="ignore"
            )
            ds_forest["S"].groupby("time.hour").mean().plot(
                ax=axs[i, 0], vmin=2, vmax=15, levels=14
            )
            ds_grass["S"].groupby("time.hour").mean().plot(
                ax=axs[i, 1], vmin=2, vmax=15, levels=14
            )
            ds_diff["S"].groupby("time.hour").mean().plot(
                ax=axs[i, 2], cmap="RdBu_r", vmin=-2, vmax=2
            )

            axs[i, 0].text(
                -0.27,
                0.5,
                month_dic[month],
                verticalalignment="center",
                transform=axs[i, 0].transAxes,
                color="darkred",
                fontsize=14,
                rotation=90,
            )

        axs[0, 0].set_title("FOREST")
        axs[0, 1].set_title("GRASS")
        axs[0, 2].set_title("DIFF")
        plt.suptitle(ins + " in " + loc, fontsize=18)
        for ax in axs.flatten():
            ax.set_xticks(ds_forest["approximate height"])
            ax.set_yticks([0, 6, 12, 18])
            ax.set_xlim(xmin=0, xmax=700)

        plt.savefig(
            "../plots/exploration/sub-daily/Profile_" + ins + "_" + loc + ".jpeg"
        )
