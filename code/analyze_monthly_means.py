from utils import *
from params import approximate_heights, roughness_dict
import pandas as pd
import seaborn as sns

plt.rc("axes.spines", top=False, right=False)

data_path = "../data/monthly/"
institutions = ["IDL", "ETH", "GERICS", "OUR", "BCCR"]  # JLU not yet preprocessed


def select_lowest_level(ds, institution):
    vertical_name = vertical_dim_dic[institution]
    vertical_levels = ds[vertical_name].values
    min_level = vertical_levels[
        np.argmin([approximate_heights[institution][x] for x in vertical_levels])
    ]
    return ds.sel({vertical_name: min_level})


def calculate_changes(s_dict, relative=False, season=None, onshore=False, monthly=True):
    """
    Calculates changes between GRASS and FOREST and returns as pandas DataFrame for plotting
    with seaborn.

    If relative is set to True, changes are reported relative to the change in the lowermost level.

    relative: True or False
    season: None (i.e., year-round), "DJF", "MAM", "JJA", "SON"
    """
    df_list = []
    tmp_institutions = institutions
    if onshore:
        tmp_institutions = ["IDL", "GERICS"]
    for institution in tmp_institutions:
        ds_tmp = s_dict[institution]
        if onshore:
            ds_tmp = restrict_to_land(ds_tmp, monthly)
        if season:
            ds_tmp = (
                ds_tmp.groupby("time.season").mean().sel(season=season).drop("season")
            )
        else:
            ds_tmp = ds_tmp.mean(dim="time")
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


def load_monthly_data_dictionary():
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
    return s_dict


def compute_mean_onshore_surface_change(s_dict):
    """
    Compute the absolute wind speed change in the lowest model level
    in IDL and GERICS
    """
    mean_land = {}
    for experiment in ["GRASS", "FOREST"]:
        if not experiment in mean_land.keys():
            mean_land[experiment] = {}
        mean_land[experiment]["IDL"] = float(
            restrict_to_land(s_dict["IDL"])
            .mean(dim=["time", "rlat", "rlon"])
            .isel(mlev=0)
            .sel(experiment=experiment)["S"]
        )
        mean_land[experiment]["GERICS"] = float(
            restrict_to_land(s_dict["GERICS"])
            .mean(dim=["time", "rlat", "rlon"])
            .sel(lev=27.0)
            .sel(experiment=experiment)["S"]
        )
    return mean_land


##########################################
# Maps for different heights
##########################################
def plot_maps_per_height(s_dict, season=None):
    for ins in institutions:
        vertical_dim = vertical_dim_dic[ins]
        N_vertical = s_dict[ins][vertical_dim].size
        f, ax = plt.subplots(N_vertical, 3, figsize=(9, N_vertical * 3))
        if season:
            title_name = ins + ": " + season
        else:
            title_name = ins + ": full year"
        plt.suptitle(title_name)
        for N in range(N_vertical):
            s_GRASS = (
                s_dict[ins].isel({vertical_dim: N}).sel({"experiment": "GRASS"})["S"]
            )
            s_FOREST = (
                s_dict[ins].isel({vertical_dim: N}).sel({"experiment": "FOREST"})["S"]
            )
            if season:
                s_GRASS = (
                    s_GRASS.groupby("time.season").mean(dim="time").sel(season=season)
                )
                s_FOREST = (
                    s_FOREST.groupby("time.season").mean(dim="time").sel(season=season)
                )
            else:
                s_GRASS = s_GRASS.mean("time")
                s_FOREST = s_FOREST.mean("time")

            s_GRASS.plot(ax=ax[N, 0], levels=15, vmin=1, vmax=15)
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
        figname = "Diff_maps_" + ins + ".jpeg"
        if season:
            figname = "Diff_maps_" + ins + "_" + season + ".jpeg"
        plt.savefig(
            "../plots/exploration/absolute_differences/" + figname,
            dpi=300,
        )


