# Plotting and analysis functionality for the capacity factor timeseries
# Additional plots are available in Notebook 29

from utils import *
import pandas as pd
import seaborn as sns
import xarray as xr
import matplotlib.pyplot as plt

data_path = "../output/generation/"

##################################
# Computing functions
##################################


def build_CF_dict(downsample=False):
    """
    Build up a big dataset that contains means of wind power generation

    downsample: True or False
    controls whether the hourly IDL data should be downsampled to 6hr (as GERICS)
    before computing the mean
    """
    ds_dict = {}
    for ins in ["GERICS", "IDL"]:
        ds_dict[ins] = {}
        for experiment in ["GRASS", "FOREST"]:
            print(experiment)
            if (downsample) & (ins == "IDL"):
                ds_tmp = downsample_IDL(experiment)
            else:
                ds = xr.open_mfdataset(
                    data_path + ins + "*" + experiment + ".nc"
                ).rename({"S_hub": "CF SWT120-3600"})
                ds_tmp = (
                    ds["CF SWT120-3600"]
                    .mean(dim="time")
                    .compute()
                    .to_dataset(name="mean")
                )
            ds_dict[ins][experiment] = ds_tmp
    return ds_dict


def downsample_IDL(experiment):
    """
    Downsample hourly IDL capacity factors to 6h and then compute means
    """
    assert experiment in ["GRASS", "FOREST"]
    ds = xr.open_mfdataset(data_path + "IDL" + "*" + experiment + ".nc").rename(
        {"S_hub": "CF SWT120-3600"}
    )
    ds = ds.isel(time=np.arange(0, ds.time.size, 6))  # sample every 6th value
    ds = ds["CF SWT120-3600"].mean(dim="time").compute().to_dataset(name="mean")
    return ds


def construct_histogram_data(ins, experiment, bins):
    """
    On a per timestep basis, commpute histogramm data for pre-defined bins.
    For memory reasons, the computation is executed seperately per year and
    counts are summed up.

    ins: name of the institution, either "GERICS" or "IDL"
    experiment: "FOREST" or "GRASS"
    bins: array of bins to be used for the computation of te histograms
    """
    for year in range(1986, 2016):  # all years under consideration
        if year in [1990, 2000, 2010]:  # visualize progress
            print(year)
        ds = xr.open_mfdataset(
            data_path + ins + "*" + str(year) + "*" + experiment + ".nc"
        )
        ds_land = restrict_to_land(ds, monthly=False, variable_name="S_hub")
        da_land = ds_land["S_hub"].values
        n, bins = np.histogram(da_land[np.isfinite(da_land)], bins=bins)
        if year == 1986:
            n_sum = n
        else:
            n_sum += n
    df = pd.DataFrame(
        data=n_sum,
        index=pd.Index(name="CF", data=np.round(bins[1:], 2)),
        columns=["count"],
    )
    df["relative_count"] = df["count"].values / df["count"].values.sum() * 100
    df["experiment"] = experiment
    df["model"] = ins
    df = df.reset_index()
    return df


def compute_concatenated_histograms(save=True):
    """
    Loop over combinations of institutions and experiment to build
    up a dataframe
    """
    bins = np.arange(0, 1.01, 0.05)
    df_1 = construct_histogram_data("GERICS", "FOREST", bins)
    df_2 = construct_histogram_data("GERICS", "GRASS", bins)
    df_3 = construct_histogram_data("IDL", "FOREST", bins)
    df_4 = construct_histogram_data("IDL", "GRASS", bins)
    df = pd.concat([df_1, df_2, df_3, df_4])
    if save:
        df.to_csv("../output/CF_histograms.csv")
    return df


