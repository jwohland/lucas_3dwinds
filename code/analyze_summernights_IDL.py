import xarray as xr
from utils import *
import matplotlib.pyplot as plt

data_dir = "../data/summernights_IDL/"
plot_dir = "../plots/summernights_IDL/"


ds_forest = xr.open_dataset(data_dir + "FOREST/S_IDL_summernights.nc")
ds_grass = xr.open_dataset(data_dir + "GRASS/S_IDL_summernights.nc")
ds_diff = ds_grass - ds_forest
ds_diff = ds_diff.sel(mlev=slice(6))
ds_diff = replace_vertical_coordinate(ds_diff, "IDL")

f, axs = plt.subplots(ncols=6, figsize=(20, 5), sharex=True)
plt.subplots_adjust(bottom=0.23)
cbar_ax = f.add_axes([0.2, 0.12, 0.6, 0.04])
cbar_kwargs = {
    "label": "GRASS - FOREST wind speed change [m/s]",
    "orientation": "horizontal",
}
for i in range(6):
    ds_diff.isel({"approximate height": i})["S"].plot(
        ax=axs[i],
        cbar_ax=cbar_ax,
        cbar_kwargs=cbar_kwargs,
        vmin=-2,
        vmax=2,
        cmap=plt.get_cmap("RdBu_r"),
    )
    axs[i].set_ylabel("")
    axs[i].set_xlabel("")
    plt.savefig(plot_dir + "summernights_IDL.jpeg, dpi=300")