def plot_maps_per_height_paper(s_dict, season=None):
    for ins in ["IDL", "GERICS"]:
        vertical_dim = vertical_dim_dic[ins]
        if ins == "IDL":
            N_vertical = 4  # number of levels below approx. 300m
        else:
            N_vertical = 3
        f, ax = plt.subplots(
            N_vertical,
            3,
            figsize=(9, N_vertical * 3),
            sharex=True,
            sharey=True,
            **SUBPLOT_KW,
        )
        cbar_ax = f.add_axes([0.08, 0.05, 0.55, 0.03])
        cbar_ax_diff = f.add_axes([0.68, 0.05, 0.25, 0.03])

        for N in range(N_vertical):
            # IDL counts from surface upwards while GERICS counts from top of atmosphere down
            if ins == "IDL":
                lev_index = N
            else:
                lev_index = -(N + 1)
            s_GRASS = (
                s_dict[ins]
                .isel({vertical_dim: lev_index})
                .sel({"experiment": "GRASS"})["S"]
            )
            s_FOREST = (
                s_dict[ins]
                .isel({vertical_dim: lev_index})
                .sel({"experiment": "FOREST"})["S"]
            )
            if season:
                s_GRASS = (
                    s_GRASS.groupby("time.season").mean(dim="time").sel(season=season)
                )
                s_FOREST = (
                    s_FOREST.groupby("time.season").mean(dim="time").sel(season=season)
                )
            else:
                s_GRASS = s_GRASS.mean("time")
                s_FOREST = s_FOREST.mean("time")
            s_diff = s_GRASS - s_FOREST
            # Plot parameters
            cbar_kwargs = {
                "label": "Mean wind speeds [m/s]",
                "orientation": "horizontal",
            }
            params_abs = {"levels": 13, "vmin": 2, "vmax": 14, "extend": "neither"}
            params_diff = {
                "levels": 6,
                "vmin": 0,
                "vmax": 2.5,
                "extend": "max",
                "cmap": "Reds",
            }
            if N == 0:
                # plot with colorbar
                s_GRASS.plot(
                    ax=ax[N, 0],
                    **params_abs,
                    cbar_ax=cbar_ax,
                    cbar_kwargs=cbar_kwargs,
                )
                s_FOREST.plot(
                    ax=ax[N, 1],
                    **params_abs,
                    cbar_ax=cbar_ax,
                    cbar_kwargs=cbar_kwargs,
                )
                s_diff.plot(
                    ax=ax[N, 2],
                    **params_diff,
                    cbar_ax=cbar_ax_diff,
                    cbar_kwargs={
                        "label": "Wind speed difference [m/s]",
                        "orientation": "horizontal",
                    },
                )
            else:
                s_GRASS.plot(ax=ax[N, 0], **params_abs, add_colorbar=False)
                s_FOREST.plot(ax=ax[N, 1], **params_abs, add_colorbar=False)
                s_diff.plot(
                    ax=ax[N, 2],
                    **params_diff,
                    add_colorbar=False,
                )
            if ins != "IDL":
                height = approximate_heights["GERICS"][float(s_GRASS[vertical_dim])]
            else:
                height = approximate_heights["IDL"][
                    N
                ]  # this is IDL which only counts its levels
            ax[N, 0].text(
                -0.06,
                0.5,
                str(height) + " m",
                rotation=90,
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax[N, 0].transAxes,
                fontsize=14,
            )
        for ax_tmp in ax.flatten():
            add_coast_boarders(ax_tmp)
            ax_tmp.set_title("")
        ax[0, 0].set_title("GRASS")
        ax[0, 1].set_title("FOREST")
        ax[0, 2].set_title("GRASS-FOREST")
        figname = "Diff_maps_" + ins
        if season:
            figname += "_" + season

        plt.subplots_adjust(0.05, 0.10, 0.95, 0.97, hspace=0.05, wspace=0.05)
        add_letters(ax, x=0.05, y=0.95, fs=12)
        plt.savefig(
            "../plots/exploration/absolute_differences/" + figname + "_paper.jpeg",
            dpi=300,
        )


