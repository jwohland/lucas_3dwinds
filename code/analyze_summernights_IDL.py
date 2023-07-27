from utils import *

data_dir = "../data/summernights_IDL/"
plot_dir = "../plots/summernights_IDL/"


ds_forest = xr.open_dataset(data_dir + "FOREST/S_IDL_summernights.nc")
ds_grass = xr.open_dataset(data_dir + "GRASS/S_IDL_summernights.nc")
ds_diff = ds_grass - ds_forest
ds_diff = ds_diff.sel(mlev=slice(6))
ds_diff = replace_vertical_coordinate(ds_diff, "IDL")

f, axs = plt.subplots(ncols=6, figsize=(20, 5), sharex=True, subplot_kw=SUBPLOT_KW)
plt.subplots_adjust(bottom=0.20)
cbar_ax = f.add_axes([0.2, 0.12, 0.6, 0.04])
cbar_kwargs = {
    "label": "July midnight wind speed change [m/s]",
    "orientation": "horizontal",
}
for i in range(6):
    ds_diff.isel({"approximate height": i})["S"].plot(
        ax=axs[i],
        cbar_ax=cbar_ax,
        cbar_kwargs=cbar_kwargs,
        vmin=-1.75,
        vmax=1.75,
        cmap=plt.get_cmap("RdBu_r"),
        levels=8,
        extend="both",
    )
    axs[i].set_ylabel("")
    axs[i].set_xlabel("")
    add_coast_boarders(axs[i])
add_letters(axs)
plt.subplots_adjust(left=0.05, right=0.95, top=0.95)
plt.savefig(plot_dir + "summernights_IDL.jpeg, dpi=300")