##################################
# Plotting functions
##################################
def plot_mean_maps(ds_dict, filename_extension=""):
    """
    Make a 3x2 plot displaying mean wind power generation
        per model (rows)
        per experiment and as GRASS-FOREST difference (columns)
    """
    plt.close()
    f, axs = plt.subplots(ncols=3, nrows=2, figsize=(10, 7), **SUBPLOT_KW)
    plt.subplots_adjust(0.04, 0.13, 0.97, 0.95, hspace=0.06, wspace=0.06)
    cbar_ax = f.add_axes([0.02, 0.07, 0.63, 0.03])
    cbar_ax_diff = f.add_axes([0.673, 0.07, 0.3, 0.03])
    for i, ins in enumerate(["GERICS", "IDL"]):
        for j, experiment in enumerate(["GRASS", "FOREST"]):
            ds_dict[ins][experiment]["mean"].plot(
                ax=axs[i, j],
                vmin=0.2,
                vmax=0.65,
                levels=10,
                extend="both",
                cbar_ax=cbar_ax,
                cbar_kwargs={
                    "label": "Mean capacity factor",
                    "orientation": "horizontal",
                },
            )

        diff = ds_dict[ins]["GRASS"]["mean"] - ds_dict[ins]["FOREST"]["mean"]
        diff.plot(
            ax=axs[i, 2],
            vmin=-0.11,
            vmax=0.11,
            levels=12,
            extend="both",
            cbar_ax=cbar_ax_diff,
            cmap=plt.get_cmap("RdBu_r"),
            cbar_kwargs={
                "label": "Difference in mean capacity factor",
                "orientation": "horizontal",
            },
        )

        axs[0, 0].set_title("GRASS")
        axs[0, 1].set_title("FOREST")
        axs[0, 2].set_title("GRASS - FOREST")
        axs[i, 0].text(
            -0.1,
            0.5,
            ins,
            verticalalignment="center",
            transform=axs[i, 0].transAxes,
            rotation=90,
            fontsize=12,
        )

    for ax in axs.flatten():
        ax.set_xlabel("")
        add_coast_boarders(ax)
    add_letters(axs, x=-0.03, y=1.02, fs=12)

    plt.savefig(
        "../plots/generation/Mean_CF_change_maps" + filename_extension + ".png", dpi=300
    )


def plot_relative_change(ds_dict):
    """
    Make a 1x2 plot displaying relative change in mean wind power generation
        (GRASS-FOREST)/FOREST
    """
    plt.close()
    f, axs = plt.subplots(
        nrows=3, sharex=True, sharey=True, figsize=(4, 12), **SUBPLOT_KW
    )
    plt.subplots_adjust(0.06, 0.13, 0.95, 0.97, hspace=0.05, wspace=0.05)
    cbar_ax = f.add_axes([0.1, 0.07, 0.8, 0.03])
    for i, ins in enumerate(["GERICS", "IDL", "IDL-6h"]):
        if ins == "IDL-6h":
            print("Downsampling hourly IDL to 6h, this takes a minute or so.")
            ds_grass = downsample_IDL("GRASS")["mean"]
            print("Grass done")
            ds_forest = downsample_IDL("FOREST")["mean"]
            print("Forest done")
        else:
            ds_grass = ds_dict[ins]["GRASS"]["mean"]
            ds_forest = ds_dict[ins]["FOREST"]["mean"]
        diff = (ds_grass - ds_forest) / ds_forest * 100
        diff.plot(
            ax=axs[i],
            vmin=0,
            vmax=50,
            levels=11,
            extend="max",
            cbar_ax=cbar_ax,
            cmap=plt.get_cmap("Reds"),
            cbar_kwargs={
                "label": "Relative difference in mean capacity factor [%]",
                "orientation": "horizontal",
            },
        )
        axs[0].set_title("(GRASS - FOREST) / FOREST")

        axs[i].set_ylabel(ins)

    for ax in axs.flatten():
        ax.set_xlabel("")
        add_coast_boarders(ax)
    add_letters(axs, x=-0.02, y=1.02, fs=12)

    plt.savefig("../plots/generation/Mean_CF_change_relative_diff_maps.png", dpi=300)


def plot_mean_histograms(ds_dict):
    """ """
    f, axs = plt.subplots(nrows=2, sharex=True, sharey=True, figsize=(4, 8))
    for i, ins in enumerate(["GERICS", "IDL"]):
        for experiment in ["GRASS", "FOREST"]:
            ds_tmp = ds_dict[ins][experiment]["mean"]
            ds_tmp = restrict_to_land(ds_tmp.to_dataset(name="S"), monthly=False)
            sns.histplot(
                ds_tmp["S"].values.flatten(),
                hue=None,
                kde=True,
                label=experiment,
                ax=axs[i],
                binwidth=0.01,
                stat="percent",
            )
        axs[i].set_title(ins)
        axs[i].set_ylabel("Percentage of onshore grid cells")
    axs[0].legend()
    axs[1].set_xlabel("Time-mean onshore capacity factor")
    plt.tight_layout()
    plt.savefig("../plots/generation/CF_distribution_time-mean.png", dpi=300)


if __name__ == "__main__":
    ds_dict = build_CF_dict()
    plot_mean_maps(ds_dict)
    plot_relative_change(ds_dict)
    df_histograms = compute_concatenated_histograms(save=True)
    plot_mean_histograms(ds_dict)
    # check that results are robust after downsampling
    ds_dict = build_CF_dict(True)
    plot_mean_maps(ds_dict, filename_extension="_downsampled")