##########################################
# Statistics as a table
##########################################
def stats_per_height(s_dict):
    """
    Computes key statistics per height level and outputs as a
    latex table

    Assumes that GERICS and IDL are on the same grid. That is, the additional
    two grid box slices in GERISC have to be already removed.
    """
    for ins in ["GERICS", "IDL"]:
        # Open data
        diff = s_dict[ins].sel(experiment="GRASS") - s_dict[ins].sel(
            experiment="FOREST"
        )
        diff = diff.mean(dim="time")
        diff_land = restrict_to_land(diff, monthly=True)

        # on and offshore means
        mean_onshore_change = diff_land.mean(dim=["rlat", "rlon"])
        mean_offshore_change = diff.where(diff_land.isnull()).mean(dim=["rlat", "rlon"])

        # Fraction of onshore cells exceeding threshold
        vertical_name = vertical_dim_dic[ins]
        number_land_cells = (
            diff_land.where(diff_land.S >= 0)["S"].isel({vertical_name: 0}).count()
        )

        def fraction_greater_threshold(diff_land, number_land_cells, threshold):
            return (
                (diff_land["S"] > threshold).sum(dim=["rlat", "rlon"])
                / number_land_cells
                * 100
            )

        percentage_greater_half = fraction_greater_threshold(
            diff_land, number_land_cells, 0.5
        )
        percentage_greater_one = fraction_greater_threshold(
            diff_land, number_land_cells, 1
        )
        percentage_greater_oneandhalf = fraction_greater_threshold(
            diff_land, number_land_cells, 1.5
        )

        # Combine in dataframe
        def _convert_rename(ds, name):
            return ds.to_dataframe().rename(columns={"S": name})

        mean_onshore_change = _convert_rename(
            mean_onshore_change, "Mean onshore change [m/s]"
        )
        mean_offshore_change = _convert_rename(
            mean_offshore_change, "Mean offshore change [m/s] "
        )
        percentage_greater_half = _convert_rename(
            percentage_greater_half, "Onshore fraction greater 0.5 m/s [%]"
        )
        percentage_greater_one = _convert_rename(
            percentage_greater_one, "Onshore fraction greater 1 m/s [%]"
        )
        percentage_greater_oneandhalf = _convert_rename(
            percentage_greater_oneandhalf, "Onshore fraction greater 1.5 m/s [%]"
        )

        df = pd.concat(
            [
                mean_onshore_change,
                mean_offshore_change,
                percentage_greater_half,
                percentage_greater_one,
                percentage_greater_oneandhalf,
            ],
            axis=1,
        )

        # Add approximate height as index
        df["approximate height [m]"] = [approximate_heights[ins][x] for x in df.index]
        df = df.set_index("approximate height [m]").sort_index().round(2)

        # Save
        df[df.index < 350].style.to_latex(
            "../output/Table_absolute_change_" + ins + ".txt"
        )


##########################################
# Height analysis using relative changes
##########################################
def plot_path(relative):
    if relative:
        return "../plots/exploration/relative_differences/"
    else:
        return "../plots/exploration/absolute_differences/"


def plot_decay_quantiles_all(s_dict):
    """
    Plot signal decay (GRASS-FOREST) at heights below 400m
    seperated by model, season, and quantile
    """
    df_list = []
    for season in ["DJF", "MAM", "JJA", "SON", None]:
        df = calculate_changes(
            s_dict=s_dict,
            relative=False,
            season=season,
            onshore=True,
            monthly=True,
        )
        for quantile in [0.1, 0.5, 0.9]:
            df_tmp = (
                df.groupby(["institution", "height"])
                .quantile(quantile)
                .drop(columns=["rlat", "rlon"])
            )
            if season == None:
                df_tmp["season"] = "full year"
            else:
                df_tmp["season"] = season
            df_tmp["quantile"] = quantile
            df_list.append(df_tmp)
    df_combined = pd.concat(df_list)

    f, axs = plt.subplots(ncols=3, nrows=2, figsize=(9, 6), sharex=True)
    for i, q in enumerate([0.9, 0.5, 0.1]):
        for j, ins in enumerate(["IDL", "GERICS"]):
            ax = axs[j, i]
            ax.set_xscale("log")
            df_plot = df_combined[df_combined["quantile"] == q].reset_index()
            df_plot = df_plot[df_plot["institution"] == ins]
            if (i == 1) & (j == 0):
                legend = "brief"
            else:
                legend = False
            sns.scatterplot(
                ax=ax,
                data=df_plot,
                hue="season",
                hue_order=["full year", "DJF", "MAM", "JJA", "SON"],
                x="height",
                y="S",
                legend=legend,
                palette="tab10",
                s=50,
                alpha=0.8,
            )
            ax.set_ylabel("")
            ax.set_xlim(xmax=700)
            ax.set_xticks([30, 100, 200, 400])
            ax.set_xticklabels([30, 100, 200, 400])
            ax.set_ylim(ymin=-0.02)
            if j == 0:
                ax.set_title(str(int(q * 100)) + "th percentile")
    add_letters(axs, y=1.05, x=-0.15)
    sns.move_legend(axs[0, 1], "center", ncol=5, bbox_to_anchor=(0.5, -0.15))
    for i in range(2):
        axs[i, 0].set_ylabel("Wind speed change [m/s]")
        axs[i, 0].set_xlabel("")
        axs[i, 2].set_xlabel("")
    axs[1, 1].set_xlabel("Approximate height [m]")
    plt.subplots_adjust(left=0.07, right=0.98, top=0.95, bottom=0.08, hspace=0.35)
    plt.savefig(plot_path(relative=False) + "/Signal_decay_quantiles_all.jpeg", dpi=600)


