import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

plt.rc("axes.spines", top=False, right=False)
from utils import *
from params import approximate_heights
import seaborn as sns

data_path = "../data/monthly/"
institutions = ["IDL", "ETH", "GERICS", "OUR", "BCCR"]  # JLU not yet preprocessed


def select_lowest_level(ds, institution):
    vertical_name = vertical_dim_dic[institution]
    vertical_levels = ds[vertical_name].values
    min_level = vertical_levels[
        np.argmin([approximate_heights[institution][x] for x in vertical_levels])
    ]
    return ds.sel({vertical_name: min_level})


def calculate_changes(relative, season=None):
    """
    Calculates changes between GRASS and FOREST and returns as pandas DataFrame for plotting
    with seaborn.

    If relative is set to True, changes are reported relative to the change in the lowermost level.

    relative: True or False
    season: None (i.e., year-round), "DJF", "MAM", "JJA", "SON"
    """
    df_list = []
    for institution in institutions:
        if season:
            ds_tmp = (
                s_dict[institution]
                .groupby("time.season")
                .mean()
                .sel(season=season)
                .drop("season")
            )
        else:
            ds_tmp = s_dict[institution].mean(dim="time")
        ds_tmp = ds_tmp.drop(["lat", "lon"], errors="ignore")
        diff = ds_tmp.sel({"experiment": "GRASS"}) - ds_tmp.sel(
            {"experiment": "FOREST"}
        )
        if relative:
            diff /= select_lowest_level(diff, institution).mean()
        df = diff["S"].to_dataframe()
        df = df.reset_index(["rlat", "rlon"])  # seperate z, rlat, rlon multiindex
        df.index = pd.Index(
            name="height", data=[approximate_heights[institution][x] for x in df.index]
        )
        df["institution"] = institution
        df_list.append(df)
    df = pd.concat(df_list)
    return df


# Load data into a dictionary
s_dict = {}
for institution in institutions:
    print(institution)
    ds_forest = constrain_vertical_range(
        xr.open_dataset(data_path + "FOREST/S_" + institution + ".nc"), institution
    )
    ds_grass = constrain_vertical_range(
        xr.open_dataset(data_path + "GRASS/S_" + institution + ".nc"), institution
    )
    s_dict[institution] = xr.concat(
        [ds_forest, ds_grass], pd.Index(["FOREST", "GRASS"], name="experiment")
    )


##########################################
# Maps for different heights
##########################################
def plot_maps_per_height():
    for ins in institutions:
        vertical_dim = vertical_dim_dic[ins]
        N_vertical = s_dict[ins][vertical_dim].size
        f, ax = plt.subplots(N_vertical, 3, figsize=(9, N_vertical * 3))
        plt.suptitle(ins + " , vertical dimension: " + vertical_dim)
        for N in range(N_vertical):
            s_GRASS = (
                s_dict[ins]
                .isel({vertical_dim: N})
                .sel({"experiment": "GRASS"})["S"]
                .mean("time")
            )
            s_GRASS.plot(ax=ax[N, 0], levels=15, vmin=1, vmax=15)
            s_FOREST = (
                s_dict[ins]
                .isel({vertical_dim: N})
                .sel({"experiment": "FOREST"})["S"]
                .mean("time")
            )
            s_FOREST.plot(ax=ax[N, 1], levels=15, vmin=1, vmax=15)
            s_diff = s_GRASS - s_FOREST
            s_diff.plot(
                ax=ax[N, 2], levels=7, vmin=0, vmax=3, extend="max", cmap="Blues"
            )
            if ins != "IDL":
                ax[N, 0].set_ylabel(str(s_GRASS[vertical_dim].values))
            else:
                ax[N, 0].set_ylabel(str(N))  # this is IDL which only counts its levels
            ax[N, 1].set_ylabel("")
            ax[N, 2].set_ylabel("")
        for ax_tmp in ax.flatten():
            ax_tmp.set_xlabel("")
            # ax_tmp.set_ylabel("")
            ax_tmp.set_title("")
        ax[0, 0].set_title("GRASS")
        ax[0, 1].set_title("FOREST")
        ax[0, 2].set_title("GRASS-FOREST")
        plt.savefig(
            "../plots/exploration/absolute_differences/Diff_maps_" + ins + ".jpeg",
            dpi=300,
        )


plot_maps_per_height()

##########################################
# Height analysis using relative changes
##########################################


def plot_path(relative):
    if relative:
        return "../plots/exploration/relative_differences/"
    else:
        return "../plots/exploration/absolute_differences/"


