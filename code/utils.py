import cartopy.crs as ccrs
import cartopy.feature as cf
import numpy as np
from params import approximate_heights, horizontal_ranges
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib as mpl


SUBPLOT_KW = {
    "subplot_kw": {"projection": ccrs.PlateCarree(), "extent": [-15, 50, 35, 70]}
}

FIG_PARAMS = {
    "dpi": 300,
    "facecolor": "w",
    "transparent": False,
}

TEXT_PARAMS = {
    "horizontalalignment": "left",
    "verticalalignment": "center",
}


def add_coast_boarders(ax):
    ax.add_feature(cf.COASTLINE)
    ax.add_feature(cf.BORDERS)


vertical_dim_dic = {
    "IDL": "mlev",
    "ETH": "pressure",
    "GERICS": "lev",
    "OUR": "plev",
    "BCCR": "plev",
}


def constrain_vertical_range(ds, institution):
    """
    Restrict 3D data to height levels that are of interest for this analysis.
        GERICS: 22 - 27
        IDL: 0-5
    And sort entries in decreasing order. Initially:
        from high to low: GERICS, BCCR, ETH
        from low to high: OUR, IDL
    BCCR needs no specific handling
    """
    if institution in ["GERICS", "IDL"]:
        ranges = {"GERICS": np.arange(22, 28), "IDL": np.arange(6)}
        dim_name = vertical_dim_dic[institution]
        ds = ds.sel({dim_name: ranges[institution]})
    if institution in ["OUR", "IDL"]:
        vertical_dim = vertical_dim_dic[institution]
        ds = ds.reindex(vertical_dim=list(reversed(ds[vertical_dim])))
    return ds


def get_focus_area(ds, area_name):
    assert area_name in ["Sweden", "Germany", "Spain"]
    if area_name == "Sweden":
        rlat = slice(7, 8)
        rlon = slice(-3, -2)
    elif area_name == "Germany":
        rlon = slice(-6.5, -5.5)
        rlat = slice(1, 2)
    elif area_name == "Spain":
        rlon = slice(-18, -17)
        rlat = slice(-8, -7)
    return ds.sel(rlon=rlon, rlat=rlat).mean(dim=["rlat", "rlon"])


def replace_vertical_coordinate(ds, ins):
    initial_name = vertical_dim_dic[ins]
    ds[initial_name] = [approximate_heights[ins][x] for x in ds[initial_name].values]
    ds = ds.rename({initial_name: "approximate height"})
    ds["approximate height"].attrs = {"unit": "m"}
    return ds


def compute_land_sea_mask(other=np.nan, save=True, plot=True, monthly=False):
    """
    Based on the land area fraction file provided by IDL, a land-sea mask is computed by iteratively
    excluding regions that are not relevant for this analysis.
    """
    ds_mask = xr.open_dataset(
        "../data/IDL/sflt_EUR-44_ECMWF-ERAINT_LUCAS_EVAL_r1i1p1_IDL_WRFV381D_v1_fx.nc"
    )
    ds_mask = ds_mask["sflt"]
    ds_mask = ds_mask.where(ds_mask > 50, other).where(
        ds_mask < 50, 1
    )  # change to binary mask: 1 is land, other is not land
    ds_mask = ds_mask.where(ds_mask.rlat > -17, other)  # exclude northern Africa
    ds_mask = ds_mask.where(
        ((ds_mask.rlat > -12) | (ds_mask.rlon > -5)), other
    )  # exclude northern Africa
    ds_mask = ds_mask.where(
        ((ds_mask.rlat < 13) | (ds_mask.rlon > -5)), other
    )  # exclude Iceland
    ds_mask = ds_mask.where((ds_mask.rlon < 10), other)  # exclude Eastern end
    # Monthly mask must be cropped in line with monthly data
    filename = "land_sea_mask"
    if monthly:
        ds_mask = ds_mask.sel(
            {"rlat": horizontal_ranges["rlats"], "rlon": horizontal_ranges["rlons"]}
        )
        ds_mask = ds_mask.sel(rlon=slice(-30, 17.6))
        filename += "_monthly"
    if save:
        ds_mask.to_netcdf("../output/" + filename + ".nc")
    if plot:
        ds_mask.plot(add_colorbar=False, cmap=mpl.colormaps["Oranges"])
        plt.xlim(xmin=-23, xmax=11)
        plt.ylim(ymin=-15, ymax=22)
        plt.title("Land mask used for signal decay over Europe")
        plt.savefig("../plots/land_sea_mask.jpeg", dpi=300)
    return ds_mask


def restrict_to_land(ds, monthly=True, variable_name="S"):
    """
    Exclude data over oceans and restrict to domain of interest

    This function is only demonstrated to work for IDL and GERICS data because of the different grid sizes!
    """
    filename = "land_sea_mask"
    if monthly:
        filename += "_monthly"
    try:
        land_sea_mask = xr.open_dataarray("../output/" + filename + ".nc")
    except:
        land_sea_mask = compute_land_sea_mask(plot=False, monthly=True)

    # GERICS simulations have larger outputs and need to be cropped
    if ds.rlat.size > 104:
        ds = ds.isel(rlon=slice(8, -15), rlat=slice(8, -10))

    # Grids are typically off by a small margin. Use coordinates of the provided dataset
    # also for the land sea if the deviation is less than 5% of the grid spacing
    if np.abs((land_sea_mask.rlat.values - ds.rlat.values).mean()) < 0.05 * 0.44:
        land_sea_mask["rlat"] = ds.rlat
        land_sea_mask["rlon"] = ds.rlon
        ds_masked = (land_sea_mask * ds[variable_name]).to_dataset(name=variable_name)
        return ds_masked
    else:
        print("Grids of land sea mask and wind data do not match")
