from utils import *

plt.rc("axes.spines", top=False, right=False)

data_path = "../data/sub-daily/"
month_dic = {1: "January", 4: "April", 7: "July", 10: "October"}


def plot_profile_subdaily(loc):
    """
    For a given location loc (either "Germany" or "Sweden" or "Spain"),
    this function creates a plot of the mean wind speed in the lowermost 700m
    of the atmosphere for the IDL and GERICS model.

    The other models are not included because resolution is too coarse
    or geopotential height is not available
    """
    f, axs = plt.subplots(ncols=4, nrows=4, figsize=(10, 10), sharey=True)
    cbar_list = [f.add_axes([0.1 + 0.47 * i, 0.045, 0.37, 0.015]) for i in range(2)]
    plt.subplots_adjust(bottom=0.12, top=0.95, right=0.98, left=0.08)

    for j, ins in enumerate(["GERICS", "IDL"]):
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
            if (i == 0) & (j == 0):
                # Add colorbar

                ds_grass["S"].groupby("time.hour").mean().plot(
                    ax=axs[i, 0],
                    vmin=2,
                    vmax=14,
                    levels=13,
                    cbar_ax=cbar_list[0],
                    cbar_kwargs={
                        "label": "Mean wind speed [m/s]",
                        "orientation": "horizontal",
                    },
                )
                ds_diff["S"].groupby("time.hour").mean().plot(
                    ax=axs[i, 1],
                    cmap="RdBu_r",
                    vmin=-2.2,
                    vmax=2.2,
                    levels=12,
                    cbar_ax=cbar_list[1],
                    cbar_kwargs={
                        "label": "Wind speed change [m/s]",
                        "orientation": "horizontal",
                    },
                )
            else:
                ds_grass["S"].groupby("time.hour").mean().plot(
                    ax=axs[i, 0 + 2 * j], vmin=2, vmax=14, levels=13, add_colorbar=False
                )
                ds_diff["S"].groupby("time.hour").mean().plot(
                    ax=axs[i, 1 + 2 * j],
                    cmap="RdBu_r",
                    vmin=-2.2,
                    vmax=2.2,
                    levels=12,
                    add_colorbar=False,
                )
            if j == 0:
                axs[i, 0].text(
                    -0.35,
                    0.5,
                    month_dic[month],
                    verticalalignment="center",
                    transform=axs[i, 0].transAxes,
                    color="darkred",
                    fontsize=14,
                    rotation=90,
                )

        axs[0, 2 * j].text(
            1.1,
            1.2,
            ins,
            verticalalignment="center",
            horizontalalignment="center",
            transform=axs[0, 2 * j].transAxes,
            color="darkred",
            fontsize=14,
        )

        axs[0, 0 + 2 * j].set_title("GRASS")
        axs[0, 1 + 2 * j].set_title("GRASS - FOREST")

        for i_tick in range(4):
            for j_tick in range(2):
                ax = axs[i_tick, 2 * j + j_tick]
                ax.set_xticks(ds_forest["approximate height"])
                ax.set_yticks([0, 6, 12, 18])
                ax.set_xlim(xmin=0, xmax=700)

    # Delete non-needed x axis labels in the middle of the plot
    for i in range(3):
        for k in range(4):
            axs[i, k].set_xlabel("")
    # Delete non-needed y axis labels
    for l in range(1, 4):
        for k in range(4):
            axs[k, l].set_ylabel("")
    add_letters(axs, x=-0.1, y=1, fs=10)

    plt.savefig(
        "../plots/exploration/sub-daily/Profile_" + loc + "_paper.jpeg", dpi=300
    )


if __name__ == "__main__":
    for loc in ["Germany", "Sweden", "Spain"]:
        plot_profile_subdaily(loc)