def plot_signal_decay_quantiles(relative, season=None):
    """
    # Signal decay with height for 50th, 90th and 95th percentile
    """
    df = calculate_changes(relative=relative, season=season)
    f, ax = plt.subplots(ncols=3, figsize=(15, 5))
    for i, q in enumerate([0.50, 0.90, 0.95]):
        sns.scatterplot(
            ax=ax[i],
            data=df.groupby(["institution", "height"]).quantile(q),
            x="height",
            y="S",
            hue="institution",
            alpha=0.8,
        )
        ax[i].set_title(str(int(q * 100)) + "th Percentile")
        ax[i].set_xlim(xmax=1550, xmin=0)
        ax[i].set_ylabel("")
        ax[i].set_xlabel("Approximate height")
    if relative:
        ax[0].set_ylabel("GRASS - FOREST normalized with mean lowest level")
    else:
        ax[0].set_ylabel("GRASS - FOREST [m/s]")
    if season:
        figname = "Signal_decay_quantiles_" + season + ".jpeg"
    else:
        figname = "Signal_decay_quantiles.jpeg"
    plt.savefig(
        plot_path(relative) + figname,
        dpi=300,
    )


plot_signal_decay_quantiles(relative=True)
plot_signal_decay_quantiles(relative=False)
plot_signal_decay_quantiles(relative=False, season="DJF")


def plot_signal_decay_distributions(relative):
    """
    Aggregated  distributions
    """
    df = calculate_changes(relative=relative)
    f, ax = plt.subplots(figsize=(12, 4))
    sns.violinplot(
        data=df.reset_index(),
        x="height",
        y="S",
        hue="institution",
        alpha=0.8,
        linewidth=0.1,
        width=1.5,
        inner="quartile",
    )
    ax.set_ylim(ymax=5, ymin=-1.0)
    ax.set_xlim(xmax=15.5, xmin=-1.5)
    ax.set_ylabel("GRASS - FOREST normalized with mean lowest level")
    plt.savefig(
        plot_path(relative) + "Signal_decay_distributions.jpeg",
        dpi=300,
    )


plot_signal_decay_distributions(relative=True)


def plot_signal_decay_mean_loglog(relative):
    df = calculate_changes(relative=relative)
    # Looking at the mean in log-log plot using relative height
    df_mean = df.groupby(["institution", "height"]).mean()
    df_mean = df_mean.reset_index(["height"])
    df_min = df_mean.reset_index().groupby("institution")["height"].min()
    df_mean["relative_height"] = df_mean["height"] / df_min

    # Add synthetic
    df_synthetic = pd.DataFrame(
        index=pd.Index(name="relative_height", data=np.arange(1, 30)),
        data=(np.arange(1, 30) ** (1.0 / 7)),
        columns=["S"],
    )
    df_synthetic["institution"] = "Power law"
    df_synthetic["relative_height"] = df_synthetic.index
    df_mean = pd.concat([df_mean, df_synthetic.set_index("institution")])

    # Add synthetic -- log-law
    def log_law(relative_heights):
        d = 3  # m guessed
        z_zero = 0.05  # roughly the mean accross models over C3 grass
        z_low = 30  # lowest level at 10m
        s = [
            np.log((z * z_low - d) / z_zero) / np.log((z_low - d) / z_zero)
            for z in relative_heights
        ]
        return s

    df_synthetic = pd.DataFrame(
        index=pd.Index(name="relative_height", data=np.arange(1, 30)),
        data=log_law(np.arange(1, 30)),
        columns=["S"],
    )
    df_synthetic["institution"] = "Log law (from 10m)"
    df_synthetic["relative_height"] = df_synthetic.index
    df_mean = pd.concat([df_mean, df_synthetic.set_index("institution")])

    # Just looking at the mean
    f, ax = plt.subplots()
    sns.scatterplot(
        data=df_mean, x="relative_height", y="S", hue="institution", alpha=0.7
    )
    ax.set_xscale("log")
    # ax.set_yscale("log")

    ax.set_ylabel("GRASS - FOREST normalized with mean lowest level")
    plt.savefig(
        plot_path(relative) + "Signal_decay_mean_log.jpeg",
        dpi=300,
    )


plot_signal_decay_mean_loglog(relative=True)


def plot_boxplots_per_model(relative):
    df = calculate_changes(relative=relative)
    f, axs = plt.subplots(ncols=len(institutions), sharey=True, figsize=(14, 4))
    for i, institution in enumerate(institutions):
        df_tmp = df[df.institution == institution]
        sns.boxplot(data=df_tmp, x=df_tmp.index, y="S", ax=axs[i], orient="v")
        if relative:
            axs[i].set_ylim(ymax=5, ymin=-2.5)
        else:
            axs[i].set_ylim(ymax=2.5, ymin=-0.5)
        axs[i].set_title(institution)
        axs[i].set_xlabel("Approximate height [m]")
        axs[i].axhline(y=0, ls="--", color="firebrick")
    if relative:
        axs[0].set_ylabel("GRASS - FOREST normalized with mean lowest level")
    else:
        axs[0].set_ylabel("GRASS - FOREST [m/s]")
    plt.savefig(
        plot_path(relative) + "Signal_decay_boxplot_per_model.jpeg",
        dpi=300,
    )


plot_boxplots_per_model(relative=True)
plot_boxplots_per_model(relative=False)