def plot_signal_decay_distributions(s_dict, relative, onshore=False, monthly=True):
    """
    Aggregated  distributions
    """
    df = calculate_changes(
        s_dict=s_dict, relative=relative, onshore=onshore, monthly=monthly
    )
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
    figname = "Signal_decay_distributions"
    if onshore:
        figname += "_onshore"
    plt.savefig(
        plot_path(relative) + figname + ".jpeg",
        dpi=300,
    )


def plot_signal_decay_mean_log(s_dict, relative=False, onshore=False, monthly=True):
    df = calculate_changes(
        s_dict=s_dict, relative=relative, onshore=onshore, monthly=monthly
    )
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
    df_synthetic["institution"] = "Power law (unmodified)"
    df_synthetic["relative_height"] = df_synthetic.index
    df_mean = pd.concat([df_mean, df_synthetic.set_index("institution")])

    # Add synthetic -- log-law
    def log_law(relative_heights, z_zero=0.05, z_low=30, d=3):
        """
        z_zero = 0.05  # roughly the mean accross models over C3 grass
        z_low = 30  # lowest level at 10m
        d = 3  # m guessed discplacement height
        """

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
    df_synthetic["institution"] = "Log law (unmodified)"
    df_synthetic["relative_height"] = df_synthetic.index
    df_mean = pd.concat([df_mean, df_synthetic.set_index("institution")])

    # Add synthetic -- log law -- accounting for change in profile
    for ins in ["GERICS", "IDL"]:
        if ins == "GERICS":
            z_low = 30
        else:
            z_low = 28
        mean_land = compute_mean_onshore_surface_change(s_dict)
        grass_profile = log_law(
            np.arange(1, 30), roughness_dict[ins]["C3"], z_low=z_low, d=0
        )
        forest_profile = log_law(
            np.arange(1, 30),
            0.5 * (roughness_dict[ins]["NET"] + roughness_dict[ins]["BDT"]),
            z_low=z_low,
            d=0,
        )  # Mean of both forest types
        diff_profile = np.multiply(
            mean_land["GRASS"][ins], grass_profile
        ) - np.multiply(mean_land["FOREST"][ins], forest_profile)
        df_synthetic = pd.DataFrame(
            index=pd.Index(name="relative_height", data=np.arange(1, 30)),
            data=diff_profile / diff_profile.max(),
            columns=["S"],
        )
        df_synthetic["institution"] = "Log law " + ins
        df_synthetic["relative_height"] = df_synthetic.index
        df_mean = pd.concat([df_mean, df_synthetic.set_index("institution")])

    # Just looking at the mean
    f, ax = plt.subplots()
    sns.scatterplot(
        data=df_mean, x="relative_height", y="S", hue="institution", alpha=0.7
    )
    ax.set_xscale("log")
    ax.set_ylabel("GRASS - FOREST normalized with mean lowest level")
    ax.set_xlabel("Height / height of lowest model level")
    figname = "Signal_decay_mean_log"
    if onshore:
        figname += "_onshore"
    plt.savefig(
        plot_path(relative) + figname + ".jpeg",
        dpi=300,
    )


def plot_boxplots_per_model(s_dict, relative, season=None, monthly=True, onshore=False):
    df = calculate_changes(
        s_dict=s_dict,
        relative=relative,
        season=season,
        monthly=monthly,
        onshore=onshore,
    )
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
    figname = "Signal_decay_boxplot_per_model"
    if season:
        figname = "Signal_decay_boxplot_per_model_" + season
    if onshore:
        figname += "_onshore"
    plt.savefig(
        plot_path(relative) + figname + ".jpeg",
        dpi=300,
    )


if __name__ == "__main__":
    # Execute a lot of plots
    s_dict = load_monthly_data_dictionary()
    plot_maps_per_height_paper(s_dict)
    for season in ["DJF", "MAM", "JJA", "SON"]:
        plot_maps_per_height_paper(s_dict, season=season)
    # Onshore decay computation needs corrections for GERICS because grid is too large
    s_dict["GERICS"] = s_dict["GERICS"].isel(rlat=slice(0, -1), rlon=slice(0, -1))
    stats_per_height(s_dict)
    plot_decay_quantiles_all(s_dict)
    plot_signal_decay_distributions(s_dict, onshore=True, relative=True)
    plot_signal_decay_mean_log(s_dict, relative=True, onshore=True)
